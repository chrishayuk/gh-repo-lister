import os
import json
from config_manager import load_config, get_language_term_pairs
from github_api import get_repositories
from surql_generator import create_org_surql, create_repo_surql, generate_repo_provider_surql

# Load configurations
config = load_config('config.ini')
output_directory = config['OUTPUT']["OUTPUT_DIRECTORY"]
surql_directory = os.path.join(output_directory, "surql")
repos_jsonl_path = os.path.join(output_directory, "repos.jsonl")
repos_txt_path = os.path.join(output_directory, "repos.txt")

# Setup directories
os.makedirs(output_directory, exist_ok=True)
os.makedirs(surql_directory, exist_ok=True)

# Load GitHub parameters
num_results = int(config['GITHUB']['NUM_RESULTS'])
sort_by = config['GITHUB']['SORT_BY']
order = config['GITHUB']['ORDER']
licenses = [license.strip() for license in config['GITHUB']['LICENSES'].split(',') if license.strip()]

# Load language-term pairs
language_term_pairs = get_language_term_pairs(config)

# Load secrets
secrets = load_config('secrets.ini')
TOKEN = secrets['DEFAULT']['token']

def save_content_to_file(filename, content):
    with open(filename, "w", encoding='utf-8') as f:
        f.write(content)

def save_repo_providers_surql():
    surql_content = generate_repo_provider_surql()
    save_content_to_file(os.path.join(surql_directory, "01-repo-provider.surql"), surql_content)

def save_repo_org_surql_to_file(orgs):
    content = ''.join([create_org_surql(org) for org in orgs])
    save_content_to_file(os.path.join(surql_directory, "02-repo-org.surql"), content)

def save_repo_surql_to_file(repositories):
    content = ''.join([create_repo_surql(repo) for repo in repositories])
    save_content_to_file(os.path.join(surql_directory, "03-repo.surql"), content)

def save_results_to_jsonl(repositories, file_path):
    content = ''.join([f"{json.dumps(repo)}\n" for repo in repositories])
    save_content_to_file(file_path, content)

def save_repos_txt(repositories, file_path):
    content = ''.join([f"{repo['url']}\n" for repo in repositories])
    save_content_to_file(file_path, content)

if __name__ == "__main__":
    all_repos = []

    for language, terms in language_term_pairs.items():
        for term in terms:
            for license in licenses:  # Loop over all specified licenses
                repos = get_repositories(language, license, term, sort_by, order, num_results, TOKEN)
                all_repos.extend(repos)  # Store all repositories from all calls

    unique_orgs = {repo['org'] for repo in all_repos if 'org' in repo}

    # save the files
    save_repo_providers_surql()
    save_repo_org_surql_to_file(unique_orgs)
    save_results_to_jsonl(all_repos, repos_jsonl_path)
    save_repos_txt(all_repos, repos_txt_path)
    save_repo_surql_to_file(all_repos)
