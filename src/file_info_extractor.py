"""
File information extraction module.
"""

import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class FileInfoExtractor:
    """Extracts metadata from files."""
    
    def __init__(self, calculate_hash: bool = False, max_hash_size: int = 100 * 1024 * 1024):
        """
        Initialize the file info extractor.
        
        Args:
            calculate_hash: Whether to calculate SHA256 hash
            max_hash_size: Maximum file size (bytes) for hash calculation
        """
        self.calculate_hash = calculate_hash
        self.max_hash_size = max_hash_size
        self.logger = logging.getLogger(__name__)
    
    def extract(self, file_path: Path) -> Optional[Dict]:
        """
        Extract metadata from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file metadata or None if error occurs
        """
        try:
            stat_info = file_path.stat()
            
            file_info = {
                'file_path': str(file_path.absolute()),
                'file_name': file_path.name,
                'file_extension': file_path.suffix,
                'file_size_bytes': stat_info.st_size,
                'file_size_human': self._format_size(stat_info.st_size),
                'created_time': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'accessed_time': datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                'is_symlink': file_path.is_symlink(),
                'scan_timestamp': datetime.now().isoformat()
            }
            
            # Add hash if requested and file is small enough
            if self.calculate_hash and stat_info.st_size <= self.max_hash_size:
                file_info['sha256_hash'] = self._compute_hash(file_path)
            
            return file_info
            
        except (PermissionError, OSError) as e:
            self.logger.warning(f"Could not access file {file_path}: {e}")
            return None
    
    def _compute_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                # Read in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(chunk)
            
            return sha256_hash.hexdigest()
            
        except Exception as e:
            self.logger.warning(f"Could not calculate hash for {file_path}: {e}")
            return "error_calculating_hash"
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Convert bytes to human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted string (e.g., "1.50 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.2f} PB"