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
<button onclick="setrenderedgdot(gvar1_main, gvar1_key)">Show authors as well</button>
<button onclick="setrenderedgdot(gvar2_main, gvar2_key)">Don't show authors</button>
<div id="graph-key" style="background-color: white; text-align: center; width: 90vw; height: 10vh;"></div>
"""
    )
    f.write("<script>\n")
    for var_name_base, gp in (
        (
            "gvar1",
            graph.GraphParams.if_label_contains("Needs contributor"),
        ),
        (
            "gvar2",
            graph.GraphParams.if_label_contains(
                "Needs contributor", show_authors=False
            ),
        ),
    ):
        gmain, gkey = graph.make_graph(prs, gp)
        for var_name, g in (
            (var_name_base + "_main", gmain),
            (var_name_base + "_key", gkey),
        ):
            f.write(
                var_name
                + " = atob('"
                + base64.encodebytes(g.source.encode())
                .decode()
                .replace("\n", "")
                .replace("\r", "")
                + "');\n"
            )
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
    setrenderedgdot(gvar2_main, gvar2_key);
    """
    )
    f.write("</script>\n</body>")

print(__file__, "OK")
