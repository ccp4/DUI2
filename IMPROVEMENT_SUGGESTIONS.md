# Improvement suggestions for `Dui2-ai-pr`

Notes from comparing `luisodls/Dui2-ai-pr` against `ccp4/DUI2` (upstream), plus a
general repo-hygiene pass. For personal study/reference — not yet actioned.

## Status vs upstream

`master` here is exactly `ccp4/DUI2`'s `master` (`694aa46`) plus 4 commits ahead,
0 behind. Clean superset, no merge conflicts, no rebase needed.

### The 4 commits ahead of upstream

| Commit | What it does | Note |
|---|---|---|
| `d9e6ac0` removing eval for security reasons | Replaces `eval(right_side)` / `str(params)` with `json.loads`/`json.dumps` in 3 files (`img_view_threads_n_menus.py`, `data_n_json.py`, `img_view_utils.py`) | Genuinely good — `eval()` on data coming over the wire (client↔server) is a real code-injection risk. Strongest commit of the four. |
| `7277e63` replacing while loop with thread.wait | Swaps a busy-wait loop for `thread.wait()` | Efficiency cleanup |
| `8328b07` working-directory picker dialog | Lets the user pick a working dir via file dialog | UX feature |
| `cf53956` log file relocation | Moves log file alongside the chosen dir | Small follow-up to the above |

**Recommendation:** none of these are upstream yet. Especially the `eval()` fix —
worth opening a PR to `ccp4/DUI2` for that one on its own rather than letting it
sit only in the fork.

## Repo hygiene (missing in both upstream and fork, but easy wins here)

- **No `.gitignore`** — `__pycache__/*.pyc` currently sits untracked in the
  working tree only by luck; one `git add -A` away from being committed. Add a
  standard Python `.gitignore`.
- **No CI** (`.github/workflows/`) — nothing runs tests or lint on push. Even a
  minimal "install + pytest" GitHub Actions workflow signals the repo is
  maintained, and gives the README something legitimate to badge.
- **Tests exist but aren't wired up** — `src/dui2/client/tests/` has ~10 test
  files but no `pytest.ini` / `conftest.py` / CI job actually running them.
  Untested-looking tests read worse than no tests.
- **`pyproject.toml` is missing standard metadata** — no `authors`, `readme`,
  `license`, `classifiers`, or `urls` (Homepage/Repository/Issues). A GPL-2
  `LICENSE` file exists but isn't declared in `pyproject.toml`.

## Code-level smells (grepped across `src/`, ~17k LOC)

- **233 `print()` calls** in production code vs. the `logging` module that's
  already used elsewhere — inconsistent, and `print` can't be silenced/leveled
  in production.
- **53 TODO/FIXME/XXX** comments left in-tree — either resolve them or move
  them to GitHub issues.
- **25 wildcard `import *`** — hides what's actually imported, defeats linters.
- **12 hardcoded `/home/`/`/Users/` absolute paths** — portability red flag.
- **1 bare `except:`** — swallows everything including `KeyboardInterrupt`.
- **Sprawling entry points** — `src/run_dui2*.py` (×4), `run_img_client.py`,
  `run_img_server.py`, `run_multi_user_dui2_server.py`, `run_user_login.py`,
  plus `all_local.py` / `all_local_all_ram.py` / `only_client.py` /
  `only_server.py` inside the package — no doc anywhere explaining which is
  canonical vs. legacy. A short "which script do I run" table in the README
  would help a lot.
- **Commit message style is inconsistent** (lowercase, informal — e.g. "adding
  log file to dir re-location") — fine for personal work, but worth tightening
  if this fork is meant to be reviewed or upstreamed.

## Suggested priority order

1. Add `.gitignore` (5 min, zero risk)
2. Fill in `pyproject.toml` metadata (`license`, `readme`, `authors`, `urls`)
   (10 min)
3. Add a minimal CI workflow that installs the package and runs the existing
   tests (30 min — biggest "looks maintained" signal)
4. Open a PR upstream with the `eval()` security fix specifically — that's the
   commit most worth getting merged
5. Swap `print()` → `logging` and clean up the bare `except:` as time allows
