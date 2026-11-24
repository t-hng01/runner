import os
import shutil
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
    if v21 == "typescript":
        return [v22, v13[v21]]
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


def v18(v28, v29, v30=""):
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
            "GOROOT": "/usr/local/go",
            "GOCACHE": str(v32 / ".gocache"),
            "GOPATH": str(v32 / "go"),
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
        v47 = v42.returncode
        if v47 == 124:
            v46 = True
        v48 = bytes(v43).decode("utf-8", "replace").replace(str(v32), "~")
        return {
            "ok": v47 == 0 and not v46,
            "exit_code": v47,
            "timed_out": v46,
            "seconds": round(time.perf_counter() - v41, 2),
            "output": v14(v48) if v48 else ("(het gio, khong co output)" if v46 else "(khong co output)"),
        }
    finally:
        shutil.rmtree(v32, ignore_errors=True)
