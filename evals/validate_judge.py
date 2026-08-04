"""Compare the LLM judge with labels personally completed by the student."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.config import load_settings
from app.llm import OpenAIClient
from evals.judge import judge_answer, load_cases


def validate(cases: list[dict[str, object]], client: object, model_id: str) -> dict[str, object]:
    if any(case.get("human_grounded") is None for case in cases):
        raise ValueError("human labels contain null; the student must personally complete every human_grounded value")
    tp = tn = fp = fn = 0
    for case in cases:
        predicted = judge_answer(client, model_id, str(case["context"]), str(case["answer"]))["grounded"]
        actual = bool(case["human_grounded"])
        tp += predicted and actual
        tn += (not predicted) and (not actual)
        fp += predicted and (not actual)
        fn += (not predicted) and actual
    total = len(cases)
    agreement = tp + tn
    return {
        "total": total,
        "agreement": agreement,
        "agreement_percentage": agreement / total * 100,
        "false_positive_count": fp,
        "false_negative_count": fn,
        "confusion_matrix": {"true_positive": tp, "true_negative": tn, "false_positive": fp, "false_negative": fn},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("labels", type=Path)
    parser.add_argument("--min-agreement", type=float, default=0.80)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    settings = load_settings()
    try:
        result = validate(
            load_cases(args.labels), OpenAIClient(settings.base_url, settings.api_key), settings.judge_model_id
        )
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2
    print(json.dumps(result, indent=2))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0 if result["agreement_percentage"] / 100 >= args.min_agreement else 1


if __name__ == "__main__":
    sys.exit(main())
