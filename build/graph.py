from dataclasses import dataclass
import html
from typing import Any, Callable

import graphviz

from .data import PR, User, Label


@dataclass
class GraphParams:
    pr_node_style: str = "none"  # wedged, sober, none

    get_show_pr: Callable[[PR], bool] = lambda pr: True
    get_show_label: Callable[[PR, Label], bool] = lambda pr, label: True
    get_show_label_links: Callable[[Label], bool] = lambda label: False
    get_show_approval: Callable[[PR, User], bool] = lambda pr, user: True

    show_labels: bool = False
    show_authors: bool = True
    show_approvals: bool = True

    @staticmethod
    def if_label_contains(label_name_frag):
        def get_show_pr(pr: PR):
            return any(label_name_frag in label.name for label in pr.labels)

        def get_show_label_links(label: Label):
            return label_name_frag in label.name

        return GraphParams(
            pr_node_style="sober",
            get_show_pr=get_show_pr,
            get_show_label_links=get_show_label_links,
            show_labels=True,
        )


def make_graph(prs: list[PR], gp: GraphParams):

    prs = [
        PR(
            pr.id,
            pr.name,
            pr.author,
            frozenset(label for label in pr.labels if gp.get_show_label(pr, label)),
            frozenset(
                user for user in pr.approved_by if gp.get_show_approval(pr, user)
            ),
        )
        for pr in prs
        if gp.get_show_pr(pr)
    ]

    g = graphviz.Digraph()
    gkey = graphviz.Digraph()

    nodes: dict[Any, str] = dict()

    labels: set[Label] = set()

    for pr in prs:
        for label in pr.labels:
            labels.add(label)

    for label in labels:
        if gp.show_labels:
            if gp.get_show_label_links(label):
                nodes[label] = f"Label {label.name}"
                g.node(
                    nodes[label],
                    label.name,
                    style="filled",
                    fillcolor=label.color,
                )

        gkey.node(
            f"Label {label.name}",
            label.name,
            style="filled",
            fillcolor=label.color,
        )

    users: set[User] = set()

    for pr in prs:
        if gp.show_authors:
            users.add(pr.author)
        if gp.show_approvals:
            for user in pr.approved_by:
                users.add(user)

    for user in users:
        nodes[user] = f"User {user.login}"
        g.node(
            nodes[user],
            user.login,
            style="filled",
            fillcolor="lightgray",
            # fontsize="300",
        )

    def word_wrap(s: str, minLen=10, maxLen=20, out_html=False):
        parts = [[]]

        for w in s.split(" "):
            if (
                len(" ".join(parts[-1])) < minLen
                or len(" ".join((*parts[-1], w))) <= maxLen
            ):
                parts[-1].append(w)
            else:
                parts.append([w])

        for i in range(len(parts) - 1):
            ws1 = parts[i]
            ws2 = parts[i + 1]
            if len(" ".join(ws1)) > len(" ".join(ws2)):
                while len(" ".join(ws1[:-1])) > len(" ".join((ws1[-1], *ws2))):
                    ws2.insert(0, ws1.pop())
            else:
                while len(" ".join((*ws1, ws2[0]))) < len(" ".join(ws2[1:])):
                    ws1.append(ws2.pop(0))

        if out_html:
            return "<br/>".join(html.escape(" ".join(ws)) for ws in parts)
        else:
            return "\\n".join(" ".join(ws) for ws in parts)

    for pr in prs:
        nodes[pr] = f"PR {pr.id}"
        attrs = dict()

        attrs.update(
            dict(
                href=f"https://github.com/zeldaret/oot/pull/{pr.id}",
            )
        )

        if gp.pr_node_style == "wedged":
            if len(pr.labels) == 0:
                pass
            elif len(pr.labels) == 1:
                attrs.update(
                    dict(
                        style="filled",
                        fillcolor=list(pr.labels)[0].color,
                    )
                )
            else:
                attrs.update(
                    dict(
                        style="wedged",
                        fillcolor=":".join(label.color for label in pr.labels),
                    )
                )
            g.node(
                nodes[pr],
                f"#{pr.id}\\n{word_wrap(pr.name)}",
                **attrs,
            )
        elif gp.pr_node_style == "sober":
            g.node(
                nodes[pr],
                "<"
                + "".join(
                    (
                        "<table border='0'>",
                        "<tr><td>",
                        *(
                            html.escape(f"#{pr.id}"),
                            "<br/>",
                            word_wrap(pr.name, out_html=True),
                        ),
                        "</td></tr>",
                        "<tr><td>",
                        *(
                            (
                                "<table border='0' cellpadding='0' cellspacing='0'"
                                f" fixedsize='true' width='{50 * len(pr.labels)}' height='20'><tr>",
                                "".join(
                                    f"<td bgcolor='{label.color}' border='1'"
                                    " fixedsize='true' width='50' height='20'></td>"
                                    for label in pr.labels
                                ),
                                "</tr></table>",
                            )
                            if pr.labels
                            else ()
                        ),
                        "</td></tr>",
                        "</table>",
                    )
                )
                + ">",
                style="filled",
                fillcolor="beige",
                **attrs,
            )
        elif gp.pr_node_style == "none":
            g.node(
                nodes[pr],
                f"#{pr.id}\\n{word_wrap(pr.name)}",
                **attrs,
            )
        else:
            assert False, gp.pr_node_style

        for label in pr.labels:
            if gp.show_labels:
                if gp.get_show_label_links(label):
                    g.edge(
                        nodes[label],
                        nodes[pr],
                        color=label.color,
                    )

        if gp.show_authors:
            g.edge(
                nodes[pr.author],
                nodes[pr],
                color="purple",
            )

        for user in pr.approved_by:
            if gp.show_approvals:
                g.edge(
                    nodes[pr],
                    nodes[user],
                    color="darkgreen",
                )

    if gp.show_authors:
        gkey.node("PR 1", "PR")
        gkey.node("User 1", "User", style="filled", fillcolor="lightgray")
        gkey.edge("User 1", "PR 1", label="Opened By", color="purple")

    if gp.show_approvals:
        gkey.node("PR 2", "PR")
        gkey.node("User 2", "User", style="filled", fillcolor="lightgray")
        gkey.edge("PR 2", "User 2", label="Approved", color="darkgreen")

    return g, gkey
