"""
RabbitMQ client for publishing messages.
"""

import json
import logging
import time
from typing import Dict, Optional
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError


class RabbitMQClient:
    """Handles RabbitMQ connection and message publishing with health monitoring."""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 5672,
        username: str = 'guest',
        password: str = 'guest',
        queue_name: str = 'file_scan_queue',
        exchange_name: str = '',
        max_retries: int = 10,
        heartbeat_check_interval: int = 100  # Check connection every N messages
    ):
        """
        Initialize RabbitMQ client.
        
        Args:
            host: RabbitMQ server hostname
            port: RabbitMQ server port
            username: RabbitMQ username
            password: RabbitMQ password
            queue_name: Name of the queue to publish to
            exchange_name: Exchange name (empty for default exchange)
            max_retries: Maximum connection retry attempts
            heartbeat_check_interval: Check connection health every N messages
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.max_retries = max_retries
        self.heartbeat_check_interval = heartbeat_check_interval
        
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.logger = logging.getLogger(__name__)
        
        self._message_count = 0
    
    def connect(self) -> bool:
        """
        Establish connection to RabbitMQ with retry logic.
        
        Returns:
            True if connection successful, False otherwise
        """
        for attempt in range(0, self.max_retries):
            try:
                self.logger.info(
                    f"Connecting to RabbitMQ at {self.host}:{self.port} "
                    f"(attempt {attempt}/{self.max_retries})"
                )
                
                credentials = pika.PlainCredentials(self.username, self.password)
                parameters = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    credentials=credentials,
                    connection_attempts=3,
                    retry_delay=2,
                    heartbeat=600,  # 10 minutes - prevents timeout on long operations
                    blocked_connection_timeout=300,
                    socket_timeout=10
                )
                
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                # Declare queue (idempotent)
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                
                # Enable publisher confirms for reliability
                self.channel.confirm_delivery()
                
                self.logger.info("Successfully connected to RabbitMQ")
                return True
                
            except AMQPConnectionError as e:
                self.logger.error(f"Connection attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    self.logger.error("Max retries reached. Connection failed.")
                    return False
        
        return False
    
    def disconnect(self):
        """Safely close RabbitMQ connection."""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                self.logger.info("RabbitMQ connection closed")
        except Exception as e:
            self.logger.error(f"Error closing connection: {e}")
    
    def publish(self, message: Dict) -> bool:
        """
        Publish a message to the RabbitMQ queue with confirmation.
        Includes periodic connection health checks for long-running operations.
        
        Args:
            message: Dictionary containing message data
            
        Returns:
            True if published successfully, False otherwise
        """
        if not self.channel:
            self.logger.error("Cannot publish: not connected to RabbitMQ")
            return False
        
        # Periodic connection health check
        self._message_count += 1
        if self._message_count % self.heartbeat_check_interval == 0:
            self._ensure_connection_alive()
        
        file_path = message.get('file_path', 'unknown')

        
        try:
            message_body = json.dumps(message, indent=2)
            
            # Use confirm_delivery for guaranteed delivery
            try:
                self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=self.queue_name,
                    body=message_body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Persistent message
                        content_type='application/json'
                    ),
                    mandatory=True
                )
                return True
                
            except pika.exceptions.UnroutableError:
                self.logger.error("Message was returned as unroutable")
                return False
            
        except (AMQPConnectionError, AMQPChannelError) as e:
            self.logger.error(f"Failed to publish message for file {file_path}: {e}")
            
            # Attempt to reconnect
            self.logger.info("Attempting to reconnect...")
            if self.connect():
                # Retry once after reconnection
                try:
                    message_body = json.dumps(message, indent=2)
                    self.channel.basic_publish(
                        exchange=self.exchange_name,
                        routing_key=self.queue_name,
                        body=message_body,
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            content_type='application/json'
                        ),
                        mandatory=True
                    )
                    return True
                except Exception as retry_error:
                    self.logger.error(f"Retry failed: {retry_error}")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Unexpected error publishing message: {e}")
            return False
    
    def _ensure_connection_alive(self):
        """
        Verify connection is still alive, reconnect if needed.
        Important for long-running scans.
        """
        try:
            if self.connection and not self.connection.is_closed:
                # Process any pending events to keep connection alive
                self.connection.process_data_events(time_limit=0)
            else:
                self.logger.warning("Connection lost, attempting to reconnect...")
                self.connect()
        except Exception as e:
            self.logger.warning(f"Connection check failed: {e}, reconnecting...")
            self.connect()
    
    def is_connected(self) -> bool:
        """Check if connected to RabbitMQ."""
        return (
            self.connection is not None and
            not self.connection.is_closed and
            self.channel is not None
        )