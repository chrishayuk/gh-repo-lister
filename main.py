import requests
import configparser
import json
import os

GITHUB_API_URL = "https://api.github.com/search/repositories"

def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def get_language_term_pairs(config):
    language_term_section = config['LANGUAGE_TERM_PAIRS']
    return {
        language: [term.strip() for term in terms.split(',')]
        for language, terms in language_term_section.items()
    }

config = load_config('config.ini')
output_directory = config['OUTPUT']["OUTPUT_DIRECTORY"]
surql_directory = os.path.join(output_directory,"surql")
repos_jsonl_path = os.path.join(output_directory,"repos.jsonl")
repos_txt_path = os.path.join(output_directory,"repos.txt")

# make the surql directory
os.makedirs(output_directory, exist_ok=True)
os.makedirs(surql_directory, exist_ok=True)

# github parameters
num_results = int(config['GITHUB']['NUM_RESULTS'])
sort_by = config['GITHUB']['SORT_BY']
order = config['GITHUB']['ORDER']
licenses = [
    license.strip() for license in config['GITHUB']['LICENSES'].split(',')
    if license.strip()
]

# get the language term pairs
language_term_pairs = get_language_term_pairs(config)

secrets = load_config('secrets.ini')
TOKEN = secrets['DEFAULT']['token']
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_repositories(language, license, term, sort_by, order, num_results):
    query = f"{term} license:{license} language:{language}"
    params = {
        "q": query,
        "sort": sort_by,
        "order": order,
        "per_page": num_results
    }
    response = requests.get(GITHUB_API_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    items = response.json().get("items", [])
    
    return [
        {
            "org": repo["full_name"].split('/')[0],
            "repo": repo["name"],
            "path": repo["full_name"],
            "url": "https://github.com/" + repo["full_name"],
            "description": repo["description"],
            "license": repo["license"]["name"] if repo.get("license") else "N/A",
            "stars": repo["stargazers_count"],
            "language": repo["language"],
            "last_commit_date": repo["pushed_at"]
        }
        for repo in items
    ]
        
def create_org_surql(org):
    """Generate a CREATE statement for an organization."""
    return (f"// this creates the ingested repo organizations\n"
            f"CREATE repo_org:{{provider:'github', org:'{org}'}} SET\n"
            f"    provider = repo_provider:github,\n"
            f"    org = '{org}',\n"
            f"    url = 'https://github.com/{org}/',\n"
            f"    ingested_at = time::now()\n"
            f";\n")

def create_repo_surql(repo):
    """Generate a CREATE statement for a repository."""
    return (f"// this creates the ingested repos\n"
            f"CREATE repo:{{provider:'github', org:'{repo['org']}', repo:'{repo['repo']}'}} SET\n"
            f"    org = repo_org:{{provider:'github', org:'{repo['org']}'}},\n"
            f"    name = '{repo['repo']}',\n"
            f"    privacy = 'public',\n"
            f"    repo_url = 'https://github.com/{repo['path']}/',\n"
            f"    description = '{repo['description']}',\n"
            f"    license = '{repo['license']}',\n"
            f"    stars = {repo['stars']},\n"
            f"    last_commit_date = '{repo['last_commit_date']}',\n"
            f"    language = '{repo['language']}',\n"
            f"    ingested_at = time::now()\n"
            f";\n")

def save_repo_providers_surql():
    # Create the 01-repo-provider.surql file with static content
    with open(os.path.join(surql_directory, "01-repo-provider.surql"), "w") as provider_file:
        provider_file.write("// this creates the supported repo providers\n"
                        "CREATE repo_provider:github SET\n"
                        "    provider = 'github',\n"
                        "    url = 'https://github.com/',\n"
                        "    ingested_at = time::now()\n"
                        ";\n")
        
def save_results_to_jsonl(repositories, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        for repo in repositories:
            f.write(f"{json.dumps(repo)}\n")

def save_repos_txt(repositories, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        for repo in repositories:
            f.write(f"{repo['url']}\n")

def save_repo_org_surql_to_file(orgs):
    with open(os.path.join(surql_directory, "02-repo-org.surql"), 'w', encoding='utf-8') as f:
        for org in orgs:
            f.write(create_org_surql(org))

def save_repo_surql_to_file(repositories):
    with open(os.path.join(surql_directory, "03-repo.surql"), 'w', encoding='utf-8') as f:
        for repo in repositories:
            f.write(create_repo_surql(repo))

if __name__ == "__main__":
    # get a unique org list
    unique_orgs = set()

    # save the surql providers
    save_repo_providers_surql()

    # save the repos
    for language, terms in language_term_pairs.items():
        for term in terms:
            repos = get_repositories(language, "mit", term, sort_by, order, num_results)
    
    # Populate the unique_orgs set
    for repo in repos:
        unique_orgs.add(repo['org'])
        
    # save the orgs surql
    save_repo_org_surql_to_file(unique_orgs)

    # save results and repos
    save_results_to_jsonl(repos, repos_jsonl_path)
    save_repos_txt(repos, repos_txt_path)
    save_repo_surql_to_file(repos)
