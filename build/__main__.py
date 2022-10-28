import base64
import argparse
import html
from pathlib import Path

from . import data
from . import graph


def btoa(s: str):
    return base64.encodebytes(s.encode()).decode().replace("\n", "").replace("\r", "")


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

with (out_dir / "index.html").open("w") as f:
    f.write("<!-- Hello from python -->")

    f.write(
        """
<head>
<meta charset="utf-8">
<script src="https://d3js.org/d3.v5.min.js"></script>
<script src="https://unpkg.com/@hpcc-js/wasm@0.3.11/dist/index.min.js"></script>
<script src="https://unpkg.com/d3-graphviz@3.0.5/build/d3-graphviz.js"></script>
</head>
<body style="background-color: silver;">
<div id="graph" style="background-color: white; text-align: center; width: 90vw; height: 80vh;"></div>
"""
    )
    for var_name_base, msg in (
        ("g_needcontrib_authors", "Needs contributor approval (with authors)"),
        ("g_needcontrib_noauthors", "Needs contributor approval (without authors)"),
        ("g_needlead_authors", "Needs lead approval (with authors)"),
        ("g_needlead_noauthors", "Needs lead approval (without authors)"),
    ):
        f.write(
            f"""<button onclick="setrenderedgdot({var_name_base}_main, {var_name_base}_key)">{html.escape(msg)}</button>"""
        )
    f.write(
        """
<div id="graph-key" style="background-color: white; text-align: center; width: 90vw; height: 10vh;"></div>
<div>Hints: PR nodes can be clicked.
- Click the buttons for viewing different graphs.
- The view can be panned by left clicking and zoomed by scrolling inside the white area.
- Buttons can be clicked again to recompute the graph layout.
- The small view above is the legend.
- The colored rectangles in PR nodes correspond to labels.</div>
"""
    )
    f.write("<script>\n")
    for var_name_base, gp in (
        (
            "g_needcontrib_authors",
            graph.GraphParams.if_label_contains("Needs contributor"),
        ),
        (
            "g_needcontrib_noauthors",
            graph.GraphParams.if_label_contains(
                "Needs contributor", show_authors=False
            ),
        ),
        (
            "g_needlead_authors",
            graph.GraphParams.if_label_contains("Needs lead"),
        ),
        (
            "g_needlead_noauthors",
            graph.GraphParams.if_label_contains("Needs lead", show_authors=False),
        ),
    ):
        gmain, gkey = graph.make_graph(prs, gp)
        for var_name, g in (
            (var_name_base + "_main", gmain),
            (var_name_base + "_key", gkey),
        ):
            f.write(var_name + " = atob('" + btoa(g.source) + "');\n")
    f.write(
        """
    var t = d3.transition()
        .duration(1000)
        .ease(d3.easeLinear);

    var graphElem = document.getElementById("graph");
    d3.select("#graph").graphviz()
        .engine("fdp")
        .width(graphElem.clientWidth).height(graphElem.clientHeight)
        .fit(true)
        .tweenPrecision("1%")
        .transition(t);

    var graphElem = document.getElementById("graph-key");
    d3.select("#graph-key").graphviz()
        .engine("dot")
        .width(graphElem.clientWidth).height(graphElem.clientHeight)
        .fit(true);

    function setrenderedgdot(gdot, gdotkey) {
        d3.select("#graph").graphviz().renderDot(gdot);
        d3.select("#graph-key").graphviz().renderDot(gdotkey);
    }
    setrenderedgdot(g_needcontrib_noauthors_main, g_needcontrib_noauthors_key);
    """
    )
    f.write("</script>\n</body>")

print(__file__, "OK")
