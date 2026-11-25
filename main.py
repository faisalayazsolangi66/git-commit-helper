#!/usr/bin/env python3
"""Draft a commit message from the staged diff (or a diff file).

Reads `git diff --cached` by default, inspects the changed files and
added lines, guesses a conventional-commit type, and prints a draft
message. Nothing is committed; copy the draft into `git commit -m`.
"""
import argparse
import re
import subprocess
import sys
from collections import Counter

TYPE_HINTS = [
    (r"\b(fix|bug|error|crash|patch)\b", "fix"),
    (r"\b(test|spec)\b", "test"),
    (r"\b(doc|readme|comment)\b", "docs"),
    (r"\b(refactor|clean|rename|move)\b", "refactor"),
    (r"\b(style|format|lint)\b", "style"),
    (r"\b(chore|config|build|deps?|ci)\b", "chore"),
]


def get_diff(repo, staged, diff_file):
    if diff_file:
        with open(diff_file, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    args = ["diff", "--cached"] if staged else ["diff"]
    result = subprocess.run(["git"] + args, cwd=repo,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return result.stdout


def parse_diff(diff):
    files, added = [], []
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            parts = line.split(" b/")
            if len(parts) == 2:
                files.append(parts[1])
        elif line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:].strip())
    return files, [a for a in added if a]


def guess_type(files, added):
    text = " ".join(files + added).lower()
    for pattern, kind in TYPE_HINTS:
        if re.search(pattern, text):
            return kind
    if any(f.endswith((".md", ".rst", ".txt")) for f in files):
        return "docs"
    if any("test" in f.lower() for f in files):
        return "test"
    return "feat"


def summarize(files, added):
    topics = Counter()
    for line in added:
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", line)
        for word in words:
            if word.lower() not in {"the", "and", "for", "with", "this",
                                    "that", "from", "return", "import"}:
                topics[word.lower()] += 1
    return topics.most_common(5)


def main():
    parser = argparse.ArgumentParser(
        description="Draft a commit message from the staged diff.")
    parser.add_argument("repo", nargs="?", default=".",
                        help="Path to the git repository (default: current directory)")
    parser.add_argument("--unstaged", action="store_true",
                        help="Use the unstaged diff instead of the staged diff")
    parser.add_argument("--diff-file", help="Read the diff from a file instead of git")
    parser.add_argument("--type", dest="ctype",
                        help="Override the guessed commit type, e.g. feat, fix, docs")
    parser.add_argument("--scope", help="Scope for the message, e.g. auth, api")
    parser.add_argument("--subject", help="Override the generated subject line")
    args = parser.parse_args()

    try:
        diff = get_diff(args.repo, not args.unstaged, args.diff_file)
    except (RuntimeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not diff.strip():
        print("No changes found. Stage changes first with 'git add'.")
        return 1

    files, added = parse_diff(diff)
    if not files:
        print("Could not parse any changed files from the diff.")
        return 1

    ctype = args.ctype or guess_type(files, added)
    scope = f"({args.scope})" if args.scope else ""
    if args.subject:
        subject = args.subject
    else:
        topics = summarize(files, added)
        hint = ", ".join(w for w, _ in topics[:3]) if topics else "update"
        subject = f"{ctype}{scope}: update {hint} in {len(files)} file(s)"

    print("Draft commit message:")
    print("-" * 40)
    print(subject)
    print()
    for f in files:
        print(f"- {f}")
    print(f"\n{len(files)} file(s) changed, {len(added)} added line(s).")
    print("-" * 40)
    print("Nothing was committed. Use: git commit -m \"<subject>\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
