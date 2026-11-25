# git-commit-helper

Draft a conventional-commit message from the staged diff. Nothing is committed.

## Requirements

- Python 3 (standard library only — no third-party packages)

## How to run

```bash
cd 052-git-commit-helper
python3 main.py
```

Run `python3 main.py --help` to see all options.

## Example

```bash
python3 main.py
```

Sample output:

```
Draft commit message:
----------------------------------------
fix: update login, retry in 1 file(s)

- src/auth.py

1 file(s) changed, 3 added line(s).
----------------------------------------
Nothing was committed. Use: git commit -m "<subject>"
```

## Notes

Stage changes first with `git add`. Use `--unstaged` for the unstaged diff, `--diff-file` to read a diff from a file, and `--type` / `--scope` / `--subject` to override the guess.

## License

MIT — see [LICENSE](LICENSE).
