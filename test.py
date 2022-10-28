import sys
from pathlib import Path

import github

print(sys.argv)

runner_temp_dir = Path(sys.argv[1])

g = github.Github(sys.argv[2])

with (runner_temp_dir / "index.html").open("w") as f:
    f.write("Hello from python")

    repo = g.get_repo("zeldaret/oot")
    f.write(repo.full_name)
    f.write(repo.description)
