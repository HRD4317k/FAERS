import os
import requests
import zipfile
import tempfile
from tqdm import tqdm
from pathlib import Path

# Base URL for FAERS ASCII data
BASE_URL = "https://fis.fda.gov/content/Exports/faers_ascii_{year}q{quarter}.zip"

# Data directory
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

def main(years, quarters):
    # Ensure directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    for year in years:
        for quarter in quarters:
            url = BASE_URL.format(year=year, quarter=quarter)
            zip_filename = f"faers_ascii_{year}q{quarter}.zip"
            zip_path = DATA_DIR / zip_filename
            extract_dir = DATA_DIR / f"{year}q{quarter}"
            
            if extract_dir.exists():
                print(f"Skipping {year} Q{quarter}, already extracted.")
                continue
                
            print(f"Downloading {year} Q{quarter} from {url}...")
            try:
                download_file(url, zip_path)
            except Exception as e:
                print(f"Failed to download {url}: {e}")
                continue
                
            print(f"Extracting {zip_filename}...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                print(f"Extracted to {extract_dir}")
                os.remove(zip_path) # Clean up zip file
                print(f"Deleted {zip_filename}")
            except Exception as e:
                print(f"Failed to extract {zip_filename}: {e}")

if __name__ == "__main__":
    # To start, just downloading 2023 Q1
    # For full 2023-2024, modify this to years=[2023, 2024], quarters=[1, 2, 3, 4]
    years = [2023]
    quarters = [1]
    
    # Change working directory to the script's directory so relative paths work
    os.chdir(Path(__file__).parent)
    main(years, quarters)
