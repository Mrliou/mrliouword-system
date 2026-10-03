#!/usr/bin/env python3
"""Resolve the full Closure Sync target set from .mrliou/sync.targets.json.

The policy file is the explicit, versioned authority for *which* repositories
receive the particle dictionary. This tool turns that policy into a concrete,
filtered list by asking the GitHub API, then splits it into matrix chunks.

Fail-closed rules (mirrors sync_manager.py):
  * only repositories under the declared ``owners`` are ever accepted;
  * the source repository is always excluded;
  * archived / disabled / empty repositories are skipped when the policy says so;
  * no network call is made unless a token is supplied.

Stdlib only so it can run in the leanest CI step.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

API = "https://api.github.com"
FULL_NAME = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


# --------------------------------------------------------------------------- #
# GitHub access
# --------------------------------------------------------------------------- #
class GitHub:
    def __init__(self, token: str):
        self.token = token
        self._login: Optional[str] = None

    def _get(self, url: str) -> Any:
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "mrliou-closure-sync-resolver",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310 - fixed https host
            return json.load(response), response.headers

    def _paginate(self, path: str, params: Dict[str, str]) -> Iterable[Dict[str, Any]]:
        params = dict(params, per_page="100")
        url = f"{API}{path}?{urllib.parse.urlencode(params)}"
        while url:
            body, headers = self._get(url)
            for item in body:
                yield item
            url = None
            link = headers.get("Link", "")
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part[part.find("<") + 1 : part.find(">")]

    @property
    def login(self) -> str:
        if self._login is None:
            body, _ = self._get(f"{API}/user")
            self._login = body["login"]
        return self._login

    def owner_kind(self, owner: str) -> str:
        body, _ = self._get(f"{API}/users/{owner}")
        return body.get("type", "User")

    def repos_for_owner(self, owner: str) -> List[Dict[str, Any]]:
        """All repositories owned by ``owner``, private ones included when the token allows."""
        if owner.lower() == self.login.lower():
            # /users/{me}/repos hides my own private repos; /user/repos does not.
            return list(self._paginate("/user/repos", {"affiliation": "owner"}))
        if self.owner_kind(owner) == "Organization":
            return list(self._paginate(f"/orgs/{owner}/repos", {"type": "all"}))
        return list(self._paginate(f"/users/{owner}/repos", {"type": "owner"}))


# --------------------------------------------------------------------------- #
# Policy application (pure, unit-testable)
# --------------------------------------------------------------------------- #
def load_policy(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        policy = json.load(handle)
    owners = policy.get("owners") or []
    if not owners:
        raise ValueError("sync.targets.json must declare at least one owner")
    for name in policy.get("exclude", []) + policy.get("include_extra", []):
        if not FULL_NAME.match(name):
            raise ValueError(f"Malformed repository name in policy: {name!r}")
    return policy


def apply_policy(
    policy: Dict[str, Any],
    repos: Iterable[Dict[str, Any]],
    source_repository: str,
) -> Dict[str, Any]:
    """Filter raw repository records into the approved target list.

    Returns a dict with ``targets`` (sorted full names) and ``skipped``
    (full name -> reason) so the decision is auditable in the evidence ledger.
    """
    owners = {owner.lower() for owner in policy["owners"]}
    exclude = {name.lower() for name in policy.get("exclude", [])}
    exclude.add(source_repository.lower())
    include_extra = [name for name in policy.get("include_extra", [])]

    targets: Dict[str, Dict[str, Any]] = {}
    skipped: Dict[str, str] = {}

    def consider(full_name: str, record: Dict[str, Any]) -> None:
        key = full_name.lower()
        owner = key.split("/", 1)[0]
        if owner not in owners:
            skipped[full_name] = "owner_not_approved"
            return
        if key in exclude:
            skipped[full_name] = "excluded_by_policy"
            return
        if record.get("archived") and policy.get("exclude_archived", True):
            skipped[full_name] = "archived"
            return
        if record.get("disabled") and policy.get("exclude_disabled", True):
            skipped[full_name] = "disabled"
            return
        if record.get("fork") and not policy.get("include_forks", False):
            skipped[full_name] = "fork_not_included"
            return
        if record.get("private") and not policy.get("include_private", False):
            skipped[full_name] = "private_not_included"
            return
        if policy.get("exclude_empty", True) and (
            record.get("size", 1) == 0 or not record.get("default_branch")
        ):
            skipped[full_name] = "empty"
            return
        targets[full_name] = {
            "full_name": full_name,
            "default_branch": record.get("default_branch", "main"),
            "fork": bool(record.get("fork")),
            "private": bool(record.get("private")),
            "visibility": record.get("visibility", "private" if record.get("private") else "public"),
        }

    for record in repos:
        consider(record["full_name"], record)
    for name in include_extra:
        if name not in targets and name not in skipped:
            consider(name, {"full_name": name, "default_branch": "main"})

    ordered = sorted(targets.values(), key=lambda item: item["full_name"].lower())
    return {"targets": ordered, "skipped": dict(sorted(skipped.items()))}


def chunk(targets: List[Dict[str, Any]], size: int) -> List[List[Dict[str, Any]]]:
    size = max(1, int(size))
    return [targets[i : i + size] for i in range(0, len(targets), size)]


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve Closure Sync targets from policy")
    parser.add_argument("--policy", default=".mrliou/sync.targets.json")
    parser.add_argument("--source-repository", required=True, help="owner/repo running the sync")
    parser.add_argument("--token-env", default="SYNC_TOKEN", help="env var holding the GitHub token")
    parser.add_argument("--from-file", help="Offline: JSON array of repo records instead of the API")
    parser.add_argument("--output", default="targets.json")
    parser.add_argument("--github-output", help="Path of $GITHUB_OUTPUT to append matrix/count to")
    args = parser.parse_args()

    policy = load_policy(Path(args.policy))

    if args.from_file:
        with open(args.from_file, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    else:
        token = os.environ.get(args.token_env, "")
        if not token:
            print(f"::error::{args.token_env} is required to resolve targets", file=sys.stderr)
            return 1
        client = GitHub(token)
        raw = []
        for owner in policy["owners"]:
            try:
                raw.extend(client.repos_for_owner(owner))
            except urllib.error.HTTPError as error:
                print(f"::error::GitHub API {error.code} listing {owner}: {error.reason}", file=sys.stderr)
                return 1

    resolved = apply_policy(policy, raw, args.source_repository)
    chunks = chunk(resolved["targets"], policy.get("chunk_size", 20))
    matrix = {"include": [{"chunk": index, "repos": [t["full_name"] for t in group]} for index, group in enumerate(chunks)]}

    payload = {
        "policy_version": policy.get("version"),
        "policy": policy.get("policy"),
        "source_repository": args.source_repository,
        "owners": policy["owners"],
        "target_count": len(resolved["targets"]),
        "targets": resolved["targets"],
        "skipped": resolved["skipped"],
        "chunks": len(chunks),
    }
    Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as handle:
            handle.write(f"matrix={json.dumps(matrix)}\n")
            handle.write(f"count={len(resolved['targets'])}\n")
            handle.write(f"max_parallel={int(policy.get('max_parallel', 8))}\n")

    print(f"resolved {len(resolved['targets'])} targets in {len(chunks)} chunks; skipped {len(resolved['skipped'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
