"""
SkillNova AI - Push to GitHub using GitHub REST API
Pushes all application files directly to https://github.com/kavithajayaraj04-cmd/SkillNova
without needing git.exe installed.
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error

REPO = "kavithajayaraj04-cmd/SkillNova"
BRANCH = "main"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_token():
    if len(sys.argv) > 1:
        return sys.argv[1].strip()
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token.strip()
    return None


def get_file_sha(file_path, token):
    url = f"https://api.github.com/repos/{REPO}/contents/{file_path}?ref={BRANCH}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "SkillNova-Uploader"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def upload_file(local_path, repo_path, token):
    with open(local_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("utf-8")

    sha = get_file_sha(repo_path, token)
    payload = {
        "message": f"feat: add {repo_path} for SkillNova AI platform",
        "content": content_b64,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha

    url = f"https://api.github.com/repos/{REPO}/contents/{repo_path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "SkillNova-Uploader",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✓ Uploaded {repo_path}")
            return True
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        print(f"✗ Failed {repo_path}: {e.code} - {err}")
        return False


def main():
    token = get_token()
    if not token:
        print("Usage: python push_to_github.py <YOUR_GITHUB_PERSONAL_ACCESS_TOKEN>")
        print("Or set GITHUB_TOKEN environment variable.")
        sys.exit(1)

    print(f"Pushing SkillNova AI files to https://github.com/{REPO}...")
    uploaded_count = 0

    def is_ignored(name):
        if name in [".env", "skillnova.db", "test_skillnova.db"]:
            return True
        if name.endswith(".zip") or name.endswith(".log") or name.endswith(".pyc"):
            return True
        if "__pycache__" in name or name == ".git":
            return True
        return False

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not is_ignored(d)]
        for f in files:
            if is_ignored(f):
                continue
            local_fp = os.path.join(root, f)
            rel_path = os.path.relpath(local_fp, BASE_DIR).replace("\\", "/")
            if upload_file(local_fp, rel_path, token):
                uploaded_count += 1

    print(f"\n🎉 Successfully committed and pushed {uploaded_count} files to GitHub!")


if __name__ == "__main__":
    main()
