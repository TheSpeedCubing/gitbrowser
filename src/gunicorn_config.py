import os

def on_starting(server):
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        print("GITHUB_TOKEN found.")
    else:
        print("GITHUB_TOKEN not specified.")
