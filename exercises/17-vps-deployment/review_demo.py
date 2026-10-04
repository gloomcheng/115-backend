"""Lesson 17 — code review, measured on this repository.

    python review_demo.py sizes       # how big are the diffs people review
    python review_demo.py mechanical  # what a script can catch here
    python review_demo.py human       # what only a person can catch
    python review_demo.py all

The sizes come from running git over this repository's real history, not
from a table in a book. The mechanical checks run over the lesson exercises
and report what they actually find, including nothing.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout


def run_sizes() -> None:
    print("1. How large are the diffs this repository asks someone to review?")
    print()
    commits = git("log", "--format=%H").split()
    if not commits:
        print("   no git history found")
        return

    sizes = []
    for commit in commits:
        numstat = git("show", "--numstat", "--format=", commit)
        total = 0
        for line in numstat.strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
                total += int(parts[0]) + int(parts[1])
        sizes.append(total)

    sizes.sort()
    count = len(sizes)

    def percentile(fraction: float) -> int:
        return sizes[min(count - 1, int(count * fraction))]

    print(f"   commits measured      : {count}")
    print(f"   median lines changed  : {percentile(0.5)}")
    print(f"   75th percentile       : {percentile(0.75)}")
    print(f"   90th percentile       : {percentile(0.9)}")
    print(f"   largest single commit : {sizes[-1]}")
    print()
    print("   A reviewer's working memory does not grow with the diff. Somewhere")
    print("   past a few hundred lines the reader starts skimming and approving")
    print("   from the shape of the change instead of reading it.")
    print()
    print("   So the number above is not a compliment to the repository. It is")
    print("   the reason section 10.5 says a large change should arrive in")
    print("   pieces. This file is measuring the lesson against itself.")


CHECKS = [
    (
        "bare except",
        re.compile(r"except\s*:\s*(?:pass)?\s*$", re.MULTILINE),
        "except with no handler swallows every error, including KeyboardInterrupt",
    ),
    (
        "todo left behind",
        re.compile(r"\b(?:TODO|FIXME|XXX)\b"),
        "a marker in a commit is fine, a marker in main is a promise you forgot",
    ),
    (
        "printed instead of logged",
        re.compile(r"^\s*print\(", re.MULTILINE),
        "print goes to stdout; unit 15 explains why that is not a log",
    ),
    (
        "hardcoded host and port",
        re.compile(r"(?:localhost|127\.0\.0\.1):\d{4}"),
        "fine in teaching material, not fine in code you ship",
    ),
]


def run_mechanical() -> None:
    print("2. What a script can check")
    print()
    # This file is excluded: every pattern below appears in its own source.
    targets = [
        path
        for path in sorted(ROOT.glob("exercises/*/*.py"))
        if path.name != "review_demo.py"
    ]
    print(f"   scanning {len(targets)} exercise files, excluding this one")
    print()

    noisy = None
    for name, pattern, why in CHECKS:
        hits = []
        for path in targets:
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in pattern.finditer(text):
                line = text[: match.start()].count("\n") + 1
                hits.append(f"{path.relative_to(ROOT)}:{line}")

        shown = ", ".join(hits[:3]) if hits else "nothing"
        if len(hits) > 3:
            shown += f", and {len(hits) - 3} more"
        print(f"   {name}")
        print(f"     {len(hits)} hit(s): {shown}")
        print(f"     why: {why}")
        if len(hits) > 50:
            noisy = name
        print()

    print("   Every one of those is a grep with a regular expression. No model and")
    print("   no judgement required.")
    print()
    if noisy:
        print(f"   Look at the hit count on '{noisy}'. That check is not wrong, and")
        print("   turning it on anyway would be a mistake.")
        print()
        print("   These are command line teaching scripts. stdout *is* their")
        print("   interface, so every print is correct. The rule is aimed at a web")
        print("   service, where stdout has a different job.")
        print()
        print("   And this is the part people get wrong about linters: a rule that")
        print("   fires five hundred times on correct code gets switched off within")
        print("   a week, and a rule that is switched off catches nothing at all.")
        print("   Five hundred false positives is worse than no rule, because it")
        print("   removes the habit of reading the output.")
        print()
        print("   The concurrency lesson has the same problem from the other")
        print("   direction: it deliberately contains a data-losing race, and a")
        print("   checker that flagged that file would be wrong about it.")


def run_human() -> None:
    print("3. What only a person can check")
    print()
    print("   None of the following is expressible as a pattern, and every real")
    print("   review turns on them:")
    print()
    print("     Intent      Does this change what we said it changes? A diff shows")
    print("                 what happened, never why it was wanted.")
    print()
    print("     Duplication Three places that know the role is admin is fine.")
    print("                 Three places that know how to parse a date is a")
    print("                 decision that was never made deliberately.")
    print()
    print("     Naming      Nothing fails when a function is called handle().")
    print("                 The cost is paid by whoever reads it in six months.")
    print()
    print("     Scope       This commit changed the rate limit and the colour of")
    print("                 a log line. One of those is a security control. Both")
    print("                 are now unreviewable as separate things.")
    print()
    print("     Consequences A test proves the contract holds. It cannot tell you")
    print("                 the contract is the right one.")
    print()
    print("   A linter checks the list on the left. You are paid for the list on")
    print("   the right, and it is the only one that catches a wrong turn taken")
    print("   confidently and with passing tests.")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    runners = {"sizes": run_sizes, "mechanical": run_mechanical, "human": run_human}
    if mode == "all":
        for runner in runners.values():
            runner()
    elif mode in runners:
        runners[mode]()
    else:
        print(f"unknown mode: {mode}")
        print(f"try one of: {', '.join(runners)}")
        sys.exit(1)


if __name__ == "__main__":
    main()