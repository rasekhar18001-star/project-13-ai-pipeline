"""Command-line interface."""

import argparse
import json

from app.rag import RAGService


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    args = parser.parse_args()
    print(json.dumps(RAGService().answer(args.question), indent=2))


if __name__ == "__main__":
    main()
