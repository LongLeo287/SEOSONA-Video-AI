import re
import requests

def parse_github_url(url):
    """Parse a GitHub URL to extract owner and repo."""
    match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
    if match:
        owner = match.group(1)
        repo = match.group(2).replace(".git", "")
        return owner, repo
    return None, None

def fetch_readme(url):
    """Fetch the README content from a Github repo."""
    owner, repo = parse_github_url(url)
    if not owner or not repo:
        raise ValueError(f"Invalid GitHub URL: {url}")
        
    print(f"[Github Fetcher] Fetching repo info for {owner}/{repo}...")
    
    # Try different branch names and readme formats
    branches = ["main", "master"]
    readme_names = ["README.md", "readme.md", "README.MD", "Readme.md"]
    
    for branch in branches:
        for name in readme_names:
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{name}"
            response = requests.get(raw_url)
            if response.status_code == 200:
                print(f"[Github Fetcher] Successfully fetched README from branch '{branch}'")
                return response.text
                
    raise FileNotFoundError(f"Could not find a README file in {owner}/{repo}")

if __name__ == "__main__":
    content = fetch_readme("https://github.com/obra/superpowers")
    print(f"Fetched {len(content)} characters from README.")
