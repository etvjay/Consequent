from __future__ import annotations

import argparse
import json

from consequent.yuma_reference import simulate_yuma


def _rows() -> tuple[dict[int, float], dict[int, dict[int, float]]]:
    # Miners: 10 = useful, 11 = mediocre, 12 = unsafe/cabal target.
    honest_a = {10: 0.70, 11: 0.30, 12: 0.00}
    honest_b = {10: 0.65, 11: 0.35, 12: 0.00}
    malicious = {10: 0.00, 11: 0.00, 12: 1.00}
    return {1: 0.40, 2: 0.35, 3: 0.25}, {1: honest_a, 2: honest_b, 3: malicious}


def main() -> None:
    parser = argparse.ArgumentParser(description="Pressure Consequent weight rows through the documented Yuma reference model.")
    parser.add_argument("--kappa", type=float, default=0.5)
    parser.add_argument("--sweep-malicious-stake", action="store_true")
    args = parser.parse_args()

    base_stakes, rows = _rows()

    if not args.sweep_malicious_stake:
        result = simulate_yuma(stakes=base_stakes, weights=rows, kappa=args.kappa)
        print(
            json.dumps(
                {
                    "state": "YUMA_REFERENCE_PRESSURE_PASS",
                    "kappa": args.kappa,
                    "stakes": base_stakes,
                    "consensus": result.consensus,
                    "ranks": result.ranks,
                    "incentives": result.incentives,
                    "note": "Reference model only; Subtensor is authoritative economic evidence.",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return

    sweep = []
    for malicious_percent in range(0, 101, 5):
        malicious = malicious_percent / 100.0
        honest = 1.0 - malicious
        stakes = {1: honest * 0.55, 2: honest * 0.45, 3: malicious}
        result = simulate_yuma(stakes=stakes, weights=rows, kappa=args.kappa)
        winner = max(result.incentives, key=result.incentives.get)
        sweep.append(
            {
                "malicious_stake": malicious,
                "winner_uid": winner,
                "useful_incentive": result.incentives[10],
                "unsafe_incentive": result.incentives[12],
                "unsafe_consensus": result.consensus[12],
            }
        )

    print(
        json.dumps(
            {
                "state": "YUMA_REFERENCE_STAKE_SWEEP",
                "kappa": args.kappa,
                "sweep": sweep,
                "note": "Reference model only; identifies mechanism boundaries to verify against chain behavior.",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
