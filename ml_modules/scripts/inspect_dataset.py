"""Look at what the parser actually produces for a given hand-history file.

The hand-history corpus is not in the repository (it is several gigabytes, and
`.gitignore` excludes it), so this is the tool for answering "is the data shaped
the way the pipeline assumes" before spending twenty minutes on an ingest run.
Three questions come up repeatedly:

    python scripts/inspect_dataset.py file <path>      # what did one file yield?
    python scripts/inspect_dataset.py survey <dir>     # which sources parse at all?
    python scripts/inspect_dataset.py raw <path>       # what does pokerkit see?

This replaces four scripts that lived in `ml_modules/tests/` and were named
`test_*.py` despite containing no assertions. pytest collected them, tried to
import a `data_loader` module that had since moved into `src/parsers/`, and
aborted the whole run on the ImportError. They were never tests; they were
these three questions with the paths hardcoded to one machine's layout.
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Same preamble as pipeline/run_pipeline.py: the package imports itself
# absolutely, so the ml_modules root has to be importable.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

import pandas as pd
import pokerkit

from src.parsers.data_loader import PHHParser

# The columns worth eyeballing. `hole_cards` is only populated for hands that
# reached a showdown, which is the constraint the whole labeling approach is
# built around, so it belongs in any quick look at a file.
SUMMARY_COLUMNS = ['player_id', 'street', 'is_showdown', 'hole_cards', 'bet_amount']


def inspect_file(path: str, limit: int) -> int:
    """Parse one file and print a sample of the records it produced."""
    parser = PHHParser()

    start = time.time()
    records = list(parser.parse_phh_file(path))
    elapsed = time.time() - start

    print(f"{path}")
    print(f"  {len(records)} records in {elapsed:.2f}s")

    if not records:
        # Not necessarily a failure: a file of hands that all ended preflop
        # without a showdown legitimately yields nothing the labeler can use.
        # `failed_parses.log` is where PHHParser records the real errors.
        print("  no records - check failed_parses.log for parse errors")
        return 1

    frame = pd.DataFrame(records)
    present = [c for c in SUMMARY_COLUMNS if c in frame.columns]
    missing = [c for c in SUMMARY_COLUMNS if c not in frame.columns]

    print(f"  columns: {', '.join(frame.columns)}")
    if missing:
        print(f"  MISSING expected columns: {', '.join(missing)}")

    showdowns = int(frame['is_showdown'].sum()) if 'is_showdown' in frame else 0
    print(f"  showdown records: {showdowns} of {len(frame)}")
    print()
    print(frame[present].head(limit).to_string())

    return 0


def survey_directory(directory: str) -> int:
    """Parse one file from each subdirectory to see which sources work.

    The handhq dump is split by site and stake, and the sites do not all use the
    same dialect. Parsing a single file per directory is enough to find the ones
    that yield zero records before committing to a full ingest.
    """
    root = Path(directory)
    if not root.is_dir():
        print(f"Not a directory: {directory}")
        return 1

    subdirs = sorted(d for d in root.iterdir() if d.is_dir())
    if not subdirs:
        print(f"No subdirectories under {directory}")
        return 1

    parser = PHHParser()
    print(f"{'Source':<60} | Records")
    print("-" * 75)

    empty = 0
    for directory_entry in subdirs:
        sample = next(directory_entry.rglob('*.phhs'), None) or next(
            directory_entry.rglob('*.phh'), None
        )
        if sample is None:
            print(f"{directory_entry.name:<60} | no .phh/.phhs files")
            continue
        try:
            count = len(list(parser.parse_phh_file(str(sample))))
        except Exception as exc:  # noqa: BLE001 - surveying, so report and continue
            print(f"{directory_entry.name:<60} | error: {exc}")
            empty += 1
            continue
        print(f"{directory_entry.name:<60} | {count}")
        if count == 0:
            empty += 1

    print()
    print(f"{len(subdirs) - empty} of {len(subdirs)} sources produced records")
    return 0


def dump_raw(path: str, hands: int, actions: int) -> int:
    """Print pokerkit's own view of a file, bypassing PHHParser entirely.

    Useful when PHHParser returns nothing and the question is whether the file is
    malformed or the extraction logic is wrong.

    One gotcha this makes visible: `state_actions` is a generator over replayed
    game states, so iterating it twice does not give the same thing twice. Code
    that walks it more than once needs its own list.
    """
    if not Path(path).exists():
        print(f"No such file: {path}")
        return 1

    with open(path) as handle:
        content = handle.read()

    parsed = pokerkit.HandHistory.loads(content)
    if not isinstance(parsed, list):
        parsed = [parsed]

    print(f"{path}")
    print(f"  {len(parsed)} hand(s)")

    for index, hand in enumerate(parsed[:hands]):
        print()
        print(f"  hand {index}: variant={hand.variant}")
        print(f"    players:  {hand.players}")
        print(f"    winnings: {hand.winnings}")

        state_actions = list(hand.state_actions)
        print(f"    {len(state_actions)} state/action pairs")

        for position, (state, action) in enumerate(state_actions[:actions]):
            pot = sum(p.amount for p in state.pots) if state.pots else 0
            actor = None
            if state.actor_index is not None and state.actor_index < len(hand.players):
                actor = hand.players[state.actor_index]
            print(
                f"      [{position}] street={state.street_index} "
                f"actor={actor} pot={pot} action={action}"
            )

        if hand.winnings:
            showdown = any(w for w in hand.winnings if w is not None)
            print(f"    reached showdown (nonzero winnings): {showdown}")
        else:
            print("    winnings is None, so no showdown to label")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect hand-history files and what the parser makes of them."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    file_cmd = subcommands.add_parser("file", help="parse one file and sample the records")
    file_cmd.add_argument("path", help="path to a .phh or .phhs file")
    file_cmd.add_argument("--limit", type=int, default=20, help="rows to display")

    survey_cmd = subcommands.add_parser(
        "survey", help="parse one file per subdirectory to find sources that yield nothing"
    )
    survey_cmd.add_argument("directory", help="directory of per-source subdirectories")

    raw_cmd = subcommands.add_parser("raw", help="dump pokerkit's parse, bypassing PHHParser")
    raw_cmd.add_argument("path", help="path to a .phh or .phhs file")
    raw_cmd.add_argument("--hands", type=int, default=1, help="hands to dump")
    raw_cmd.add_argument("--actions", type=int, default=5, help="actions per hand")

    args = parser.parse_args()

    if args.command == "file":
        return inspect_file(args.path, args.limit)
    if args.command == "survey":
        return survey_directory(args.directory)
    return dump_raw(args.path, args.hands, args.actions)


if __name__ == "__main__":
    sys.exit(main())
