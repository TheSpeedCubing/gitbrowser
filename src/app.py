import os
import requests
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
import cmarkgfm

app = Flask(__name__)
app.url_map.strict_slashes = False


if __name__ != "__main__":
    import logging
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

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
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json().get("default_branch", "main")
    except Exception as e:
        app.logger.error(f"Error fetching default branch: {e}")
        return None

def fetch_git_tree(owner, repo, branch):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    try:
        r = requests.get(url, headers=get_headers())
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json().get("tree", [])
    except Exception as e:
        app.logger.error(f"Error fetching tree: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html', owner="TheSpeedCubing", repo="gitbrowser", branch="main")

@app.route('/<owner>/<repo>')
def repo_root(owner, repo):
    branch = get_default_branch(owner, repo)
    if not branch:
        abort(404)
    return render_template('index.html', owner=owner, repo=repo, branch=branch)

@app.route('/<owner>/<repo>/tree/<branch>')
def index(owner, repo, branch):
    if fetch_git_tree(owner, repo, branch) is None:
        abort(404)
    return render_template('index.html', owner=owner, repo=repo, branch=branch)

@app.route('/api/tree/<owner>/<repo>/tree/<branch>')
def get_tree(owner, repo, branch):    
    cache_key = f"{owner}/{repo}/{branch}"
    
    now = time.time()
    expired_keys = [k for k, v in TREE_CACHE.items() if now - v["timestamp"] > 30]
    for k in expired_keys:
        del TREE_CACHE[k]
    
    if cache_key in TREE_CACHE:
        return jsonify(TREE_CACHE[cache_key]["tree"])
    
    tree_data = fetch_git_tree(owner, repo, branch)
    if tree_data is None:
        abort(404)
        
    TREE_CACHE[cache_key] = {
        "branch": branch, 
        "tree": tree_data,
        "timestamp": now
    }
    
    return jsonify(tree_data)

@app.route('/api/render/<owner>/<repo>/tree/<branch>')
def render_markdown(owner, repo, branch):
    path = request.args.get('path', '')
    
    if not path:
        return "Missing path", 400

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
