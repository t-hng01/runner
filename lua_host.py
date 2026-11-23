import sys

try:
    from lupa.lua54 import LuaRuntime
except Exception as v1:
    print(f"lupa/lua54 khong co: {v1}", file=sys.stderr)
    sys.exit(2)

v2 = r"""
python = nil
if package and package.loaded then package.loaded.python = nil end
io.open = nil; io.popen = nil; io.input = nil; io.output = nil; io.lines = nil; io.tmpfile = nil
os.execute = nil; os.remove = nil; os.rename = nil; os.tmpname = nil; os.getenv = nil; os.setlocale = nil
package = nil; require = nil; dofile = nil; loadfile = nil; debug = nil
"""

with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as v3:
    v4 = v3.read()

v5 = LuaRuntime(register_eval=False, register_builtins=False, unpack_returned_tuples=True)
try:
    v5.set_max_memory(256 * 1024 * 1024)
except Exception:
    pass
v5.execute(v2)
try:
    v5.execute(v4)
except Exception as v6:
    sys.stdout.flush()
    print(str(v6), file=sys.stderr)
    sys.exit(1)
sys.stdout.flush()
