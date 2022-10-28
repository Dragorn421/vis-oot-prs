import sys
from pathlib import Path

print(sys.argv)

runner_temp_dir = Path(sys.argv[1])

with (runner_temp_dir / "index.html").open("w") as f:
    f.write("Hello from python")
