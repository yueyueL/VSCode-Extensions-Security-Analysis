# VSCode Extensions Security Analysis

This repository contains the source code and replication package for our research paper "[Protect Your Secrets: Understanding and Measuring Data Exposure in VSCode Extensions](https://arxiv.org/abs/2412.00707)". Our work investigates security vulnerabilities in VSCode extensions, particularly focusing on credential-related data exposure risks.

## Project Overview

This project provides tools for:
1. Collecting and crawling VSCode extensions from the marketplace
2. Analyzing extensions for potential security vulnerabilities
3. Detecting credential-related data exposure risks

## Repository Structure

- `/vscode-crawler-code/`: Scripts for collecting VSCode extensions (see [crawler README](./vscode-crawler-code/README.md) for details)
- `/analysis-code/`: Security analysis tools
- `/data/`: Storage for extensions and analysis results

## Security Analysis Pipeline

Our analysis pipeline consists of two main stages: extension unpacking and security analysis.

### 1. Extension Unpacking
First, we unpack the VSCode extension (.vsix) files to extract their source code and manifest files. The unpacking process handles both simple and complex extensions with dependencies:

```bash
python3 analysis-code/1_unpack_vsix.py \
    --vsix-path data/vsix/waxidiotic.jw-link.vsix \
    --output-dir data/code \
    --verbose
```

This will:
1. Extract the extension package
2. Process the manifest (package.json)
3. Handle JavaScript bundling, beautify and consolidate all source code into a single file
4. Output processed files to data/code/[extension-id]/

The unpacked files include:
- `extension.js`: Main extension code containing all consolidated source code
- package.json: Extension manifest

### 2. Static Analysis and Feature Extraction
After unpacking, we analyze the extensions for potential security vulnerabilities, particularly focusing on credential exposure risks:

```bash
python3 analysis-code/2_code_analysis.py \
    --extension-id "waxidiotic.jw-link" \
    --extension-dir data/code \
    --output-dir data/output \
    --sources-file data/sources.json
```

The analysis process:
1. Builds Abstract Syntax Trees (AST) using Espree
2. Constructs Program Dependency Graphs (PDG) 
3. Identifies potential credential exposure points by analyzing:
   - Command registrations
   - API usage patterns
   - Configuration access
   - Data flow between extensions
4. Generates detailed analysis reports in data/output/[extension-id]/

### Analysis Configuration
The analysis is guided by predefined patterns in sources.json:
```json
    "sources": {
        "Commands": [
            "commands.registerCommand",
            "commands.registerTextEditorCommand"
            ],
        "WorkspaceConfiguration": [
            "WorkspaceConfiguration.update",
            "WorkspaceConfiguration.get",
            "getConfiguration().get",
            "workspace.getConfiguration"
            
        ],
        "InputBox": [
            "showInputBox"
        ],
        "GlobalState": [
            "globalState.update",
            "globalState.get",
            "workspaceState.update"
        ]
    }
```

### 3. Model Training and Prediction

After extracting security-related patterns using static analysis, we manually labeled these patterns to create a ground truth dataset by examining their code context, documentation, and data flow to determine if they are credential-related.

In our manuscript, we employed a fine-tuned BERT model to automate the detection process. The model is trained on our labeled dataset to classify whether a code pattern involves credential-related operations. The code can be found on `analysis-code/model_detect`

## Dependencies

### Core Dependencies
- Python 3.8+
- Node.js and npm

### External Tools
1. [DoubleX](https://github.com/Aurore54F/DoubleX/): For building program dependency graphs
2. [Espree](https://github.com/eslint/espree): For JavaScript AST generation



## Data Files

- `data/extension_metas.json`: Extension metadata including names, categories, and download links
- `data/sources.json`: API sources for vulnerability detection
- `data/Ground_Truth_datasets.csv`: Manually labeled dataset (16,958 data points across 500 extensions)

## Citation

If you use this work in your research, you are highly encouraged to cite the following [paper](https://arxiv.org/abs/2412.00707):

```bibtex
@inproceedings{liu2025protect,
  title={Protect Your Secrets: Understanding and Measuring Data Exposure in VSCode Extensions},
  author={Liu, Yue and Tantithamthavorn, Chakkrit and Li, Li},
  booktitle={2025 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER)},
  year={2025}
  organization={IEEE}
}
```

### Abstract:
Recent years have witnessed the emerging trend of extensions in modern Integrated Development Environments (IDEs) like Visual Studio Code (VSCode) that significantly enhance developer productivity. 
Especially, popular AI coding assistants like GitHub Copilot and Tabnine provide conveniences like automated code completion and debugging. While these extensions offer numerous benefits, they may introduce privacy and security concerns to software developers.
However, there is no existing work that systematically analyzes the security and privacy concerns, including the risks of data exposure in VSCode extensions.

In this paper, we investigate on the security issues of cross-extension interactions in VSCode and shed light on the vulnerabilities caused by data exposure among different extensions. 
Our study uncovers high-impact security flaws that could allow adversaries to stealthily acquire or manipulate credential-related data (e.g., passwords, API keys, access tokens) from other extensions if not properly handled by extension vendors.
To measure their prevalence, we design a novel automated risk detection framework that leverages program analysis and natural language processing techniques to automatically identify potential risks in VSCode extensions.
By applying our tool to 27,261 real-world VSCode extensions, we discover that 8.5\% of them (i.e., 2,325 extensions) are exposed to credential-related data leakage through various vectors, such as commands, user input, and configurations.
Our study sheds light on the security challenges and flaws of the extension-in-IDE paradigm and provides suggestions and recommendations for improving the security of VSCode extensions and mitigating the risks of data exposure.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Research Artifacts

### Proof-of-Concept Extensions
In Section III of our paper, we demonstrate the attack vectors by creating six proof-of-concept extensions that were successfully published on the VSCode marketplace (and subsequently removed after approval). For research purposes, the source code of these proof-of-concept attacks is available upon request. Please contact us via email.

### Vulnerability Dataset
Our analysis identified 2,325 vulnerable extensions with their corresponding security patterns. This comprehensive dataset, including detailed vulnerability patterns and analysis results, is available for research purposes upon request. Please contact us via email.

### Contact
For access to research artifacts or any questions, please contact:
- Knox (yuehhhliu@gmail.com)
