import os
import json
from surql_generator import generate_repo_provider_surql, create_org_surql, create_repo_surql


def save_content_to_file(filename, content):
    """Saves the content to the specified filename."""
    with open(filename, "w", encoding='utf-8') as f:
        f.write(content)

def save_repo_providers_surql(surql_directory):
    """Generates and saves the repo provider SURQL content."""
    surql_content = generate_repo_provider_surql()
    save_content_to_file(os.path.join(surql_directory, "01-repo-provider.surql"), surql_content)

def save_repo_org_surql_to_file(surql_directory, orgs):
    """Generates and saves the repo organization SURQL content."""
    content = ''.join([create_org_surql(org) for org in orgs])
    save_content_to_file(os.path.join(surql_directory, "02-repo-org.surql"), content)

def save_repo_surql_to_file(surql_directory, repositories):
    """Generates and saves the repository SURQL content."""
    content = ''.join([create_repo_surql(repo) for repo in repositories])
    save_content_to_file(os.path.join(surql_directory, "03-repo.surql"), content)

def save_results_to_jsonl(repositories, file_path):
    """Saves the list of repositories in JSONL format."""
    with open(file_path, 'w', encoding='utf-8') as f:
        for repo in repositories:
            f.write(f"{json.dumps(repo)}\n")

def save_repos_txt(repositories, file_path):
    """Saves the list of repository URLs to a text file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        for repo in repositories:
            f.write(f"{repo['url']}\n")
