import json
import os
from multiprocessing import Pool
import subprocess
import sys
import argparse
from ext_js import pdg_test_analysis
from meta_analysis import analyze_package_json, process_commands

def parse_arguments():
    parser = argparse.ArgumentParser(description='Analyze VSCode extension code for security vulnerabilities')
    
    parser.add_argument(
        '--extension-id',
        required=True,
        help='ID of the extension to analyze'
    )
    
    parser.add_argument(
        '--extension-dir',
        required=True,
        help='Base directory containing unpacked extensions'
    )
    
    parser.add_argument(
        '--output-dir',
        required=True,
        help='Directory to store analysis results'
    )
    
    parser.add_argument(
        '--sources-file',
        required=True,
        help='Path to sources.json containing sink/source definitions'
    )
    
    parser.add_argument(
        '--max-lines',
        type=int,
        default=8000,
        help='Maximum number of lines before enabling pruned analysis (default: 8000)'
    )

    return parser.parse_args()

def process_one_extension(args):
    """
    Process a single extension for security analysis
    
    Args:
        args: Command line arguments containing extension details
    """
    # Construct paths
    extension_path = os.path.join(args.extension_dir, args.extension_id)
    cs_path = os.path.join(extension_path, "extension.js")
    store_dir = os.path.join(args.output_dir, args.extension_id)

    # Create output directory if it doesn't exist
    if not os.path.exists(store_dir):
        os.makedirs(store_dir)

    # Validate input file exists
    if not os.path.exists(cs_path):
        print(f"Error: extension.js not found at {cs_path}")
        return

    # Read and validate content
    try:
        with open(cs_path, "r", encoding='utf-8') as f:
            content = f.readlines()
            if not content:
                print(f"Warning: Empty file at {cs_path}")
                return
            
            is_pruned = len(content) > args.max_lines
            
    except Exception as e:
        print(f"Error reading {cs_path}: {str(e)}")
        return

    # Run analysis
    store_json_p = os.path.join(store_dir, "analysis.json")
    try:
        pdg_test_analysis(
            cs_path, 
            store_json_p, 
            args.sources_file,
            Prune_Analysis=is_pruned
        )
        print(f"Analysis completed for {args.extension_id}")
        
    except Exception as e:
        print(f"Error analyzing {args.extension_id}: {str(e)}")

def main():
    args = parse_arguments()
    process_one_extension(args)

if __name__ == "__main__":
    main()
