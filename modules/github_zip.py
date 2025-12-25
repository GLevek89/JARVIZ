from __future__ import annotations

import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Optional, Callable

import requests

@dataclass(frozen=True)
class RepoRef:
    owner: str
    repo: str
    branch: str

def parse_repo(url: str, branch: str) -> RepoRef:
    url = (url or "").strip()
    branch = (branch or "").strip() or "main"

    ssh_match = re.match(r"git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^.]+)(?:\.git)?$", url)
    if ssh_match:
        return RepoRef(ssh_match.group("owner"), ssh_match.group("repo"), branch)

    parsed = urlparse(url)
    if parsed.netloc.lower() not in ("github.com", "www.github.com"):
        raise ValueError("That does not look like a github.com link.")

    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise ValueError("Paste a GitHub repo link like https://github.com/OWNER/REPO")

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]

    if len(parts) >= 4 and parts[2] == "tree":
        branch = parts[3]

    return RepoRef(owner, repo, branch)

def zip_url(ref: RepoRef) -> str:
    return f"https://github.com/{ref.owner}/{ref.repo}/archive/refs/heads/{ref.branch}.zip"

def download_repo_zip(
    repo_url: str,
    branch: str,
    out_dir: str,
    token: Optional[str] = None,
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> str:
    ref = parse_repo(repo_url, branch)
    url = zip_url(ref)

    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{ref.owner}_{ref.repo}_{ref.branch}.zip")

    headers = {}
    if token:
        headers["Authorization"] = f"token {token.strip()}"

    with requests.get(url, headers=headers, stream=True, timeout=60) as r:
        if r.status_code == 404:
            raise RuntimeError("404 Not Found. Check owner/repo/branch.")
        if r.status_code in (401, 403):
            raise RuntimeError(f"Auth failed ({r.status_code}). If private repo, add a token.")
        if r.status_code != 200:
            raise RuntimeError(f"Download failed: HTTP {r.status_code}")

        ctype = (r.headers.get("Content-Type") or "").lower()
        if "text/html" in ctype:
            raise RuntimeError("Got HTML instead of a zip. Link or auth may be wrong.")

        total = int(r.headers.get("Content-Length", "0") or "0")
        done = 0

        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if not chunk:
                    continue
                f.write(chunk)
                done += len(chunk)
                if on_progress:
                    on_progress(done, total)

    return out_path
