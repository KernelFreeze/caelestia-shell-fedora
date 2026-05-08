#!/usr/bin/env python3
"""Check RPM specs for upstream updates and optionally open a PR."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "caelestia-fedora-spec-updater"
DEFAULT_BRANCH = "automation/update-specs"


@dataclasses.dataclass(frozen=True)
class FieldCheck:
    field: str
    getter: Callable[[str | None], str]
    kind: str = "header"
    reset_release: bool = False


@dataclasses.dataclass(frozen=True)
class SnapshotCheck:
    repo: str
    path: str
    commit_macro: str = "commit"
    snapdate_macro: str = "snapdate"
    reset_release: bool = True


@dataclasses.dataclass(frozen=True)
class SpecTarget:
    spec: str
    fields: tuple[FieldCheck, ...] = ()
    snapshot: SnapshotCheck | None = None
    validate_sources: bool = True


@dataclasses.dataclass(frozen=True)
class Change:
    spec: str
    field: str
    old: str
    new: str


@dataclasses.dataclass(frozen=True)
class SkippedUpdate:
    spec: str
    reason: str


def github_api(path: str, token: str | None = None) -> Any:
    return fetch_json(f"https://api.github.com{path}", token=token)


def fetch_json(url: str, token: str | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
    }
    if token and urllib.parse.urlparse(url).netloc == "api.github.com":
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def latest_github_release(repo: str, strip_prefix: str = "v") -> Callable[[str | None], str]:
    def getter(token: str | None) -> str:
        release = github_api(f"/repos/{repo}/releases/latest", token=token)
        tag = release["tag_name"]
        return strip_once(tag, strip_prefix)

    return getter


def latest_github_tag(repo: str, prefix: str) -> Callable[[str | None], str]:
    def getter(token: str | None) -> str:
        for page in range(1, 6):
            tags = github_api(
                f"/repos/{repo}/tags?per_page=100&page={page}",
                token=token,
            )
            if not tags:
                break
            for tag in tags:
                name = tag["name"]
                if name.startswith(prefix):
                    return name[len(prefix) :]
        raise RuntimeError(f"no GitHub tag with prefix {prefix!r} found in {repo}")

    return getter


def latest_pypi_version(project: str) -> Callable[[str | None], str]:
    def getter(_token: str | None) -> str:
        data = fetch_json(f"https://pypi.org/pypi/{project}/json")
        return data["info"]["version"]

    return getter


def latest_dart_stable(_token: str | None) -> str:
    data = fetch_json(
        "https://storage.googleapis.com/dart-archive/channels/stable/release/latest/VERSION"
    )
    return data["version"]


TARGETS: tuple[SpecTarget, ...] = (
    SpecTarget(
        "caelestia-shell.spec",
        fields=(
            FieldCheck(
                "Version",
                latest_github_release("caelestia-dots/shell"),
                reset_release=True,
            ),
        ),
    ),
    SpecTarget(
        "caelestia-cli.spec",
        fields=(
            FieldCheck(
                "Version",
                latest_github_release("caelestia-dots/cli"),
                reset_release=True,
            ),
        ),
    ),
    SpecTarget(
        "cliphist.spec",
        fields=(
            FieldCheck(
                "Version",
                latest_github_release("sentriz/cliphist"),
                reset_release=True,
            ),
        ),
    ),
    SpecTarget(
        "cascadia-code-nerd-fonts.spec",
        fields=(
            FieldCheck(
                "Version",
                latest_github_release("ryanoasis/nerd-fonts"),
                reset_release=True,
            ),
        ),
    ),
    SpecTarget(
        "dart.spec",
        fields=(FieldCheck("Version", latest_dart_stable, reset_release=True),),
    ),
    SpecTarget(
        "dart-sass.spec",
        fields=(
            FieldCheck(
                "_sass_version",
                latest_github_tag("sass/sass", "embedded-protocol-"),
                kind="macro",
            ),
            FieldCheck(
                "_buf_version",
                latest_github_release("bufbuild/buf"),
                kind="macro",
            ),
            FieldCheck(
                "Version",
                latest_github_release("sass/dart-sass", strip_prefix="v"),
                reset_release=True,
            ),
        ),
    ),
    SpecTarget(
        "material-symbols-fonts.spec",
        snapshot=SnapshotCheck(
            repo="google/material-design-icons",
            path="variablefont",
        ),
    ),
    SpecTarget(
        "python3-materialyoucolor.spec",
        fields=(
            FieldCheck(
                "Version",
                latest_pypi_version("materialyoucolor"),
                reset_release=True,
            ),
        ),
    ),
    SpecTarget(
        "rubik-fonts.spec",
        snapshot=SnapshotCheck(
            repo="google/fonts",
            path="ofl/rubik",
        ),
    ),
)


def strip_once(value: str, prefix: str) -> str:
    if prefix and value.startswith(prefix):
        return value[len(prefix) :]
    return value


def read_field(text: str, name: str, kind: str) -> str:
    if kind == "header":
        pattern = rf"^{re.escape(name)}:\s*(\S+)"
    elif kind == "macro":
        pattern = rf"^%global\s+{re.escape(name)}\s+(\S+)"
    else:
        raise ValueError(f"unknown field kind {kind!r}")

    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"could not find {kind} field {name!r}")
    return match.group(1)


def replace_field(text: str, name: str, kind: str, value: str) -> str:
    if kind == "header":
        pattern = rf"^({re.escape(name)}:\s*)\S+(.*)$"
    elif kind == "macro":
        pattern = rf"^(%global\s+{re.escape(name)}\s+)\S+(.*)$"
    else:
        raise ValueError(f"unknown field kind {kind!r}")

    updated, count = re.subn(
        pattern,
        rf"\g<1>{value}\2",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise RuntimeError(f"could not replace {kind} field {name!r}")
    return updated


def reset_release(text: str) -> str:
    current = read_field(text, "Release", "header")
    if current == "%autorelease" or current == "1%{?dist}":
        return text
    return replace_field(text, "Release", "header", "1%{?dist}")


def version_tokens(value: str) -> list[int | str]:
    value = strip_once(value.strip(), "v")
    return [
        int(token) if token.isdigit() else token.lower()
        for token in re.findall(r"\d+|[A-Za-z]+", value)
    ]


def compare_versions(left: str, right: str) -> int | None:
    left_tokens = version_tokens(left)
    right_tokens = version_tokens(right)
    if not left_tokens or not right_tokens:
        return None

    max_len = max(len(left_tokens), len(right_tokens))
    for index in range(max_len):
        left_value = left_tokens[index] if index < len(left_tokens) else 0
        right_value = right_tokens[index] if index < len(right_tokens) else 0
        if left_value == right_value:
            continue
        if isinstance(left_value, int) and isinstance(right_value, int):
            return 1 if left_value > right_value else -1
        if isinstance(left_value, int):
            return 1
        if isinstance(right_value, int):
            return -1
        return 1 if left_value > right_value else -1
    return 0


def should_update(current: str, latest: str) -> bool:
    if current == latest:
        return False
    comparison = compare_versions(latest, current)
    return comparison is None or comparison > 0


def latest_commit_for_path(
    repo: str,
    path: str,
    token: str | None,
) -> tuple[str, str]:
    query = urllib.parse.urlencode({"path": path, "per_page": "1"})
    commits = github_api(f"/repos/{repo}/commits?{query}", token=token)
    if not commits:
        raise RuntimeError(f"no commits found for {repo}:{path}")

    commit = commits[0]
    timestamp = (
        commit.get("commit", {})
        .get("committer", {})
        .get("date")
        or commit.get("commit", {}).get("author", {}).get("date")
    )
    if not timestamp:
        raise RuntimeError(f"latest commit for {repo}:{path} has no timestamp")

    snapdate = dt.datetime.fromisoformat(
        timestamp.replace("Z", "+00:00")
    ).strftime("%Y%m%d")
    return commit["sha"], snapdate


def should_update_snapshot(
    current_commit: str,
    current_snapdate: str,
    latest_commit: str,
    latest_snapdate: str,
) -> bool:
    if current_commit == latest_commit:
        return False
    if latest_snapdate < current_snapdate:
        return False
    return True


def apply_target(
    target: SpecTarget,
    token: str | None,
    validate_sources: bool,
) -> tuple[list[Change], SkippedUpdate | None]:
    path = ROOT / target.spec
    original = path.read_text(encoding="utf-8")
    updated = original
    changes: list[Change] = []
    release_needs_reset = False

    try:
        for field in target.fields:
            current = read_field(updated, field.field, field.kind)
            latest = field.getter(token)
            if should_update(current, latest):
                updated = replace_field(updated, field.field, field.kind, latest)
                changes.append(Change(target.spec, field.field, current, latest))
                release_needs_reset = release_needs_reset or field.reset_release

        if target.snapshot:
            current_commit = read_field(
                updated,
                target.snapshot.commit_macro,
                "macro",
            )
            current_snapdate = read_field(
                updated,
                target.snapshot.snapdate_macro,
                "macro",
            )
            latest_commit, latest_snapdate = latest_commit_for_path(
                target.snapshot.repo,
                target.snapshot.path,
                token,
            )
            if should_update_snapshot(
                current_commit,
                current_snapdate,
                latest_commit,
                latest_snapdate,
            ):
                updated = replace_field(
                    updated,
                    target.snapshot.commit_macro,
                    "macro",
                    latest_commit,
                )
                updated = replace_field(
                    updated,
                    target.snapshot.snapdate_macro,
                    "macro",
                    latest_snapdate,
                )
                changes.append(
                    Change(
                        target.spec,
                        target.snapshot.commit_macro,
                        current_commit[:12],
                        latest_commit[:12],
                    )
                )
                if current_snapdate != latest_snapdate:
                    changes.append(
                        Change(
                            target.spec,
                            target.snapshot.snapdate_macro,
                            current_snapdate,
                            latest_snapdate,
                        )
                    )
                release_needs_reset = release_needs_reset or target.snapshot.reset_release

        if not changes:
            return [], None

        if release_needs_reset:
            updated = reset_release(updated)

        if validate_sources and target.validate_sources:
            missing = missing_source_urls(updated)
            if missing:
                urls = ", ".join(missing[:3])
                suffix = "" if len(missing) <= 3 else f", and {len(missing) - 3} more"
                return [], SkippedUpdate(
                    target.spec,
                    f"updated source URL did not resolve: {urls}{suffix}",
                )

        path.write_text(updated, encoding="utf-8")
        return changes, None
    except Exception as exc:
        return [], SkippedUpdate(target.spec, str(exc))


def rpm_macros(text: str) -> dict[str, str]:
    macros: dict[str, str] = {}
    for match in re.finditer(r"^%global\s+(\S+)\s+(\S+)", text, flags=re.MULTILINE):
        macros[match.group(1)] = match.group(2)

    for header in ("Name", "Version", "URL"):
        try:
            value = read_field(text, header, "header")
        except RuntimeError:
            continue
        macros[header.lower()] = value
    return macros


def expand_macros(value: str, macros: dict[str, str]) -> str:
    expanded = value
    for _ in range(8):
        previous = expanded
        for name, macro_value in macros.items():
            expanded = expanded.replace(f"%{{{name}}}", macro_value)
        if expanded == previous:
            break
    return expanded.replace("%%", "%")


def source_urls(text: str) -> list[str]:
    macros = rpm_macros(text)
    urls: list[str] = []
    for match in re.finditer(r"^Source\d*:\s*(\S+)", text, flags=re.MULTILINE):
        value = expand_macros(match.group(1), macros)
        if value.startswith("%{pypi_source"):
            continue
        if "%{" in value:
            continue
        if not value.startswith(("http://", "https://")):
            continue
        urls.append(urllib.parse.urldefrag(value)[0])
    return urls


def missing_source_urls(text: str) -> list[str]:
    missing: list[str] = []
    for url in source_urls(text):
        if not url_exists(url):
            missing.append(url)
    return missing


def url_exists(url: str) -> bool:
    headers = {"User-Agent": USER_AGENT}
    request = urllib.request.Request(url, headers=headers, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return 200 <= response.status < 400
    except urllib.error.HTTPError as exc:
        if exc.code not in {403, 405}:
            return False

    request = urllib.request.Request(
        url,
        headers={**headers, "Range": "bytes=0-0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return 200 <= response.status < 400
    except urllib.error.URLError:
        return False


def update_specs(
    token: str | None,
    dry_run: bool,
    validate_sources: bool,
) -> tuple[list[Change], list[SkippedUpdate]]:
    changes: list[Change] = []
    skipped: list[SkippedUpdate] = []

    for target in TARGETS:
        target_changes, target_skipped = apply_target(
            target,
            token=token,
            validate_sources=validate_sources,
        )
        changes.extend(target_changes)
        if target_skipped:
            skipped.append(target_skipped)

    if dry_run and changes:
        run(["git", "restore", "--worktree", "--", *sorted({c.spec for c in changes})])

    return changes, skipped


def run(
    command: list[str],
    *,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def git_output(command: list[str]) -> str:
    return run(command, capture=True).stdout.strip()


def ensure_clean_worktree() -> None:
    status = git_output(["git", "status", "--porcelain"])
    if status:
        raise RuntimeError("worktree must be clean before creating a PR")


def configure_git_author() -> None:
    run(["git", "config", "user.name", "github-actions[bot]"])
    run(
        [
            "git",
            "config",
            "user.email",
            "41898282+github-actions[bot]@users.noreply.github.com",
        ]
    )


def create_or_update_pr(
    changes: list[Change],
    skipped: list[SkippedUpdate],
    branch: str,
    base: str,
    token: str,
) -> str:
    configure_git_author()
    run(["git", "switch", "-C", branch])
    run(["git", "add", *sorted({change.spec for change in changes})])
    run(["git", "commit", "-m", "chore: update package specs"])
    run(
        [
            "git",
            "fetch",
            "origin",
            f"+refs/heads/{branch}:refs/remotes/origin/{branch}",
        ],
        check=False,
    )
    run(["git", "push", "--force-with-lease", "origin", f"HEAD:refs/heads/{branch}"])

    repository = github_repository()
    title = "chore: update package specs"
    body = pr_body(changes, skipped)
    url = ensure_pull_request(repository, branch, base, title, body, token)
    return url


def github_repository() -> str:
    repository = os.environ.get("GITHUB_REPOSITORY")
    if repository:
        return repository

    remote = git_output(["git", "remote", "get-url", "origin"])
    match = re.search(r"github\.com[:/]([^/]+/[^/.]+)(?:\.git)?$", remote)
    if not match:
        raise RuntimeError("could not infer GitHub repository from origin remote")
    return match.group(1)


def ensure_pull_request(
    repository: str,
    branch: str,
    base: str,
    title: str,
    body: str,
    token: str,
) -> str:
    owner = repository.split("/", 1)[0]
    query = urllib.parse.urlencode(
        {
            "state": "open",
            "head": f"{owner}:{branch}",
            "base": base,
        }
    )
    pulls = github_api(f"/repos/{repository}/pulls?{query}", token=token)
    if pulls:
        number = pulls[0]["number"]
        pull = github_request(
            "PATCH",
            f"/repos/{repository}/pulls/{number}",
            token,
            {"title": title, "body": body},
        )
        return pull["html_url"]

    pull = github_request(
        "POST",
        f"/repos/{repository}/pulls",
        token,
        {
            "title": title,
            "head": branch,
            "base": base,
            "body": body,
            "maintainer_can_modify": True,
        },
    )
    return pull["html_url"]


def github_request(method: str, path: str, token: str, payload: dict[str, Any]) -> Any:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def pr_body(changes: list[Change], skipped: list[SkippedUpdate]) -> str:
    lines = [
        "Automated RPM spec update.",
        "",
        "Updates:",
    ]
    lines.extend(
        f"- `{change.spec}`: `{change.field}` `{change.old}` -> `{change.new}`"
        for change in changes
    )
    if skipped:
        lines.extend(["", "Skipped:"])
        lines.extend(f"- `{item.spec}`: {item.reason}" for item in skipped)
    lines.extend(["", "Generated by `scripts/update_specs.py`."])
    return "\n".join(lines)


def print_summary(changes: list[Change], skipped: list[SkippedUpdate]) -> None:
    if changes:
        print("Updates:")
        for change in changes:
            print(f"- {change.spec}: {change.field} {change.old} -> {change.new}")
    else:
        print("No spec updates found.")

    if skipped:
        print("")
        print("Skipped:")
        for item in skipped:
            print(f"- {item.spec}: {item.reason}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--create-pr",
        action="store_true",
        help="commit updates, push an automation branch, and open or update a PR",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print available updates without leaving edits in the worktree",
    )
    parser.add_argument(
        "--branch",
        default=DEFAULT_BRANCH,
        help=f"branch to push when creating a PR (default: {DEFAULT_BRANCH})",
    )
    parser.add_argument(
        "--base",
        default=os.environ.get("GITHUB_REF_NAME", "main"),
        help="base branch for the PR (default: GITHUB_REF_NAME or main)",
    )
    parser.add_argument(
        "--no-validate-sources",
        action="store_true",
        help="do not verify expanded Source URLs before writing updates",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.create_pr and args.dry_run:
        raise SystemExit("--create-pr and --dry-run cannot be used together")

    token = os.environ.get("GITHUB_TOKEN")
    if args.create_pr:
        ensure_clean_worktree()
        if not token:
            raise SystemExit("GITHUB_TOKEN is required with --create-pr")

    changes, skipped = update_specs(
        token=token,
        dry_run=args.dry_run,
        validate_sources=not args.no_validate_sources,
    )
    print_summary(changes, skipped)

    if args.create_pr and changes:
        pr_url = create_or_update_pr(
            changes,
            skipped,
            branch=args.branch,
            base=args.base,
            token=token,
        )
        print("")
        print(f"Pull request: {pr_url}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP error {exc.code}: {detail}", file=sys.stderr)
        raise SystemExit(1)
