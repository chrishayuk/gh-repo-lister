# GitHub Repository Lister

This script is designed to fetch metadata for GitHub repositories based on specific search criteria or a curated list of repository URLs. It then saves this metadata in different formats for further use.

## Requirements

- Python 3.x
- `requests` module (can be installed via pip)

## Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install the required packages:
```bash
pip install requests
```

3. Create a `secrets.ini` file in the root directory with the following content:
```
[DEFAULT]
token=<YOUR_GITHUB_PERSONAL_ACCESS_TOKEN>
```
Replace <YOUR_GITHUB_PERSONAL_ACCESS_TOKEN> with your actual GitHub Personal Access Token. This is required to access the GitHub API without rate limitations.

4. Update the `config.ini` file with your desired parameters.
## Usage

Run the script by executing:
```bash
python main.py
```
You'll be prompted to choose between using a curated list of repository URLs or fetching repositories based on search criteria defined in the `config.ini` file.

the following script will let you generate the curated lists

```bash
python main.py --curated
```

## Features

- **Fetch Metadata**: The script fetches metadata such as the repository name, URL, description, license, star count, primary language, and last commit date.
  
- **Flexible Output**: The metadata can be saved in multiple formats, including `.jsonl`, `.txt`, and `.surql`.
  
- **Curated or Searched**: You can provide a curated list of repository URLs or let the script search GitHub based on specific criteria.