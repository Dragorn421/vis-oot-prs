import base64
import argparse
from pathlib import Path

from . import data
from . import graph

parser = argparse.ArgumentParser()
parser.add_argument("--out")
parser.add_argument("--token")
parser.add_argument("--cache", action="store_true")
args = parser.parse_args()

out_dir = Path(args.out)

print("download_pr_list...")
if args.cache:
    prs = data.get_cached_pr_list(args.token, "zeldaret/oot")
else:
    prs = data.download_pr_list(args.token, "zeldaret/oot")
print("download_pr_list OK")

gp = graph.GraphParams.if_label_contains("Needs contributor")
print("make_graph...")
g, gkey = graph.make_graph(prs, gp)
print("make_graph OK")

with (out_dir / "index.html").open("w") as f:
    f.write("Hello from python")

    f.write(
        ""  #    """<script src="https://cdnjs.cloudflare.com/ajax/libs/d3-graphviz/4.4.0/d3-graphviz.min.js" integrity="sha512-T6HYgCVKXsFOabAI/rq1eNK4ATO2u3ziaOuPGLrHNf11UBROtR4f3fOKrZzyej79DuttNbW80U/XMcQ+u09NQg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>"""
    )

    f.write(
        """
<script src="//d3js.org/d3.v5.min.js"></script>
<script src="https://unpkg.com/@hpcc-js/wasm@0.3.11/dist/index.min.js"></script>
<script src="https://unpkg.com/d3-graphviz@3.0.5/build/d3-graphviz.js"></script>
<div id="graph" style="text-align: center;"></div>
<script>

d3.select("#graph").graphviz()
    .renderDot(atob('"""
        + base64.encodebytes(g.source.encode()).decode().replace("\n", "").replace("\r", "")
        + """'));

</script>
    """
    )

print(__file__, "OK")
