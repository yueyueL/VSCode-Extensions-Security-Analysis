import requests
import csv
import json
import time

def request_extensions(page_num, page_size=500, max_retries=3, retry_delay=5):
    retries = 0
    while retries < max_retries:
        json_data = {
            "filters": [
                {
                    "criteria": [
                        {"filterType": 8, "value": "Microsoft.VisualStudio.Code"},
                        {"filterType": 10, "value": "target:\"Microsoft.VisualStudio.Code\""},
                        {"filterType": 12, "value": "37888"}
                    ],
                    "pageSize": page_size,
                    "pageNumber": page_num,
                    "sortBy": 4,
                    "sortOrder": 0
                }
            ],
            "flags": 870
        }

        try:
            response = requests.post(
                "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery",
                json=json_data,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            print(f"Error occurred: {err}")
        
        retries += 1
        if retries < max_retries:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print(f"Max retries ({max_retries}) reached. Cannot continue.")
            return None

def extract_extension_data():
    extensions_data = []
    original_extensions = []
    page_num = 1

    while True:
        response = request_extensions(page_num)
        
        if response is None:
            break

        page_extensions = response.get("results", [])[0].get("extensions", [])

        if not page_extensions:
            break

        original_extensions.extend(page_extensions)

        for extension in page_extensions:
            stats = {stat["statisticName"]: stat["value"] for stat in extension.get("statistics", [])}
            publisher = extension.get("publisher", {})
            versions = extension.get("versions", [])
            latest_version = versions[0] if versions else {}
            
            # Extract the description URL
            description_url = ""
            for file in latest_version.get("files", []):
                if file.get("assetType") == "Microsoft.VisualStudio.Services.Content.Details":
                    description_url = file.get("source", "")
                    break
            
            extension_data = {
                "extensionId": extension.get("extensionId", "N/A"),
                "extensionName": extension.get("extensionName", "N/A"),
                "displayName": extension.get("displayName", "N/A"),
                "flags": extension.get("flags", "N/A"),
                "lastUpdated": extension.get("lastUpdated", "N/A"),
                "publishedDate": extension.get("publishedDate", "N/A"),
                "releaseDate": extension.get("releaseDate", "N/A"),
                "publisher_publisherId": publisher.get("publisherId", "N/A"),
                "publisher_publisherName": publisher.get("publisherName", "N/A"),
                "publisher_displayName": publisher.get("displayName", "N/A"),
                "publisher_flags": publisher.get("flags", "N/A"),
                "publisher_domain": publisher.get("domain", "N/A"),
                "publisher_isDomainVerified": publisher.get("isDomainVerified", False),
                "install": stats.get("install", 0),
                "averagerating": stats.get("averagerating", 0),
                "ratingcount": stats.get("ratingcount", 0),
                "trendingdaily": stats.get("trendingdaily", 0),
                "trendingmonthly": stats.get("trendingmonthly", 0),
                "trendingweekly": stats.get("trendingweekly", 0),
                "updateCount": stats.get("updateCount", 0),
                "weightedRating": stats.get("weightedRating", 0),
                "downloadCount": stats.get("downloadCount", 0),
                "categories": ", ".join(extension.get("categories", [])),
                "tags": ", ".join(extension.get("tags", [])),
                "latest_version": latest_version.get("version", "N/A"),
                "latest_version_flags": latest_version.get("flags", "N/A"),
                "latest_version_lastUpdated": latest_version.get("lastUpdated", "N/A"),
                "description_url": description_url,
                "shortDescription": extension.get("shortDescription", "N/A"),
            }
            row['shortDescription'] = row['shortDescription'].replace('\n', ' ').strip()
            extensions_data.append(extension_data)

        print(f"Processed page {page_num}")
        page_num += 1

    return extensions_data, original_extensions


if __name__ == "__main__":
    # Specify the file paths
    csv_file_path = 'data/vscode_extension_metadata.csv'
    json_file_path = 'data/vscode_extension_original.json'  # all original meta data in a json file

    # Extract extension data
    extensions_data, original_extensions = extract_extension_data()

    # Write the data to CSV
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = [
            "extensionId", "extensionName", "displayName", "flags", "lastUpdated", 
            "publishedDate", "releaseDate", "publisher_publisherId", "publisher_publisherName",
            "publisher_displayName", "publisher_flags", "publisher_domain", "publisher_isDomainVerified",
            "install", "averagerating", "ratingcount", "trendingdaily", "trendingmonthly",
            "trendingweekly", "updateCount", "weightedRating", "downloadCount",
            "categories", "tags", "latest_version", "latest_version_flags", "latest_version_lastUpdated",
            "description_url", "shortDescription"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for extension in extensions_data:
            writer.writerow(extension)

    print(f'Total {len(extensions_data)} extension details written to {csv_file_path}')

    # Write the original extension data to JSON
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(original_extensions, json_file, indent=2, ensure_ascii=False)

    print(f'Total {len(original_extensions)} original extension data written to {json_file_path}')