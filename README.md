# vis-oot-prs

Visualize OoT PRs https://dragorn421.github.io/vis-oot-prs/

This helps seeing what's going on in the zeldaret/oot repo's PRs

This whole repo is licensed under the Unlicense, see LICENSE.

## How it works

(disclaimer: the code in `__main__.py` looks really bad)

how this works, basically:

github action runs every 24 hours (or on push, or whatever, see workflow)

-> runs python code (`build` package)

-> python fetches data from the github api

-> python makes all the graphs needed (in dot format, so no set layout)

-> python creates index.html with the graphs dot sources and janky html and js and style

-> index.html is uploaded and deployed to github pages

and index.html uses various js libs to draw stuff

the graph layout happens in the browser (graphviz runs in the client browser)

## Run locally

(optional) Create and activate a virtual environment: `python3 -m venv .venv && . .venv/bin/activate`

Dependencies: `pip install -r requirements.txt`

A personal access token is needed (no specific permission required)
(see https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens / https://github.com/settings/personal-access-tokens/new )

Run the build package (`python3 -m build`)

Also pass the path to an existing directory with `--out`

Pass the api token with `--token`

Optionally pass `--cache` to enable caching the API results, so you don't spend an eternity waiting for the data every time you rerun.

With caching, the data is saved in cache.pickle in the cwd, you can delete it to rerequest fresh data from the api or rename it and save it for later

i.e. `mkdir -p _site/ && python3 -m build --out _site/ --token YOUR_TOKEN --cache`
