# Download Tool

类似迅雷的多线程下载器，适合Mac/Linux命令行，依赖基础的python环境，适合企业内部轻量化部署，加快公网资源下载速度
This is a file download tool that supports multi-threaded concurrent downloads, with download history recording and QR code generation capabilities.
This tool likes Xunlei download in windows, smart for Mac/Liunx system etc.

## Configuration File Description

All configuration items are in the `config.py` file and can be modified as needed:

### Configuration Items Description

- `FILE_SHARE_URL`: Base download URL, used for generating download links and QR codes
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
# Modify file share base URL
FILE_SHARE_URL = "https://your-domain.com/downloads/"

# Increase concurrent threads to 10
DOWNLOAD_WORKERS = 10

# Modify file storage directory
DESTINATION_DIR = "/var/www/downloads"
```

## Usage

```bash
# Download file
python download.py <URL> [new filename]

# Examples
python download.py https://example.com/file.zip
python download.py https://example.com/file.zip myfile
```

## Features

- Multi-threaded concurrent downloads
- Download progress display
- Download history recording
- Automatic download link generation
- Automatic QR code generation
- File deduplication (avoid duplicate downloads)

## Installation

### Python Environment Setup

#### Windows

1. **Download Python:**
   - Visit [python.org](https://www.python.org/downloads/)
   - Download Python 3.12 (recommended)
   - Run the installer and check "Add Python to PATH"

2. **Verify Installation:**
   ```cmd
   python --version
   pip --version
   ```

#### macOS

1. **Using Homebrew (Recommended):**
   ```bash
   # Install Homebrew if not installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Python
   brew install python
   ```

2. **Using Official Installer:**
   - Download from [python.org](https://www.python.org/downloads/)
   - Run the installer package

3. **Verify Installation:**
   ```bash
   python3 --version
   pip3 --version
   ```

#### Linux (Ubuntu)

1. **Install Python:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Verify Installation:**
   ```bash
   python3 --version
   pip3 --version
   ```

#### Linux (RedHat/CentOS)

1. **Install Python:**
   ```bash
   sudo yum install python3 python3-pip
   # or for newer versions
   sudo dnf install python3 python3-pip
   ```

2. **Verify Installation:**
   ```bash
   python3 --version
   pip3 --version
   ```

### Installing Dependencies

1. **Navigate to the project directory:**
   ```bash
   cd fastDown
   ```

2. **Install required packages:**
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Or using pip3 (if you have both Python 2 and 3)
   pip3 install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python -c "import requests, qrcode; print('Dependencies installed successfully!')"
   ``` 
