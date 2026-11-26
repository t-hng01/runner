import base64
import hashlib
import re
import os
import shutil
import stat
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

v1 = int(os.environ.get("V7", "360"))
v2 = 420
v3 = 512
v4 = 50
v5 = 6000
v6 = 1000000
v7 = "256m"
v8 = Path(__file__).resolve().parent
v9 = v8 / "lua_host.py"
v10 = {
    "python": shutil.which("python3") or sys.executable,
    "node": shutil.which("node"),
    "java": shutil.which("java"),
    "lune": shutil.which("lune"),
    "typescript": shutil.which("tsx"),
    "c": shutil.which("gcc"),
    "cpp": shutil.which("g++"),
    "go": shutil.which("go"),
    "bash": shutil.which("bash"),
    "php": shutil.which("php"),
}
v11 = ""
v12 = ("python", "node", "java", "lune", "lua", "typescript", "c", "cpp", "go", "bash", "php")
v50 = 65534
v60 = 5 * 1024 * 1024
v61 = 8 * 1024 * 1024
v62 = 10
v13 = {"python": "main.py", "node": "main.js", "java": "main.java", "lune": "main.luau", "lua": "main.lua",
       "typescript": "main.ts", "c": "main.c", "cpp": "main.cpp", "go": "main.go", "bash": "main.sh", "php": "main.php"}


def v14(v19):
    if len(v19) <= v5:
        return v19
    v20 = v5 * 2 // 3
    return v19[:v20] + f"\n...[cat {len(v19) - v5} ky tu]...\n" + v19[-(v5 - v20):]


def v15(v21):
    if v21 == "lua":
        if not v11:
            return None
        return [sys.executable, str(v9), v13[v21]]
    if v21 == "typescript":
        v81 = v10.get("typescript")
        if v81:
            return [v81, v13[v21]]
        v82 = v10.get("node")
        if v82 and v87():
            return [v82, "--no-warnings", "--experimental-strip-types", v13[v21]]
        return None
    v22 = v10.get(v21)
    if not v22:
        return None
    if v21 == "python":
        return [v22, "-B", v13[v21]]
    if v21 == "node":
        return [v22, v13[v21]]
    if v21 == "java":
        return [v22, f"-Xmx{v7}", "-XX:+UseSerialGC", "-XX:TieredStopAtLevel=1", "-cp", "/opt/javalibs/*", v13[v21]]
    if v21 == "lune":
        return [v22, "run", v13[v21]]
    if v21 == "c":
        return ["sh", "-c", f"{v22} -O2 -o main main.c -lm && ./main"]
    if v21 == "cpp":
        return ["sh", "-c", f"{v22} -O2 -std=c++17 -o main main.cpp -lm && ./main"]
    if v21 == "go":
        return [v22, "run", v13[v21]]
    if v21 == "bash":
        return [v22, v13[v21]]
    if v21 == "php":
        return [v22, v13[v21]]
    return None


def v91(v92, v93):
    v94 = {}
    if not isinstance(v93, list):
        return v94
    v95 = 0
    for v96 in v93[:20]:
        try:
            v97 = str(v96.get("path", ""))
            if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9._\-/]{0,119}", v97) or ".." in v97.split("/") or v97.endswith("/"):
                continue
            v98 = base64.b64decode(v96.get("b64", ""))
            if v95 + len(v98) > v61:
                continue
            v99 = v92 / v97
            v99.parent.mkdir(parents=True, exist_ok=True)
            v99.write_bytes(v98)
            if os.geteuid() == 0:
                for v100 in (v99, *[p for p in v99.parents if p != v92.parent and str(p).startswith(str(v92))]):
                    os.chown(v100, v50, v50)
            v95 += len(v98)
            v94[v97] = hashlib.sha256(v98).hexdigest()
        except Exception:
            continue
    return v94


def v63(v64, v65, v101=None):
    v66 = []
    v67 = 0
    for v68, v69, v70 in os.walk(v64):
        v69[:] = [v71 for v71 in v69 if not v71.startswith(".") and v71 not in ("node_modules", "__pycache__")]
        for v72 in sorted(v70):
            if v72.startswith(".") or len(v66) >= v62:
                continue
            v73 = os.path.join(v68, v72)
            v74 = os.path.relpath(v73, v64)
            if v74 in v65:
                continue
            try:
                v75 = os.open(v73, os.O_RDONLY | os.O_NOFOLLOW)
            except OSError:
                continue
            try:
                v76 = os.fstat(v75)
                if not stat.S_ISREG(v76.st_mode) or v76.st_nlink > 1 or v76.st_size > v60 or v67 + v76.st_size > v61:
                    continue
                if os.geteuid() == 0 and v76.st_uid != v50:
                    continue
                v77 = b""
                while len(v77) < v76.st_size:
                    v78 = os.read(v75, 1 << 20)
                    if not v78:
                        break
                    v77 += v78
            except OSError:
                continue
            finally:
                os.close(v75)
            if v101 and v101.get(v74.replace(os.sep, "/")) == hashlib.sha256(v77).hexdigest():
                continue
            v67 += len(v77)
            v66.append({"path": v74.replace(os.sep, "/"), "b64": base64.b64encode(v77).decode()})
    return v66


def v87():
    v83 = v10.get("typescript")
    if v83:
        return True
    v84 = v10.get("node")
    if not v84:
        return False
    try:
        v85 = subprocess.run([v84, "--version"], capture_output=True, text=True, timeout=10).stdout.strip().lstrip("v")
        v86 = [int(x) for x in v85.split(".")[:2]]
        return v86 >= [22, 6]
    except Exception:
        return False


def v16(v23):
    return v15(v23) is not None


def v17(v24, v25, v26):
    try:
        while True:
            v27 = v24.read(65536)
            if not v27:
                break
            if len(v25) < v26:
                v25 += v27[: v26 - len(v25)]
    except Exception:
        pass


def v18(v28, v29, v30="", v102=None):
    if v28 not in v12:
        return {"ok": False, "error": "ngon ngu khong ho tro"}
    v31 = v15(v28)
    if v31 is None:
        return {"ok": False, "error": f"{v28} chua san sang, xem /health"}
    v32 = Path(tempfile.mkdtemp(prefix="run_"))
    try:
        os.chmod(v32, 0o700)
        v51 = os.geteuid() == 0
        if v51:
            os.chown(v32, v50, v50)
        v103 = v91(v32, v102)
        (v32 / v13[v28]).write_text(v29, encoding="utf-8")
        (v32 / ".luaurc").write_text('{"languageMode":"nonstrict","aliases":{"libs":"/opt/lualibs"}}')
        if os.geteuid() == 0:
            os.chown(v32 / v13[v28], v50, v50)
        v33 = [str(Path(v34).parent) for v34 in v10.values() if v34]
        v35 = {
            "PATH": ":".join(dict.fromkeys(v33 + ["/usr/local/bin", "/usr/bin", "/bin"])),
            "HOME": str(v32),
            "TMPDIR": str(v32),
            "LANG": "C.UTF-8",
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "TERM": "dumb",
            "GOROOT": str(Path(v10["go"]).resolve().parent.parent) if v10.get("go") else "/usr/local/go",
            "GOCACHE": str(v32 / ".gocache"),
            "GOPATH": str(v32 / ".gopath"),
            "GOTOOLCHAIN": "local",
            "GOFLAGS": "-buildvcs=false",
            "CGO_ENABLED": "0",
            "NODE_PATH": "/opt/nodelibs/node_modules",
        }
        if v11:
            v35["PYTHONPATH"] = v11
        v36 = v10.get("java")
        if v36:
            v35["JAVA_HOME"] = str(Path(v36).resolve().parent.parent)
        v37 = (
            "umask 077; "
            f"ulimit -t {v2} 2>/dev/null; "
            f"ulimit -u {v3} 2>/dev/null; "
            f"ulimit -f {v4 * 2048} 2>/dev/null; "
            f'exec timeout -k 2 {v1} "$@"'
        )
        v38 = ["env", "-i", *[f"{v39}={v40}" for v39, v40 in v35.items()], "sh", "-c", v37, "sandbox", *v31]
        v41 = time.perf_counter()
        v42 = subprocess.Popen(
            v38, cwd=str(v32), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            start_new_session=True,
            **({"user": v50, "group": v50, "extra_groups": []} if v51 else {}),
        )
        v43 = bytearray()
        v44 = threading.Thread(target=v17, args=(v42.stdout, v43, v6), daemon=True)
        v44.start()

        def v45():
            try:
                v42.stdin.write((v30 or "")[:100000].encode())
                v42.stdin.close()
            except Exception:
                pass

        threading.Thread(target=v45, daemon=True).start()
        v46 = False
        try:
            v42.wait(timeout=v1 + 8)
        except subprocess.TimeoutExpired:
            v46 = True
        try:
            os.killpg(v42.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        v42.wait()
        v44.join(timeout=2)
        v79 = v63(v32, {v13[v28], "main", ".luaurc"}, v103)
        v47 = v42.returncode
        if v47 == 124:
            v46 = True
        v48 = bytes(v43).decode("utf-8", "replace").replace(str(v32), "~")
        v80 = {
            "ok": v47 == 0 and not v46,
            "exit_code": v47,
            "timed_out": v46,
            "seconds": round(time.perf_counter() - v41, 2),
            "output": v14(v48) if v48 else ("(het gio, khong co output)" if v46 else "(khong co output)"),
        }
        if v79:
            v80["files"] = v79
        return v80
    finally:
        shutil.rmtree(v32, ignore_errors=True)
