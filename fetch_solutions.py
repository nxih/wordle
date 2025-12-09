import requests
import datetime
import os
import json
from pathlib import Path

OUTPUT_DIR = Path("wordle_archive")
BASE_URL = "https://www.nytimes.com/svc/wordle/v2/"

def fetch_and_archive(days_to_fetch):
    """
    Calculates future dates, fetches the Wordle data, and saves it, 
    conditionally overwriting existing files if the solution changes.
    """
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    start_date = datetime.date.today()
    print(f"Starting data fetch for {days_to_fetch} days from: {start_date}")

    files_written = 0

    for i in range(days_to_fetch):
        target_date = start_date + datetime.timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")
        
        url = f"{BASE_URL}{date_str}.json"
        output_path = OUTPUT_DIR / f"{date_str}.json"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            new_data = response.json()
            
            new_solution = new_data.get("solution") 
            
            
            if output_path.exists():
                with open(output_path, 'r') as f:
                    existing_data = json.load(f)
                
                existing_solution = existing_data.get("solution")

                if new_solution == existing_solution:
                    print(f"[{date_str}] Solution is unchanged. Skipping write.")
                    continue
                else:
                    print(f"[{date_str}] **Solution CHANGED** ('{existing_solution}' -> '{new_solution}'). Overwriting file.")
            
            with open(output_path, 'w') as f:
                json.dump(new_data, f, indent=4)
            
            files_written += 1

        except requests.exceptions.RequestException as e:
            print(f"[{date_str}] Error fetching data: {e}")
        except Exception as e:
            print(f"[{date_str}] An unexpected error occurred: {e}")

    print(f"\n--- Script Complete. {files_written} files were created or updated. ---")
    
if __name__ == "__main__":
    # The cron job will run this: fetch 25 days
    fetch_and_archive(25)