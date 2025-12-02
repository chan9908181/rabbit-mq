#!/usr/bin/env python3
"""
Simple utility script to read and display messages from RabbitMQ queue.
Useful for verifying that the file scanner is working correctly.
"""

import pika
import json
import sys
import argparse


def read_messages(
    host='localhost',
    port=5672,
    user='guest',
    password='guest',
    queue='file_scan_queue',
    count=10,
    acknowledge=False
):
    """
    Read messages from RabbitMQ queue.
    
    Args:
        host: RabbitMQ hostname
        port: RabbitMQ port
        user: RabbitMQ username
        password: RabbitMQ password
        queue: Queue name to read from
        count: Number of messages to read
        acknowledge: Whether to acknowledge (remove) messages after reading
    """
    try:
        # Establish connection
        credentials = pika.PlainCredentials(user, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Declare queue (ensure it exists)
        channel.queue_declare(queue=queue, durable=True)
        
        print(f"Connected to RabbitMQ at {host}:{port}")
        print(f"Reading up to {count} messages from queue: {queue}")
        print("=" * 80)
        
        messages_read = 0
        
        for i in range(count):
            method_frame, header_frame, body = channel.basic_get(queue)
            
            if method_frame:
                messages_read += 1
                print(f"\nMessage {messages_read}:")
                print("-" * 80)
                
                try:
                    message = json.loads(body)
                    print(json.dumps(message, indent=2))
                except json.JSONDecodeError:
                    print("Raw message (not JSON):")
                    print(body.decode('utf-8'))
                
                # Acknowledge message if requested
                if acknowledge:
                    channel.basic_ack(method_frame.delivery_tag)
                    print("\n[Message acknowledged and removed from queue]")
            else:
                print(f"\nNo more messages in queue (read {messages_read} total)")
                break
        
        print("\n" + "=" * 80)
        print(f"Total messages read: {messages_read}")
        
        if not acknowledge and messages_read > 0:
            print("\nNote: Messages were not removed from queue (use --acknowledge flag to remove)")
        
        connection.close()
        
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Could not connect to RabbitMQ at {host}:{port}")
        print(f"Details: {e}")
        print("\nMake sure RabbitMQ is running:")
        print("  docker-compose up -d")
        sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Read messages from RabbitMQ queue'
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='RabbitMQ host (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5672,
        help='RabbitMQ port (default: 5672)'
    )
    
    parser.add_argument(
        '--user',
        default='guest',
        help='RabbitMQ username (default: guest)'
    )
    
    parser.add_argument(
        '--password',
        default='guest',
        help='RabbitMQ password (default: guest)'
    )
    
    parser.add_argument(
        '--queue',
        default='file_scan_queue',
        help='Queue name (default: file_scan_queue)'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=10,
        help='Number of messages to read (default: 10)'
    )
    
    parser.add_argument(
        '--acknowledge',
        action='store_true',
        help='Acknowledge (remove) messages after reading'
    )
    
    args = parser.parse_args()
    
    read_messages(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        queue=args.queue,
        count=args.count,
        acknowledge=args.acknowledge
    )


if __name__ == '__main__':
    main()