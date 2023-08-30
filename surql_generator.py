import os

def generate_repo_provider_surql():
    return ("// this creates the supported repo providers\n"
            "CREATE repo_provider:github SET\n"
            "    provider = 'github',\n"
            "    url = 'https://github.com/',\n"
            "    ingested_at = time::now()\n"
            ";\n")

def create_org_surql(org):
    """Generate a CREATE statement for an organization."""
    org_escaped = org.replace("'", "''")
    return (f"// this creates the ingested repo organizations\n"
            f"CREATE repo_org:{{provider:'github', org:'{org_escaped}'}} SET\n"
            f"    provider = repo_provider:github,\n"
            f"    org = '{org_escaped}',\n"
            f"    url = 'https://github.com/{org_escaped}/',\n"
            f"    ingested_at = time::now()\n"
            f";\n")

def create_repo_surql(repo):
    """Generate a CREATE statement for a repository."""
    
    # Check for the existence of necessary keys and provide defaults if missing
    org = repo.get('org', 'UnknownOrg').replace("'", "''")
    repo_name = repo.get('repo', 'UnknownRepo').replace("'", "''")
    path = repo.get('path', 'UnknownPath')
    
    # get the description, handling unknowns
    description_value = repo.get('description', 'No description')
    description = (description_value or 'No description').replace("'", "''")

    # get stars and last commit
    stars = repo.get('stars', 0)
    last_commit_date = repo.get('last_commit_date', 'UnknownDate')

    # get language
    language = repo.get('language', 'UnknownLanguage').replace("'", "''")

    # calculate the license
    license_value = repo.get('license', {})
    if isinstance(license_value, dict):
        license_name = license_value.get('name', 'N/A')
    else:
        license_name = str(license_value)
    license = license_name.replace("'", "''")

    return (f"// this creates the ingested repos\n"
            f"CREATE repo:{{provider:'github', org:'{org}', repo:'{repo_name}'}} SET\n"
            f"    org = repo_org:{{provider:'github', org:'{org}'}},\n"
            f"    name = '{repo_name}',\n"
            f"    privacy = 'public',\n"
            f"    repo_url = 'https://github.com/{path}/',\n"
            f"    description = '{description}',\n"
            f"    license = '{license}',\n"
            f"    stars = {stars},\n"
            f"    last_commit_date = '{last_commit_date}',\n"
            f"    language = '{language}',\n"
            f"    ingested_at = time::now()\n"
            f";\n")
