import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import threading
import urllib.request
import zipfile
from pathlib import Path

import execute

v1 = Path(__file__).resolve().parent
v2 = v1 / "tools"
v3 = 600 * 1024 * 1024
v4 = {
    "python": "https://github.com/astral-sh/python-build-standalone/releases/download/20241206/"
              "cpython-3.12.8+20241206-x86_64-unknown-linux-gnu-install_only.tar.gz",
    "node": "https://nodejs.org/dist/v22.12.0/node-v22.12.0-linux-x64.tar.gz",
    "go": "https://go.dev/dl/go1.22.10.linux-amd64.tar.gz",
    "php": [f"https://dl.static-php.dev/static-php-cli/common/php-{x}-cli-linux-x86_64.tar.gz"
            for x in ("8.3.14", "8.3.13", "8.3.12", "8.3.11", "8.3.10", "8.3.9", "8.3.8", "8.2.26", "8.2.24", "8.2.23")],
    "java": "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.5%2B11/"
            "OpenJDK21U-jdk_x64_linux_hotspot_21.0.5_11.tar.gz",
    "lune": "https://github.com/lune-org/lune/releases/download/v0.10.5/lune-0.10.5-linux-x86_64.zip",
}
v5 = {"python": "python3", "node": "node", "java": "java", "lune": "lune", "go": "go", "php": "php"}
v6 = {}
v14 = {"python": "V3", "node": "V4", "java": "V5", "lune": "V6", "go": "V10", "php": "V11"}


def v7(v15):
    v16 = v5[v15]
    v17 = v2 / v15
    if not v17.is_dir():
        return None
    v18 = [f"**/bin/{v16}", f"**/{v16}"] if v15 != "lune" else [f"**/{v16}"]
    for v19 in v18:
        for v20 in v17.glob(v19):
            if v20.is_file():
                return v20
    return None


def v8(v21, v22):
    v23 = urllib.request.Request(v21, headers={"User-Agent": "runner/1.0"})
    v24 = 0
    with urllib.request.urlopen(v23, timeout=120) as v25, open(v22, "wb") as v26:
        while True:
            v27 = v25.read(1 << 20)
            if not v27:
                break
            v24 += len(v27)
            if v24 > v3:
                raise ValueError("file qua lon")
            v26.write(v27)


def v9(v28, v29, v30):
    v29.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(v28):
        with zipfile.ZipFile(v28) as v31:
            v32 = v29.resolve()
            for v33 in v31.namelist():
                if not str((v29 / v33).resolve()).startswith(str(v32)):
                    raise ValueError("archive nguy hiem")
            v31.extractall(v29)
    elif tarfile.is_tarfile(v28):
        with tarfile.open(v28) as v34:
            try:
                v34.extractall(v29, filter="data")
            except TypeError:
                v34.extractall(v29)
    else:
        (v29 / "bin").mkdir(exist_ok=True)
        shutil.move(str(v28), v29 / "bin" / v5[v30])
    subprocess.run(["chmod", "-R", "a+rX", str(v29)], check=False)
    v35 = v7(v30)
    if v35:
        os.chmod(v35, os.stat(v35).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def v10(v36):
    v6[v36] = "installing"
    try:
        v37 = os.environ.get(v14[v36], "").strip()
        v38 = v7(v36)
        if not v38 and not v37 and execute.v10.get(v36):
            v6[v36] = "ready"
            return
        if not v38:
            v39 = v37 or (v4.get(v36) if platform.machine() in ("x86_64", "AMD64") else "")
            v39 = v39 if isinstance(v39, list) else [v39]
            if not v39[0]:
                v6[v36] = f"failed: dat {v14[v36]} (khong co link mac dinh cho {platform.machine()})"
                return
            if not all(v48.startswith("https://") for v48 in v39):
                v6[v36] = "failed: link phai la https"
                return
            v2.mkdir(exist_ok=True)
            v40 = v2 / f"{v36}.download"
            v49 = None
            for v48 in v39:
                try:
                    v8(v48, v40)
                    v49 = None
                    break
                except Exception as v50:
                    v49 = v50
                    v40.unlink(missing_ok=True)
            if v49 is not None:
                raise v49
            v9(v40, v2 / v36, v36)
            v40.unlink(missing_ok=True)
            v38 = v7(v36)
        if not v38:
            v6[v36] = "failed: khong thay file chay sau khi giai nen"
            return
        execute.v10[v36] = str(v38)
        v6[v36] = "ready"
    except Exception as v41:
        shutil.rmtree(v2 / v36, ignore_errors=True)
        v6[v36] = f"failed: {type(v41).__name__}: {str(v41)[:80]}"


def v11():
    try:
        import lupa.lua54 as v42
        execute.v11 = str(Path(v42.__file__).resolve().parent.parent)
        return True
    except Exception:
        return False


def v12():
    v6["lua"] = "installing"
    if not v11():
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "lupa"],
                           timeout=300, check=False, capture_output=True)
        except Exception:
            pass
    v6["lua"] = "ready" if v11() else "failed: pip install lupa khong duoc"


def v13(v43):
    def v44():
        for v45 in ("python", "node", "lune", "java", "go", "php"):
            if v45 in v43:
                v10(v45)
        if "lua" in v43:
            v12()
        for v47 in ("c", "cpp", "bash"):
            if v47 in v43:
                v6[v47] = "ready" if execute.v10.get(v47) else "failed: chua cai"
        if "typescript" in v43:
            v6["typescript"] = "ready" if execute.v87() else "failed: can tsx hoac node>=22.6"
        print("runner:", v6, flush=True)

    for v46 in execute.v12:
        v6[v46] = "disabled" if v46 not in v43 else "pending"
    threading.Thread(target=v44, daemon=True).start()
