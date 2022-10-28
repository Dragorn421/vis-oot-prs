from dataclasses import dataclass

from github import Github
import github.NamedUser
import github.Label


@dataclass(frozen=True)
class User:
    login: str


@dataclass(frozen=True)
class Label:
    name: str
    color: str


@dataclass(frozen=True)
class PR:
    id: int
    name: str
    author: User
    labels: frozenset[Label]
    approved_by: frozenset[User]


def download_pr_list(personal_access_token, repo):
    labels_cache = dict()

    def get_label(label: github.Label.Label):
        if label.name not in labels_cache:
            labels_cache[label.name] = Label(
                label.name,
                "#" + label.color,
            )
        return labels_cache[label.name]

    users_cache = dict()

    def get_user(user: github.NamedUser.NamedUser):
        if user.login not in users_cache:
            users_cache[user.login] = User(user.login)
        return users_cache[user.login]

    g = Github(personal_access_token)

    repo = g.get_repo(repo)

    prs: list[PR] = []

    for pr in repo.get_pulls():
        labels = set()

        for label in pr.labels:
            labels.add(get_label(label))

        approved_by = set()

        for review in pr.get_reviews():
            if review.state == "APPROVED":
                approved_by.add(get_user(review.user))

        prs.append(
            PR(
                pr.number,
                pr.title,
                get_user(pr.user),
                frozenset(labels),
                frozenset(approved_by),
            )
        )

    return prs
