# VSCode Extension Data Collection and Analysis

This directory contains Python scripts for collecting and analyzing VSCode extension data, with a focus on security analysis and AI-related plugins.

## Scripts Overview

1. `1_crawler_store_ext.py`
   - Crawls the VSCode Marketplace for extension metadata
   - Collects basic information like name, publisher, ratings, and installation count
   - Outputs: `data/vscode_extension_metadata.csv` and `data/vscode_extension_original.json`

2. `2_download_vsix.py`
   - Downloads VSIX packages for each extension
   - Output directory: `data/vsix/`

3. `3_pack_visx_code.py`
   - Extracts source code from downloaded VSIX packages
   - Processes JavaScript, TypeScript, and JSON files
   - Organizes extracted files by extension ID
   - Output directory: `data/code/`

4. `4_crawl_detailed_maketplace_description.py`
   - Retrieves comprehensive marketplace descriptions
   - Extracts features, requirements, and dependencies
   - Updates metadata with detailed information
   - Updates: `data/vscode_extension_description.json`

5. `5_filter_ai_plugins.py`
   - Identifies AI-related extensions using keyword analysis
   - Generates statistics and visualizations
   - Creates filtered dataset of AI plugins
   - Output: `data/ai_plugins.csv` and visualizations in `data/fig/`


## Requirements

- Python 3.8+
- Required packages:
  ```
  requests>=2.26.0
  pandas>=1.3.0
  beautifulsoup4>=4.9.3
  matplotlib>=3.4.3
  seaborn>=0.11.2
  ```

## Usage

Run scripts in sequence:
   ```bash
   python 1_crawler_store_ext.py  # Collect metadata
   python 2_download_vsix.py      # Download extensions
   python 3_pack_visx_code.py     # Extract code
   python 4_crawl_detailed_maketplace_description.py  # Get details
   python 5_filter_ai_plugins.py  # Analyze AI plugins
   ```

## Notes

- The marketplace crawler respects rate limits and includes appropriate delays
- The analysis primarily focuses on JavaScript and TypeScript files
- Each script can be run independently if the required input files exist

