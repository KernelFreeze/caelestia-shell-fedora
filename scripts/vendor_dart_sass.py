#!/usr/bin/env python3
"""Create the offline Dart pub cache used to build the dart-sass RPM."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path


USER_AGENT = "caelestia-fedora-dart-sass-vendor"
VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?")


def latest_version() -> str:
    request = urllib.request.Request(
        "https://api.github.com/repos/sass/dart-sass/releases/latest",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        version = json.loads(response.read().decode("utf-8"))["tag_name"]
    return validate_version(version)


def validate_version(version: str) -> str:
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"unsupported Dart Sass version: {version!r}")
    return version


def download_source(version: str, destination: Path) -> None:
    url = (
        "https://github.com/sass/dart-sass/"
        f"archive/{version}/dart-sass-{version}.tar.gz"
    )
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        with destination.open("wb") as output:
            shutil.copyfileobj(response, output)


def run(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    subprocess.run(command, cwd=cwd, env=env, check=True)


def vendor_pub_cache(version: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="dart-sass-") as temporary_dir:
        temporary = Path(temporary_dir)
        archive = temporary / f"dart-sass-{version}.tar.gz"
        download_source(version, archive)
        run(
            ["tar", "-xzf", str(archive), "-C", str(temporary)],
            cwd=temporary,
            env=os.environ.copy(),
        )

        source = temporary / f"dart-sass-{version}"
        pub_cache = temporary / "pub-cache"
        environment = os.environ.copy()
        environment["PUB_CACHE"] = str(pub_cache)
        run(["dart", "pub", "get"], cwd=source, env=environment)

        run(
            [
                "tar",
                "-czf",
                str(output),
                "-C",
                str(temporary),
                "pub-cache",
            ],
            cwd=temporary,
            env=os.environ.copy(),
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        help="Dart Sass release to vendor (defaults to the latest release)",
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    version = validate_version(args.version) if args.version else latest_version()
    vendor_pub_cache(version, args.output)
    print(f"Created {args.output} for dart-sass {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
