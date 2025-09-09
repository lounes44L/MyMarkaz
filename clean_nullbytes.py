import os
import sys

def clean_file(file_path):
    """Remove null bytes from a file and save it back"""
    print(f"Checking file: {file_path}")
    
    try:
        # Read file in binary mode
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Check if file contains null bytes
        if b'\x00' in content:
            print(f"Found null bytes in {file_path}")
            
            # Create backup
            backup_path = f"{file_path}.bak"
            with open(backup_path, 'wb') as f:
                f.write(content)
            
            # Remove null bytes
            cleaned_content = content.replace(b'\x00', b'')
            
            # Write cleaned content back
            with open(file_path, 'wb') as f:
                f.write(cleaned_content)
            
            print(f"Cleaned {file_path} (backup created at {backup_path})")
            return True
        else:
            print(f"No null bytes in {file_path}")
            return False
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    # Get the base directory (current directory)
    base_dir = os.path.abspath('.')
    print(f"Scanning directory: {base_dir}")
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip __pycache__ directories
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files")
    
    # Clean all files
    cleaned_count = 0
    for file_path in python_files:
        if clean_file(file_path):
            cleaned_count += 1
    
    print(f"\nSummary:")
    print(f"- Total Python files: {len(python_files)}")
    print(f"- Files with null bytes cleaned: {cleaned_count}")

if __name__ == "__main__":
    main()
