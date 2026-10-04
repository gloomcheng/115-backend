"""Lesson 17 — what a pipeline is, and the one failure it exists to catch.

    python pipeline_demo.py gate       # a check you can skip is not a check
    python pipeline_demo.py env        # the same code, two environments
    python pipeline_demo.py steps      # what a pipeline is made of
    python pipeline_demo.py all

Every mode runs here and in CI. The difference is the environment, and
that difference is the whole reason the pipeline exists.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run_gate() -> None:
    print("1. A gate only works if nothing can walk past it")
    print()
    print("   The repository runs its checks with one command:")
    print()
    print("     npm run check")
    print()
    print("   Sixteen checks, and a failure in any one of them stops the build.")
    print("   That command is the pipeline. It is not a GitHub feature.")
    print()
    print("   What makes it a gate rather than advice:")
    print()
    print("     you can run it            -> catches mistakes before you push")
    print("     the server runs it too     -> catches what you did not run")
    print()
    print("   So there are two copies of the same check, not one check and a")
    print("   separate review process. If they ever disagree, the disagreement")
    print("   is itself the bug.")


def run_env() -> None:
    print("2. The same code, two environments")
    print()

    key = os.environ.get("SIGNING_KEY")

    print(f"   SIGNING_KEY is {'set' if key else 'not set'}")
    print()

    if key is None:
        print("   Starting the app anyway...")
        print()
        print("   RuntimeError: SIGNING_KEY is not set.")
        print()
        print("   This is unit 12's rule, and this is why it exists.")
        print("   The app refuses to start instead of falling back to a default")
        print("   that would work on your laptop and fail on the server.")
        print()
        print("   On your computer you have the variable in your shell, so you")
        print("   never see this. On a fresh machine there is no shell profile,")
        print("   no .env you forgot to copy, and no muscle memory.")
        print()
        print("   The pipeline is the first place that fresh machine exists.")
    else:
        print("   App started. Every check passed.")
        print()
        print("   Now unset the variable and run it again:")
        print("     env -u SIGNING_KEY python pipeline_demo.py env")


def run_steps() -> None:
    print("3. What a pipeline is made of")
    print()
    print("   Four steps, and every real pipeline has all four whether or not")
    print("   the author named them:")
    print()
    print("     1. get the code          checkout the exact commit")
    print("     2. install what it needs  dependencies, pinned")
    print("     3. run the checks         the same command you run locally")
    print("     4. decide                 pass means continue, fail means stop")
    print()
    print("   Step 3 is the one people mean when they say CI. Steps 1, 2 and 4")
    print("   are where the surprises live.")
    print()
    print("   Step 1: the pipeline tests one exact commit, not your working")
    print("   directory. If you pushed something uncommitted, the pipeline is")
    print("   testing different code than the code on your screen.")
    print()
    print("   Step 2: if the dependencies are not pinned, the pipeline can break")
    print("   on a day you changed nothing, and you will spend the afternoon")
    print("   bisecting a version you never touched.")
    print()
    print("   Step 4: a pipeline that reports failure but does not block is a")
    print("   report, not a gate. Nobody reads red text in a notification for")
    print("   three months and then still reads it.")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    runners = {"gate": run_gate, "env": run_env, "steps": run_steps}
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