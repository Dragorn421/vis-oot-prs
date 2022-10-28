import sys
from pathlib import Path

import github
import graphviz
import html

print(sys.argv)

runner_temp_dir = Path(sys.argv[1])

g = github.Github(sys.argv[2])

with (runner_temp_dir / "index.html").open("w") as f:
    f.write("Hello from python")

    repo = g.get_repo("zeldaret/oot")
    f.write(repo.full_name)
    f.write(repo.description)

    gr = graphviz.Digraph()

    f.write("<pre>" + html.escape(gr.source) + "</pre>")

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
    .renderDot('digraph  {a -> b}');

</script>
    """
    )
