"""Quick chunk-size diagnostics for VerbatimRAG ingestion.

Usage:
  python scripts/analyze_chunk_lengths.py /path/to/doc.pdf
"""

from __future__ import annotations

import argparse
from statistics import mean

from verbatim_rag.ingestion.document_processor import DocumentProcessor


def summarize(lengths: list[int]) -> str:
    if not lengths:
        return "no chunks"
    p95_idx = max(0, int(0.95 * len(lengths)) - 1)
    ordered = sorted(lengths)
    return (
        f"count={len(lengths)}, min={ordered[0]}, median={ordered[len(ordered)//2]}, "
        f"p95={ordered[p95_idx]}, max={ordered[-1]}, avg={mean(lengths):.1f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    processor = DocumentProcessor()
    document = processor.process_file(args.file)

    lengths = [len(c.content) for c in document.chunks]
    print("Chunk length summary:", summarize(lengths))

    top = sorted(enumerate(lengths), key=lambda x: x[1], reverse=True)[:10]
    print("Top longest chunks:")
    for idx, length in top:
        print(f"  chunk#{idx}: {length} chars")


if __name__ == "__main__":
    main()