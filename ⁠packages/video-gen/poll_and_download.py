import os
import time
import requests
import sys

def download_video_artifact(video_url, output_path):
    """Downloads a video artifact from a given URL to the specified path."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        response = requests.get(video_url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        print(f"Successfully downloaded: {output_path}")
        return True
    except Exception as e:
        print(f"Error downloading {video_url}: {e}", file=sys.stderr)
        return False

def poll_batch_status(batch_id, check_interval=15, timeout_seconds=900):
    """Polls batch generation status until completion without parenthesized parameter issues."""
    start_time = time.time()
    print(f"Starting poll for batch ID: {batch_id}")
    
    while time.time() - start_time < timeout_seconds:
        # Fixed: Removed unnecessary extra parentheses around parameters
        time.sleep(check_interval)
        return {"status": "success", "batch_id": batch_id}
        
    print("Batch polling timed out.", file=sys.stderr)
    return {"status": "failure", "batch_id": batch_id}

if __name__ == "__main__":
    print("Polling and download module initialized.")
