#!/usr/bin/env python3
"""
File System Scanner with RabbitMQ Integration

This program recursively scans a directory and sends file information
to a RabbitMQ queue for each discovered file.
"""

import sys
import logging
import argparse
from pathlib import Path
from typing import Optional, List, Dict

from src.file_info_extractor import FileInfoExtractor
from src.rabbitmq_client import RabbitMQClient
from src.directory_scanner import DirectoryScanner
from src.logger_config import setup_logging


class FileScannerApp:
    """Main application orchestrator."""
    
    def __init__(
        self,
        rabbitmq_client: RabbitMQClient,
        file_extractor: FileInfoExtractor,
        scanner: DirectoryScanner
    ):
        self.rabbitmq = rabbitmq_client
        self.extractor = file_extractor
        self.scanner = scanner
        self.logger = logging.getLogger(__name__)
    
    def run(
        self,
        root_path: str,
        file_extensions: Optional[List[str]] = None
    ):
        """
        Run the file scanning process.
        
        Args:
            root_path: Root directory to scan
            file_extensions: Optional list of file extensions to filter
        """
        # Connect to RabbitMQ
        if not self.rabbitmq.connect():
            self.logger.error("Failed to connect to RabbitMQ")
            sys.exit(1)
        
        try:
            # Scan directory and process files
            self.scanner.scan(
                root_path=root_path,
                file_extensions=file_extensions,
                file_callback=self._process_file
            )
            
            # Print summary
            stats = self.scanner.get_statistics()
            self.logger.info(
                f"Scan completed. Processed: {stats['processed']}, "
                f"Failed: {stats['failed']}, Skipped: {stats['skipped']}"
            )
            
        except KeyboardInterrupt:
            self.logger.info("Scan interrupted by user")
        finally:
            self.rabbitmq.disconnect()
    
    def _process_file(self, file_path: Path) -> bool:
        """
        Process a single file: extract info and publish to RabbitMQ.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        # Extract file information
        file_info = self.extractor.extract(file_path)
        if not file_info:
            return False
        
        # Publish to RabbitMQ
        success = self.rabbitmq.publish(file_info)
        
        if success:
            self.logger.debug(f"Published: {file_path.name}")
        
        return success


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Recursively scan directory and publish file info to RabbitMQ'
    )
    
    parser.add_argument(
        '--input-dirs',
        nargs='+',
        required=True,
        help='Directory paths to scan (can specify multiple: --input-dirs dir1 dir2 dir3)'
    )
    
    parser.add_argument(
        '--rabbitmq-host',
        default='localhost',
        help='RabbitMQ host (default: localhost)'
    )
    
    parser.add_argument(
        '--rabbitmq-port',
        type=int,
        default=5672,
        help='RabbitMQ port (default: 5672)'
    )
    
    parser.add_argument(
        '--rabbitmq-user',
        default='guest',
        help='RabbitMQ username (default: guest)'
    )
    
    parser.add_argument(
        '--rabbitmq-password',
        default='guest',
        help='RabbitMQ password (default: guest)'
    )
    
    parser.add_argument(
        '--queue-name',
        default='file_scan_queue',
        help='RabbitMQ queue name (default: file_scan_queue)'
    )
    
    parser.add_argument(
        '--calculate-hash',
        action='store_true',
        help='Calculate SHA256 hash for files < 100MB'
    )
    
    parser.add_argument(
        '--extensions',
        nargs='+',
        help='Filter by file extensions (e.g., .txt .pdf .jpg)'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Initialize components
    rabbitmq_client = RabbitMQClient(
        host=args.rabbitmq_host,
        port=args.rabbitmq_port,
        username=args.rabbitmq_user,
        password=args.rabbitmq_password,
        queue_name=args.queue_name
    )
    
    file_extractor = FileInfoExtractor(
        calculate_hash=args.calculate_hash
    )
    
    scanner = DirectoryScanner()
    
    # Create and run application
    app = FileScannerApp(
        rabbitmq_client=rabbitmq_client,
        file_extractor=file_extractor,
        scanner=scanner
    )
    
    # Scan each directory
    for directory in args.input_dirs:
        logging.info(f"Starting scan of: {directory}")
        app.run(
            root_path=directory,
            file_extensions=args.extensions
        )


if __name__ == '__main__':
    main()