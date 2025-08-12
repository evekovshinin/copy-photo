# Photo Copy Utility
A robust Python script for securely copying photos from a camera's memory card to your computer with verification.

## Key Features
* Smart Mount Detection: Automatically finds your camera's storage across different Linux mount points -->
* Date-Based Organization: Creates destination folders using the earliest photo's date
* Progress Tracking: Real-time copy progress with visual progress bar
* Copy Verification: Validates successful transfer by comparing file counts and sizes
* Customizable Config: JSON configuration for mount points, file extensions, and folder structure
* Error Handling: Comprehensive error reporting and recovery

## Usage
bash
```python3 photo_copy.py "project_name" [--label EOS_DIGITAL] [--user $(whoami)] [--no-verify]```

## Configuration
Edit ~/.config/photo_copy/config.json to customize:

* Mount point patterns
* Supported photo extensions
* Destination folder naming template
* Subfolder structure

## Requirements
* Python 3.x
* tqdm package (```pip install tqdm```)

Perfect for photographers who need reliable, verified transfers of their camera photos with automatic organization.

New line
