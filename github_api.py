import requests
import json

GITHUB_API_URL = "https://api.github.com/search/repositories"

def get_repositories(language, license, term, sort_by, order, num_results, token):
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
