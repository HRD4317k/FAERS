import os
import requests
from pathlib import Path
from tqdm import tqdm

DATA_DIR = Path("../../data/raw/faers")

def download_file(url, target_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    
    with open(target_path, 'wb') as file, tqdm(
        desc=target_path.name,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Fetching openFDA download links...")
    r = requests.get("https://api.fda.gov/download.json")
    r.raise_for_status()
    data = r.json()
    
    partitions = data['results']['drug']['event']['partitions']
    print(f"Found {len(partitions)} files to download.")
    
    for part in partitions:
        url = part['file']
        filename = url.split('/')[-1]
        target_path = DATA_DIR / filename
        
        if target_path.exists():
            print(f"Skipping {filename}, already downloaded.")
            continue
            
        print(f"Downloading {filename}...")
        try:
            download_file(url, target_path)
        except Exception as e:
            print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    main()
