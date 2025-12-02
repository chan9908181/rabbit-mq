#!/usr/bin/env python3
"""
Create test directory structure with random files.
Simple script to generate test data for the file scanner.
"""

import os
from pathlib import Path
import random
import string


def random_content(size=100):
    """Generate random text content."""
    return ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=size))


def create_test_structure():
    """Create test directory with files."""
    
    # Create test_files directory in current location
    base_dir = Path("test_files2")
    base_dir.mkdir(exist_ok=True)
    
    print(f"Creating test structure in: {base_dir.absolute()}")
    
    total_files = 0
    
    # Create directory structure
    directories = [
        "documents",
        "images",
        "videos",
        "downloads",
        "documents/work",
        "documents/personal",
        "images/vacation",
        "images/family"
    ]
    
    for dir_name in directories:
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # File types and their extensions
    file_types = {
        "documents": [".txt", ".pdf", ".docx", ".xlsx"],
        "documents/work": [".txt", ".pdf", ".docx"],
        "documents/personal": [".txt", ".pdf"],
        "images": [".jpg", ".png", ".gif"],
        "images/vacation": [".jpg", ".png"],
        "images/family": [".jpg"],
        "videos": [".mp4", ".avi", ".mkv"],
        "downloads": [".zip", ".exe", ".tar.gz"]
    }
    
    # Create files in each directory
    for dir_name, extensions in file_types.items():
        dir_path = base_dir / dir_name
        
        # Create 10-20 files per directory
        num_files = 100000
        
        for i in range(num_files):
            ext = random.choice(extensions)
            file_name = f"file_{i:03d}{ext}"
            file_path = dir_path / file_name
            
            # Write random content
            content_size = random.randint(50, 500)
            file_path.write_text(random_content(content_size))
            
            total_files += 1
    
    # Create some files in root
    for i in range(5):
        file_path = base_dir / f"readme_{i}.txt"
        file_path.write_text(random_content(200))
        total_files += 1
    
    print(f"\n✅ Created {total_files} test files in '{base_dir}'")
    print(f"\nYou can now run:")
    print(f"  python file_scanner.py {base_dir}")


if __name__ == '__main__':
    print("=" * 60)
    print("TEST FILE GENERATOR")
    print("=" * 60)
    print("\nThis will create a 'test_files' directory with:")
    print("  - Multiple subdirectories")
    print("  - ~100-150 random files")
    print("  - Various file extensions (.txt, .pdf, .jpg, etc.)")
    
    response = input("\nContinue? (y/n): ")
    if response.lower() == 'y':
        create_test_structure()
    else:
        print("Cancelled.")