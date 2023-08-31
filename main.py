import os
import argparse
from config_manager import load_config, get_language_term_pairs
from github_api import get_repositories, get_curated_repos_data
from output_handler import save_repo_providers_surql, save_repo_org_surql_to_file, save_results_to_jsonl, save_repos_txt, save_repo_surql_to_file

def get_arguments():
    parser = argparse.ArgumentParser(description="Generate SURQL and repo data from GitHub.")
    parser.add_argument("--curated", help="Use curated list of repos", action="store_true")
    parser.add_argument("--list-path", help="Path to the curated list", type=str)
    return parser.parse_args()

def load_configuration():
    config = load_config('config.ini')
    secrets = load_config('secrets.ini')
    return config, secrets

def setup_sub_directory(language_directory, sub_type):
    sub_directory = os.path.join(language_directory, sub_type)
    os.makedirs(sub_directory, exist_ok=True)
    return sub_directory

def fetch_repos_for_language(language, terms, licenses, sort_by, order, num_results, TOKEN):
    all_repos = []
    for term in terms:
        for license in licenses:
            repos = get_repositories(language, license, term, sort_by, order, num_results, TOKEN)
            for repo in repos:
                repo['language'] = language
            all_repos.extend(repos)
    return all_repos

def save_output(all_repos, sub_directory):
    repos_jsonl_path = os.path.join(sub_directory, "repos.jsonl")
    repos_txt_path = os.path.join(sub_directory, "repos.txt")
    surql_directory = os.path.join(sub_directory, "surql")
    os.makedirs(surql_directory, exist_ok=True)
    
    save_results_to_jsonl(all_repos, repos_jsonl_path)
    save_repos_txt(all_repos, repos_txt_path)
    save_repo_surql_to_file(surql_directory, all_repos)

def main():
    args = get_arguments()
    config, secrets = load_configuration()
    curated_list_paths = config['CURATED_LISTS'] if 'CURATED_LISTS' in config else {}

    if args.curated and not curated_list_paths:
        raise ValueError("Please provide the path to your curated list using --list-path argument or configure it in the .ini file.")
    
    output_directory = config['OUTPUT']["OUTPUT_DIRECTORY"]
    num_results = int(config['GITHUB']['NUM_RESULTS'])
    sort_by = config['GITHUB']['SORT_BY']
    order = config['GITHUB']['ORDER']
    licenses = [license.strip() for license in config['GITHUB']['LICENSES'].split(',') if license.strip()]
    language_term_pairs = get_language_term_pairs(config)
    TOKEN = secrets['DEFAULT']['token']

    unique_orgs = set()

    if args.curated:
        for language, curated_list_path in curated_list_paths.items():
            all_repos = get_curated_repos_data(curated_list_path, TOKEN)
            local_unique_orgs = set()  # for each language
            for repo in all_repos:
                repo['language'] = language
                if 'org' in repo:
                    local_unique_orgs.add(repo['org'])
            language_directory = setup_sub_directory(output_directory, language)
            curated_directory = setup_sub_directory(language_directory, "curated")
            save_output(all_repos, curated_directory)
            
            # Save org and provider surql files inside the loop
            surql_directory_curated = os.path.join(curated_directory, "surql")
            if os.path.exists(surql_directory_curated):
                save_repo_providers_surql(surql_directory_curated)
                save_repo_org_surql_to_file(surql_directory_curated, local_unique_orgs)
    else:
        for language, terms in language_term_pairs.items():
            all_repos = fetch_repos_for_language(language, terms, licenses, sort_by, order, num_results, TOKEN)
            for repo in all_repos:
                if 'org' in repo:
                    unique_orgs.add(repo['org'])
            language_directory = setup_sub_directory(output_directory, language)
            search_directory = setup_sub_directory(language_directory, "search")
            save_output(all_repos, search_directory)

    for language in language_term_pairs.keys():
        language_directory = os.path.join(output_directory, language)
        surql_directory_search = os.path.join(language_directory, "search", "surql")
        surql_directory_curated = os.path.join(language_directory, "curated", "surql")
        
        if os.path.exists(surql_directory_search):
            save_repo_providers_surql(surql_directory_search)
            save_repo_org_surql_to_file(surql_directory_search, unique_orgs)
        
        if os.path.exists(surql_directory_curated):
            save_repo_providers_surql(surql_directory_curated)
            save_repo_org_surql_to_file(surql_directory_curated, unique_orgs)

if __name__ == "__main__":
    main()
