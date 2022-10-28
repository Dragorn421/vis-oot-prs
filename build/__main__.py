# SPDX-License-Identifier: Unlicense

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
<style>
#load-in-progress {
    width: 90vw;
    font-size: 10vh;
}
@keyframes flashgently {
  from {
    background-color: silver;
  }
  to {
    background-color: slategray;
  }
}
@keyframes fadein {
  from {
    opacity: 0;
    height: 0;
  }
  to {
    opacity: 1;
    height: 90vh;
  }
}
.load-in-progress-loading {
    opacity: 0;
    height: 0;
    animation-delay: 0.5s, 0.3s;
    animation-duration: 1.1s, 0.6s;
    animation-name: flashgently, fadein;
    animation-fill-mode: none, forwards;
    animation-iteration-count: infinite, 1;
    animation-direction: alternate;
}
.load-in-progress-done {
    display: none;
}
</style>
</head>
<body style="background-color: silver;">
<div id="load-in-progress" class="load-in-progress-loading">Load in progress</div>
<span style="font-weight: bold;">State of OoT PRs, approvals-wise</span>
(see buttons and hints below)
- Currently showing: <span id="currently-showing"></span>
<div id="graph" style="display: inline-block; background-color: white; text-align: center;"></div>
"""
    )
    for var_name_base, msg in (
        ("g_needcontrib_authors", "Needs contributor approval (with authors)"),
        ("g_needcontrib_noauthors", "Needs contributor approval (without authors)"),
        ("g_needlead_authors", "Needs lead approval (with authors)"),
        ("g_needlead_noauthors", "Needs lead approval (without authors)"),
    ):
        f.write(
            f"""<button onclick="setgraphkind('{var_name_base}')">{html.escape(msg)}</button>"""
        )
    f.write(
        """
<label for="ignore-author">Ignore PRs by:</label>
<select id="ignore-author" onchange="set_ignore_author()">
<option value="">- nobody</option>
"""
    )

    authors = list(set(pr.author.login for pr in prs))

    for author in authors:
        f.write(f"""<option value="{author}">{author}</option>""")
    f.write(
        """
</select>
<div id="graph-key" style="display: inline-block; background-color: white; text-align: center;"></div>
<div><span style="font-weight: bold;">Hints:</span> PR nodes can be clicked.
- Click the buttons for viewing different graphs.
- The view can be panned by left clicking and zoomed by scrolling inside the white area.
- A new layout can be made by clicking the same button again.
- The small view above is the legend.
- The colored rectangles in PR nodes correspond to labels.
- There is a list to exclude PRs by one person.
</div>
"""
    )
    f.write(
        """
<script>
var visprsgraph_src = {
"""
    )
    for key, gp in (
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
        f.write(key + " : {\n")
        gmain, gkey = graph.make_graph(prs, gp)
        f.write(f"    '': [atob('{btoa(gmain.source)}'), atob('{btoa(gkey.source)}')],")
        get_show_pr_ini = gp.get_show_pr
        for author in authors:
            gp.get_show_pr = lambda pr: (
                pr.author.login != author and get_show_pr_ini(pr)
            )
            gmain, gkey = graph.make_graph(prs, gp)
            gp.get_show_pr = get_show_pr_ini
            f.write(
                f"    '{author}': [atob('{btoa(gmain.source)}'), atob('{btoa(gkey.source)}')],"
            )
        f.write("},\n")
    f.write("};\n")
    f.write(
        """
    var t = d3.transition()
        .duration(1000)
        .ease(d3.easeLinear);

    d3.select("#graph").graphviz()
        .engine("fdp")
        .width(window.innerWidth*0.9).height(window.innerHeight*0.75)
        .fit(true)
        .tweenPrecision("1%")
        .transition(t);

    d3.select("#graph-key").graphviz()
        .engine("dot")
        .width(window.innerWidth*0.9).height(window.innerHeight*0.1)
        .fit(true);

    function setrenderedgdot(gdot, gdotkey) {
        d3.select("#graph").graphviz().renderDot(gdot);
        d3.select("#graph-key").graphviz().renderDot(gdotkey);
    }
    function updaterenderedgdot() {
        var gpair = visprsgraph_src[window.visprsgraph_key][window.visprsgraph_ignoredauthorkey];
        var gdot = gpair[0];
        var gdotkey = gpair[1];
        setrenderedgdot(gdot, gdotkey);

        var curShowingText = "";
        if (window.visprsgraph_key == "g_needcontrib_noauthors"
         || window.visprsgraph_key == "g_needcontrib_authors")
            curShowingText += " PRs requiring approvals from contributors";
        if (window.visprsgraph_key == "g_needlead_noauthors"
         || window.visprsgraph_key == "g_needlead_authors")
            curShowingText += " PRs requiring approvals from leads";
        if (window.visprsgraph_ignoredauthorkey != "")
            curShowingText += " (ignoring PRs by " + window.visprsgraph_ignoredauthorkey + ")";
        if (window.visprsgraph_key == "g_needcontrib_noauthors"
         || window.visprsgraph_key == "g_needlead_noauthors")
            curShowingText += " (not showing authors of PRs)";
        else
            curShowingText += " (showing authors of PRs)";

        var curShowing = document.getElementById("currently-showing");
        curShowing.innerText = curShowingText;
    }
    function setgraphkind(key) {
        window.visprsgraph_key = key;
        updaterenderedgdot();
    }
    function set_ignore_author() {
        var selectElem = document.getElementById("ignore-author");
        window.visprsgraph_ignoredauthorkey = selectElem.value;
        updaterenderedgdot();
    }
    window.visprsgraph_key = "g_needcontrib_noauthors";
    set_ignore_author();
    """
    )
    f.write("""</script>"
<script>
function loadDone() {
    document.getElementById("load-in-progress")
        .classList.add("load-in-progress-done");
}
//setTimeout(loadDone, 100);
loadDone();
</script>
</body>""")

print(__file__, "OK")
