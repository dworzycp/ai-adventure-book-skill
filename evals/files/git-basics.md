# Git basics for new joiners

This guide covers the handful of git operations you will use every day on the team. It assumes git is installed and you have cloned a repository.

## Mental model

Git stores snapshots of your whole project, called **commits**. Each commit points at its parent, so the history is a chain. A **branch** is just a movable label that points at a commit. `main` is the branch everyone shares; you do your work on your own branch and merge it back when it is ready.

There are three places your changes can be:

1. The **working tree**: the files on disk you are editing.
2. The **staging area** (also called the index): the set of changes you have marked for the next commit.
3. The **repository**: committed history.

`git status` tells you what is where. Run it often.

## Starting work

Always start from an up-to-date `main`:

```bash
git switch main
git pull
git switch -c feature/short-description
```

Branch names use the pattern `<type>/<short-description>`, for example `feature/csv-export` or `fix/login-timeout`. Lowercase, hyphens, no spaces.

## Saving work

Stage the files you want in the commit, then commit with a message:

```bash
git add path/to/file.ts
git commit -m "feat(export): add CSV download for catalog table"
```

Use `git add -p` to stage only some of the changes in a file. It walks you through each hunk and asks yes or no.

Commit messages follow Conventional Commits: `type(scope): summary`. Types we use are `feat`, `fix`, `refactor`, `test`, `docs`, and `chore`. The summary is imperative and lowercase, under 72 characters. A commit should be one logical change; if you find yourself writing "and" in the summary, split it.

## Sharing work

Push your branch and open a pull request:

```bash
git push -u origin feature/short-description
gh pr create --draft
```

Open every PR as a draft first. Mark it ready for review only when CI is green and you have read your own diff.

## Staying current

`main` moves while you work. Bring your branch up to date with rebase rather than merge, so the history stays linear:

```bash
git fetch origin
git rebase origin/main
```

If the rebase stops with a conflict, git will tell you which files are in conflict. Open them, look for the `<<<<<<<`, `=======`, and `>>>>>>>` markers, decide what the code should be, remove the markers, then:

```bash
git add <resolved-file>
git rebase --continue
```

If it goes badly, `git rebase --abort` puts everything back the way it was. Nothing is lost.

After a rebase your branch history has changed, so pushing needs `--force-with-lease`. Never plain `--force`: `--force-with-lease` refuses if someone else has pushed to your branch since you last fetched.

```bash
git push --force-with-lease
```

## Undoing things

| Situation | Command | Notes |
| --- | --- | --- |
| Discard edits to a file you have not staged | `git restore <file>` | Cannot be undone. |
| Unstage a file but keep the edits | `git restore --staged <file>` | Safe. |
| Change the last commit's message or contents | `git commit --amend` | Only on commits you have not pushed. |
| Undo the last commit but keep the changes | `git reset --soft HEAD~1` | Safe. |
| Find a commit you think you lost | `git reflog` | Shows everywhere HEAD has been for ~90 days. |

The reflog is the safety net. Almost nothing in git is truly gone until the reflog expires.

## Things not to do

- Do not commit directly to `main`. Branch protection will reject it, but do not rely on that.
- Do not commit secrets, `.env` files, or credentials. If one slips in, tell the team immediately so it can be rotated; deleting the file in a later commit does not remove it from history.
- Do not use `git push --force` on a shared branch.
- Do not `git add .` without checking `git status` first. It is how build artifacts and scratch files end up in PRs.

## Getting help

`git <command> --help` opens the manual for any command. For anything you cannot untangle in ten minutes, ask in `#dev-help`; a rebase gone wrong is a five-minute fix for someone who has seen it before.
