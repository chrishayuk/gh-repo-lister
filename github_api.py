import requests

# Constants
GITHUB_API_URL = "https://api.github.com/search/repositories"
GITHUB_REPO_URL = "https://api.github.com/repos/"

# Utility Functions
def extract_user_and_repo_from_url(url):
    """
    Extract the user and repo name from a given GitHub URL.
    """
    parts = url.split("/")
    user, repo_name = parts[-2], parts[-1]
    return user, repo_name

def get_single_repository(user, repo_name, token):
    """
    Fetch metadata for a single GitHub repository based on user and repo name.
    """
    HEADERS = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(f"{GITHUB_REPO_URL}{user}/{repo_name}", headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching repo: {user}/{repo_name}. Status code: {response.status_code}")
        return None

    repo = response.json()

    return {
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

# Core Functions
def get_curated_repos_data(curated_list_path, token):
    """
    Fetch metadata for a list of curated GitHub repositories.
    """
    with open(curated_list_path, 'r') as f:
        urls = f.readlines()

    all_repos = []
    for url in urls:
        user, repo_name = extract_user_and_repo_from_url(url.strip())
        repo_data = get_single_repository(user, repo_name, token)
        if repo_data:
            all_repos.append(repo_data)
            
    return all_repos

def get_search_based_repos_data(language_term_pairs, licenses, sort_by, order, num_results, token):
    """
    Fetch repositories based on search criteria.
    """
    all_repos = []
    for language, terms in language_term_pairs.items():
        for term in terms:
            for license in licenses:
                repos = get_repositories(language, license, term, sort_by, order, num_results, token)
                all_repos.extend(repos)
    return all_repos

def get_repositories(language, license, term, sort_by, order, num_results, token):
    """
    Fetch repositories based on GitHub API search.
    """
    HEADERS = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    query = f"{term} license:{license} language:{language}"
    params = {
        "q": query,
        "sort": sort_by,
        "order": order,
        "per_page": num_results
    }
    response = requests.get(GITHUB_API_URL, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise Exception(f"GitHub API Error: {response.json().get('message', 'Unknown error')}")
    
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
