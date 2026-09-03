from __future__ import annotations

import argparse
import json

from consequent.validator_dispersion import summarize_dispersion


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure Consequent validator dispersion across private evaluator seeds.")
    parser.add_argument("--seed-start", type=int, default=100)
    parser.add_argument("--seed-count", type=int, default=100)
    args = parser.parse_args()

    if args.seed_count < 1:
        raise SystemExit("--seed-count must be positive")

    seeds = range(args.seed_start, args.seed_start + args.seed_count)
    summary = summarize_dispersion(seeds)
    passed = (
        summary.useful_top_count == summary.seed_count
        and summary.policy_positive_count == 0
        and summary.useful_weight_min > summary.overfit_weight_max
    )
    print(
        json.dumps(
            {
                "state": "VALIDATOR_DISPERSION_PASS" if passed else "VALIDATOR_DISPERSION_FAIL",
                **summary.__dict__,
                "note": "Local/reference evaluator evidence only; independent on-chain validators remain a later gate.",
            },
            indent=2,
            sort_keys=True,
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
