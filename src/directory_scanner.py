"""
Directory scanning module.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Callable


class DirectoryScanner:
    """Recursively scans directories and processes files."""
    
    def __init__(self, progress_interval: int = 100):
        """
        Initialize the directory scanner.
        
        Args:
            progress_interval: Log progress every N files
        """
        self.progress_interval = progress_interval
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self._files_processed = 0
        self._files_failed = 0
        self._files_skipped = 0
    
    def scan(
        self,
        root_path: str,
        file_callback: Callable[[Path], bool],
        file_extensions: Optional[List[str]] = None
    ):
        """
        Recursively scan directory and process files.
        Uses os.walk() for efficient, memory-safe directory traversal.
        
        Args:
            root_path: Root directory to start scanning
            file_callback: Function to call for each file (receives Path, returns bool)
            file_extensions: Optional list of file extensions to filter by (e.g. ['.txt', '.log'])
        """
        root = Path(root_path)
        
        # Validate path
        if not root.exists():
            self.logger.error(f"Path does not exist: {root_path}")
            raise FileNotFoundError(f"Path does not exist: {root_path}")
        
        if not root.is_dir():
            self.logger.error(f"Path is not a directory: {root_path}")
            raise NotADirectoryError(f"Path is not a directory: {root_path}")
        
        # Reset statistics
        self._files_processed = 0
        self._files_failed = 0
        self._files_skipped = 0
        
        # Log scan start
        self.logger.info(f"Starting scan of directory: {root_path}")
        if file_extensions:
            self.logger.info(f"Filtering by extensions: {file_extensions}")
        
        # Scan directory using os.walk (memory-efficient, battle-tested)
        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                # Process each file in current directory
                for filename in filenames:
                    file_path = Path(dirpath) / filename
                    self._process_entry(file_path, file_callback, file_extensions)
                
                # Remove directories we can't access from the walk
                dirnames[:] = [d for d in dirnames if self._can_access_dir(Path(dirpath) / d)]
                
        except Exception as e:
            self.logger.error(f"Error during directory scan: {e}")
            raise Exception(f"Error during directory scan: {e}")
    
    def _can_access_dir(self, dir_path: Path) -> bool:
        """
        Check if directory is accessible.
        
        Args:
            dir_path: Directory path to check
            
        Returns:
            True if accessible, False otherwise
        """
        try:
            # Try to list directory
            next(dir_path.iterdir(), None)
            return True
        except (PermissionError, OSError) as e:
            self.logger.warning(f"Cannot access directory {dir_path}: {e}")
            return False
    
    def _process_entry(
        self,
        entry: Path,
        file_callback: Callable[[Path], bool],
        file_extensions: Optional[List[str]]
    ):
        """
        Process a single file entry.
        
        Args:
            entry: Path to process
            file_callback: Function to call for files
            file_extensions: Optional file extension filter
        """
        try:
            # Filter by extension if specified
            if file_extensions:
                # Normalize extension (add dot if missing)
                normalized_extensions = [
                    ext if ext.startswith('.') else f'.{ext}' 
                    for ext in file_extensions
                ]
                
                if entry.suffix.lower() not in normalized_extensions:
                    self._files_skipped += 1
                    self.logger.debug(f"Skipped (extension filter): {entry}")
                    return
            
            # Process file
            success = file_callback(entry)
            
            if success:
                self._files_processed += 1
            else:
                self._files_failed += 1
            
            # Log progress
            if self._files_processed % self.progress_interval == 0:
                self.logger.info(
                    f"Progress: {self._files_processed} processed, "
                    f"{self._files_failed} failed, "
                    f"{self._files_skipped} skipped"
                )
        
        except PermissionError:
            self.logger.warning(f"Permission denied: {entry}")
            self._files_skipped += 1
        except Exception as e:
            self.logger.error(f"Error processing {entry}: {e}")
            self._files_failed += 1
    
    def get_statistics(self) -> dict:
        """
        Get scanning statistics.
        
        Returns:
            Dictionary with processed, failed, and skipped counts
        """
        return {
            'processed': self._files_processed,
            'failed': self._files_failed,
            'skipped': self._files_skipped
        }