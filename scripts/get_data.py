import requests
import pandas as pd
import time
import json
from tqdm import tqdm
    
# get you a akey 
# https://www.eia.gov/opendata/register.php, 
API_KEY = ""

def build_base_url(api_key):
    """EIA API base URL with the given API key."""
    return (
        "https://api.eia.gov/v2/petroleum/pri/gnd/data/"
        f"?api_key={api_key}"
        "&frequency=weekly"
        "&data[0]=value"
        "&facets[duoarea][]=NUS&facets[duoarea][]=R10&facets[duoarea][]=R1X&facets[duoarea][]=R1Y"
        "&facets[duoarea][]=R1Z&facets[duoarea][]=R20&facets[duoarea][]=R30&facets[duoarea][]=R40"
        "&facets[duoarea][]=R50&facets[duoarea][]=R5XCA&facets[duoarea][]=SCA&facets[duoarea][]=SCO"
        "&facets[duoarea][]=SFL&facets[duoarea][]=SMA&facets[duoarea][]=SMN&facets[duoarea][]=SNY"
        "&facets[duoarea][]=SOH&facets[duoarea][]=STX&facets[duoarea][]=SWA&facets[duoarea][]=Y05LA"
        "&facets[duoarea][]=Y05SF&facets[duoarea][]=Y35NY&facets[duoarea][]=Y44HO&facets[duoarea][]=Y48SE"
        "&facets[duoarea][]=YBOS&facets[duoarea][]=YCLE&facets[duoarea][]=YDEN&facets[duoarea][]=YMIA"
        "&facets[duoarea][]=YORD"
        "&facets[process][]=PTE"
        "&facets[product][]=EPD2D&facets[product][]=EPD2DM10&facets[product][]=EPD2DXL0"
        "&facets[product][]=EPM0&facets[product][]=EPM0R&facets[product][]=EPM0U"
        "&facets[product][]=EPMM&facets[product][]=EPMMR&facets[product][]=EPMMU"
        "&facets[product][]=EPMP&facets[product][]=EPMPR&facets[product][]=EPMPU"
        "&facets[product][]=EPMR&facets[product][]=EPMRR&facets[product][]=EPMRU"
        "&start=1990-08-20&end=2024-12-31"
        "&sort[0][column]=period&sort[0][direction]=desc"
    )

def fetch_paginated_data(base_url, limit=5000):
    """Fetch paginated data from the EIA API with tqdm progress b/c you need validation."""
    offset = 0
    all_records = []
    page = 1
    pbar = None

    while True:
        try:
            paginated_url = f"{base_url}&offset={offset}&length={limit}"
            response = requests.get(paginated_url)
            response.raise_for_status()

            result = response.json()
            chunk = result.get("response", {}).get("data", [])
            total = int(result.get("response", {}).get("total", 0))

            if not chunk:
                print("✅ All data retrieved.")
                break

            all_records.extend(chunk)

            if pbar is None:
                total_pages = (total + limit - 1) // limit
                pbar = tqdm(total=total_pages, desc="Downloading", unit="page")

            pbar.update(1)

            offset += limit
            page += 1

            if offset >= total:
                break

            time.sleep(1)  # Avoid rate limits

        except requests.RequestException as e:
            print(f"Request error: {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

    if pbar:
        pbar.close()

    return all_records

def save_data(records, json_path="eia_final_raw.json", csv_path="eia_final_flat.csv"):
    """Save the records to JSON and CSV files."""
    try:
        with open(json_path, "w") as f:
            json.dump(records, f, indent=2)

        df = pd.DataFrame(records)
        df["period"] = pd.to_datetime(df["period"], errors='coerce')
        df.rename(columns={"value": "price"}, inplace=True)
        df = df[["period", "price", "duoarea", "product"]]
        df.to_csv(csv_path, index=False)

        print(f"Files saved: {csv_path}, {json_path}")
    except Exception as e:
        print(f"Error saving files: {e}")

def main():
    if not API_KEY or API_KEY == "your_api_key_here":
        print("Please insert your EIA API key in the script.")
        return

    base_url = build_base_url(API_KEY)
    records = fetch_paginated_data(base_url)

    if records:
        save_data(records)
    else:
        print("No data returned.")

if __name__ == "__main__":
    main()