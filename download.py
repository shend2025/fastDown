import os
import requests
from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm
import sys
import urllib.parse
import shutil
import csv
import datetime
import qrcode
from config import (
    DOWNLOAD_BASE_URL, 
    DOWNLOAD_WORKERS, 
    DESTINATION_DIR, 
    TEMP_DIR, 
    HISTORY_FILE
)

def download_chunk(url, start, end, filename, progress_bar, temp_dir="temp"):
    headers = {'Range': f'bytes={start}-{end}'}
    response = requests.get(url, headers=headers, stream=True)
    temp_file_path = os.path.join(temp_dir, f"{filename}.part{start}")
    with open(temp_file_path, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
            progress_bar.update(len(chunk))

def merge_files(filename, parts, temp_dir="temp"):
    final_path = os.path.join(temp_dir, filename)
    with open(final_path, 'wb') as f:
        for part in sorted(parts):
            part_path = os.path.join(temp_dir, f"{filename}.part{part}")
            with open(part_path, 'rb') as p:
                f.write(p.read())
            os.remove(part_path)
    return final_path

def download_file(url, filename, workers=DOWNLOAD_WORKERS, temp_dir=TEMP_DIR):
    # Ensure temp directory exists
    os.makedirs(temp_dir, exist_ok=True)
    
    response = requests.head(url)
    size = int(response.headers.get('content-length', 0))
    
    # If unable to get file size, use single-threaded download
    if size == 0:
        print(f"Unable to get file size, using single-threaded download: {filename}")
        response = requests.get(url, stream=True)
        
        # Try to get file size from response headers
        if 'content-length' in response.headers:
            size = int(response.headers['content-length'])
            progress_bar = tqdm(total=size, unit='B', unit_scale=True, desc=filename)
        else:
            progress_bar = tqdm(unit='B', unit_scale=True, desc=filename)
        
        temp_file_path = os.path.join(temp_dir, filename)
        with open(temp_file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
                progress_bar.update(len(chunk))
        
        progress_bar.close()
        print(f"Download completed: {temp_file_path}")
        return temp_file_path
    
    chunk_size = size // workers
    
    parts = range(0, size, chunk_size)
    
    # Create progress bar
    progress_bar = tqdm(total=size, unit='B', unit_scale=True, desc=filename)
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for i, start in enumerate(parts):
            end = start + chunk_size -1 if i != workers-1 else size-1
            futures.append(executor.submit(
                download_chunk, url, start, end, filename, progress_bar, temp_dir
            ))
        
        # Wait for all downloads to complete
        for future in futures:
            future.result()
    
    progress_bar.close()
    final_path = merge_files(filename, parts, temp_dir)
    print(f"Download completed: {final_path}")
    return final_path

def move_to_destination(temp_file_path, destination_dir=DESTINATION_DIR):
    """Move downloaded file to specified directory"""
    # Ensure destination directory exists
    os.makedirs(destination_dir, exist_ok=True)
    
    # Get filename
    filename = os.path.basename(temp_file_path)
    
    # Build destination file path
    destination_path = os.path.join(destination_dir, filename)
    
    # If destination file already exists, add numeric suffix
    counter = 1
    original_destination = destination_path
    while os.path.exists(destination_path):
        name, ext = os.path.splitext(original_destination)
        destination_path = f"{name}_{counter}{ext}"
        counter += 1
    
    try:
        # Move file
        shutil.move(temp_file_path, destination_path)
        print(f"File moved to: {destination_path}")
        return destination_path
    except Exception as e:
        print(f"Failed to move file: {e}")
        return temp_file_path

def get_file_extension(url):
    """Extract file extension from URL"""
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path
    # Get filename part
    filename = os.path.basename(path)
    # Get extension
    _, ext = os.path.splitext(filename)
    return ext

def get_original_filename(url):
    """Extract original filename from URL"""
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path
    filename = os.path.basename(path)
    
    # If no filename in URL, return default name
    if not filename or filename == '':
        return 'downloaded_file'
    
    return filename

def load_download_history(history_file=HISTORY_FILE):
    """Load download history records"""
    history = {}
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    history[row['url']] = {
                        'filename': row['filename'],
                        'download_time': row['download_time'],
                        'file_path': row['file_path'],
                        'download_url': row.get('download_url', ''),  # Compatible with old version
                        'qrcode_path': row.get('qrcode_path', '')    # Compatible with old version
                    }
        except Exception as e:
            print(f"Failed to read history records: {e}")
    return history

def save_download_history(url, filename, file_path, download_url="", qrcode_path="", history_file=HISTORY_FILE):
    """Save download history records"""
    history = load_download_history(history_file)
    
    # Add new download record
    history[url] = {
        'filename': filename,
        'download_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'file_path': file_path,
        'download_url': download_url,
        'qrcode_path': qrcode_path
    }
    
    # Save to CSV file
    try:
        with open(history_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['url', 'filename', 'download_time', 'file_path', 'download_url', 'qrcode_path']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for url_key, data in history.items():
                writer.writerow({
                    'url': url_key,
                    'filename': data['filename'],
                    'download_time': data['download_time'],
                    'file_path': data['file_path'],
                    'download_url': data.get('download_url', ''),
                    'qrcode_path': data.get('qrcode_path', '')
                })
    except Exception as e:
        print(f"Failed to save history records: {e}")

def check_existing_download(url, history_file=HISTORY_FILE):
    """Check if URL has been downloaded before"""
    history = load_download_history(history_file)
    if url in history:
        file_path = history[url]['file_path']
        download_url = history[url].get('download_url', '')
        qrcode_path = history[url].get('qrcode_path', '')
        
        # Check if file still exists
        if os.path.exists(file_path):
            return file_path, download_url, qrcode_path
        else:
            # File doesn't exist, remove from history records
            del history[url]
            save_download_history(url, "", "", "", "", history_file)
    return None, "", ""

def main():
    """Main function, handle command line arguments and execute download"""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python down.py <URL> [new_filename]")
        print("Example: python down.py https://example.com/file.zip")
        print("Example: python down.py https://example.com/file.zip myfile")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Check if already downloaded
    existing_file, existing_download_url, existing_qrcode_path = check_existing_download(url)

    if existing_file:
        print(f"File already exists: {existing_file}")
        print(f"Skip download, return file path directly")
        
        if existing_download_url:
            print(f"Download link: {existing_download_url}")
        else:
            # Compatible with old version, regenerate download link
            filename = os.path.basename(existing_file)
            existing_download_url = DOWNLOAD_BASE_URL + filename
            print(f"Download link: {existing_download_url}")
        
        if existing_qrcode_path:
            print(f"QR code path: {existing_qrcode_path}")
        else:
            print("QR code file doesn't exist or path not saved")
        
        return existing_download_url
    
    # If no new filename provided, use original filename
    if len(sys.argv) == 2:
        new_filename = get_original_filename(url)
    else:
        new_filename = sys.argv[2]
        # Get original file extension
        original_ext = get_file_extension(url)
        
        # If new filename has no extension, add original extension
        if not os.path.splitext(new_filename)[1]:
            new_filename += original_ext
    
    print(f"Start downloading: {url}")
    print(f"Save as: {new_filename}")
    
    try:
        # Download to temp directory
        temp_file_path = download_file(url, new_filename, temp_dir=TEMP_DIR)
        
        # Move file to specified directory
        final_path = move_to_destination(temp_file_path)
        print(f"Download completed: {final_path}")

        download_url = DOWNLOAD_BASE_URL + new_filename
        print("Download link: "+ download_url)
        
     
        qrcode_img = qrcode.make(download_url)
        qrcode_img.save(new_filename+"qrcode.png")
        
        # Put QR code image in the same directory as final_path
        qrcode_path = os.path.join(os.path.dirname(final_path), new_filename+"qrcode.png")
        shutil.copy(new_filename+"qrcode.png", qrcode_path)
        # Delete temporary QR code image
        os.remove(new_filename+"qrcode.png")
        qrcode_url = DOWNLOAD_BASE_URL + new_filename + "qrcode.png"
        print("QR code path: "+qrcode_url)
        
        # Save download history, including download link and QR code path
        save_download_history(url, new_filename, final_path, download_url, qrcode_url)

        return download_url
        
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

    
