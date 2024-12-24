import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from multiprocessing import Pool, cpu_count
import os

def get_description(url):
    if pd.isna(url) or url == "":
        return ""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        description = ' '.join(soup.stripped_strings)
        description = description.replace('\n', ' ').replace('\r', '')
        description = ' '.join(description.split())
        return description
    except requests.RequestException as e:
        print(f"Error fetching description from {url}: {e}")
        return ""

def process_extension(row):
    extension_id, display_name, short_description, description_url = row
    description = get_description(description_url)
    description = description.replace('\n', ' ').strip()
    return [extension_id, display_name, short_description, description]

def load_existing_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=['extensionID', 'displayName', 'shortDescription', 'Description']), set()
    df = pd.read_csv(file_path)
    return df, set(df['extensionID'])

def create_description_csv(input_file, output_file):
    input_df = pd.read_csv(input_file)
    existing_df, existing_ids = load_existing_data(output_file)
    
    # Identify new extensions
    new_extensions = input_df[~input_df['extensionId'].isin(existing_ids)]
    print(f"Found {len(new_extensions)} new extensions to process")
    
    if not new_extensions.empty:
        data = new_extensions[['extensionId', 'displayName', 'shortDescription', 'description_url']].values.tolist()
        
        with Pool(processes=cpu_count()) as pool:
            results = list(pool.imap_unordered(process_extension, data))
            
            for i, _ in enumerate(results, 1):
                print(f"\rProcessed {i}/{len(data)} new extensions", end='', flush=True)
        
        # Combine existing and new data
        new_df = pd.DataFrame(results, columns=['extensionID', 'displayName', 'shortDescription', 'Description'])
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = existing_df
    
    # Write the combined data to CSV
    combined_df.to_csv(output_file, index=False)

def explore_csv(file_path):
    df = pd.read_csv(file_path)
    total_items = len(df)
    install_stats = df['install'].describe()
    rating_stats = df['averagerating'].describe()
    top_10_installs = df.nlargest(10, 'install')[['displayName', 'install']]
    category_distribution = df['categories'].value_counts().head(10)

    print(f"\nTotal number of extensions: {total_items}")
    print("\nInstall count statistics:")
    print(install_stats)
    print("\nRating statistics:")
    print(rating_stats)
    print("\nTop 10 extensions by install count:")
    print(top_10_installs)
    print("\nTop 10 categories:")
    print(category_distribution)

if __name__ == "__main__":
    input_csv_file = 'data/vscode_extension_metadata.csv'
    output_csv_file = 'data/vscode_extension_description.csv'
    
    start_time = time.time()
    create_description_csv(input_csv_file, output_csv_file)
    end_time = time.time()
    
    print(f"\nCreated/Updated CSV file: {output_csv_file}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    explore_csv(input_csv_file)