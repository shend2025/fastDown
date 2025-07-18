# Download Proxy Tool

This is a file download tool that supports multi-threaded concurrent downloads, with download history recording and QR code generation capabilities.

## Configuration File Description

All configuration items are in the `config.py` file and can be modified as needed:

### Configuration Items Description

- `DOWNLOAD_BASE_URL`: Base download URL, used for generating download links and QR codes
- `DOWNLOAD_WORKERS`: Number of concurrent download threads (default 5 threads)
- `DESTINATION_DIR`: File storage directory
- `TEMP_DIR`: Temporary file directory
- `HISTORY_FILE`: History record filename

### Modifying Configuration

1. Edit the `config.py` file
2. Modify the corresponding configuration items
3. Save the file and restart the program

### Example Configuration

```python
# Modify download base URL
DOWNLOAD_BASE_URL = "https://your-domain.com/downloads/"

# Increase concurrent threads to 10
DOWNLOAD_WORKERS = 10

# Modify file storage directory
DESTINATION_DIR = "/var/www/downloads"
```

## Usage

```bash
# Download file
python muti_down.py <URL> [new filename]

# Examples
python muti_down.py https://example.com/file.zip
python muti_down.py https://example.com/file.zip myfile
```

## Features

- Multi-threaded concurrent downloads
- Download progress display
- Download history recording
- Automatic download link generation
- Automatic QR code generation
- File deduplication (avoid duplicate downloads) 
