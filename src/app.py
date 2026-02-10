import os
import requests
import time
from flask import Flask, render_template, request, jsonify
import cmarkgfm

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if GITHUB_TOKEN:
    print("github token found.")
else:
    print("github token not specified.")

app = Flask(__name__)

TREE_CACHE = {}

def get_headers():
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

def get_default_branch(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        r = requests.get(url, headers=get_headers())
        r.raise_for_status()
        return r.json().get("default_branch", "main")
    except Exception as e:
        print(f"Error fetching default branch: {e}")
        return "main"

def fetch_git_tree(owner, repo, branch):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    print(f"Fetching tree from: {url}")
    try:
        r = requests.get(url)
        print(f"Tree response: {r.status_code}")
        if r.status_code != 200:
            print(f"Response: {r.text}")
        r.raise_for_status()
        return r.json().get("tree", [])
    except Exception as e:
        print(f"Error fetching tree: {e}")
        return []

@app.route('/<owner>/<repo>')
@app.route('/<owner>/<repo>/tree/<branch>')
def index(owner, repo, branch=None):
    return render_template('index.html', owner=owner, repo=repo, branch=branch)

@app.route('/api/tree/<owner>/<repo>')
def get_tree(owner, repo):
    branch = request.args.get('branch')
    if not branch:
        branch = get_default_branch(owner, repo)
        
    cache_key = f"{owner}/{repo}/{branch}"
    
    # Prune expired entries from the entire cache to save memory
    now = time.time()
    expired_keys = [k for k, v in TREE_CACHE.items() if now - v["timestamp"] > 30]
    for k in expired_keys:
        del TREE_CACHE[k]
    
    # Check if requested entry still exists (and is fresh)
    if cache_key in TREE_CACHE:
        return jsonify(TREE_CACHE[cache_key]["tree"])
    
    # Fetch fresh data
    tree_data = fetch_git_tree(owner, repo, branch)
    TREE_CACHE[cache_key] = {
        "branch": branch, 
        "tree": tree_data,
        "timestamp": now
    }
    
    return jsonify(tree_data)

@app.route('/api/render/<owner>/<repo>')
def render_markdown(owner, repo):
    path = request.args.get('path', '')
    branch = request.args.get('branch')
    
    if not path:
        return "Missing path", 400
        
    if not branch:
        cache_key_default = f"{owner}/{repo}" 
        branch = get_default_branch(owner, repo)

    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    
    try:
        r = requests.get(raw_url)
        if r.status_code == 404:
            return "File not found", 404
            
        content = r.text
        
        if path.endswith(".md"):
            return cmarkgfm.github_flavored_markdown_to_html(content)
        else:
            return f"<pre>{content}</pre>"
    except Exception as e:
        return f"Error rendering: {e}", 500
