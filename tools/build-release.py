"""Build the isolated Python product with the source hash lock and no build-time network."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--work-dir", required=True, type=Path)
    parser.add_argument("--uv", default="uv")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    out, work = args.output.resolve(), args.work_dir.resolve()
    for path in (out, work):
        if path == source or source in path.parents:
            raise ValueError("build output and environment must be outside the source")
        path.mkdir(parents=True, exist_ok=False)
    env = {key: value for key, value in os.environ.items()
           if key.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT"}}
    for name in ("home", "temp", "cache"):
        (work / name).mkdir()
    env.update(HOME=str(work / "home"), USERPROFILE=str(work / "home"),
               TEMP=str(work / "temp"), TMP=str(work / "temp"),
               UV_CACHE_DIR=str(work / "cache"), UV_PYTHON_DOWNLOADS="never",
               UV_KEYRING_PROVIDER="disabled", PYTHONNOUSERSITE="1",
               SOURCE_DATE_EPOCH="1735689600")

    def run(*command):
        subprocess.run(command, cwd=source, env=env, check=True)

    venv = work / "venv"
    run(args.uv, "venv", "--no-config", "--python", args.python, str(venv))
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    run(args.uv, "pip", "sync", "--no-config", "--python", str(python),
        "--default-index", "https://pypi.org/simple", "--require-hashes", "--only-binary", ":all:",
        str(source / "requirements-build.txt"))
    run(args.uv, "build", "--no-config", "--python", str(python), "--offline",
        "--no-sources", "--no-build-isolation", "--out-dir", str(out), str(source))
    project = tomllib.loads((source / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    expected = {f"splrad_e08_product-{version}-py3-none-any.whl", f"splrad_e08_product-{version}.tar.gz"}
    if {p.name for p in out.iterdir()} != expected:
        raise ValueError("unexpected distribution set")
    evidence = {"scope": "local-build-only", "version": version,
                "buildLockSha256": hashlib.sha256((source / "requirements-build.txt").read_bytes()).hexdigest(),
                "artifacts": [{"name": p.name, "bytes": p.stat().st_size,
                               "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                              for p in sorted(out.iterdir())]}
    (work / "build-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
