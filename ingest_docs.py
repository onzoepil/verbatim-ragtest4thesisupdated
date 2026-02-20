from pathlib import Path

from verbatim_rag import VerbatimIndex
from verbatim_rag.ingestion import DocumentProcessor
from verbatim_rag.vector_stores import LocalMilvusStore
from verbatim_rag.embedding_providers import SpladeProvider

DOCS_DIR = Path("my_docs")          # <- just drop PDFs here
STATE_FILE = Path("ingested_files.txt")  # remembers what was already ingested


def get_index():
    vector_store = LocalMilvusStore(
        db_path="./index.db",          # must match api/app.py
        collection_name="verbatim_rag",
        enable_sparse=True,
        enable_dense=False,
    )
    sparse_provider = SpladeProvider(
        model_name="opensearch-project/opensearch-neural-sparse-encoding-doc-v3-distill",
        device="cpu",
    )
    return VerbatimIndex(
        vector_store=vector_store,
        sparse_provider=sparse_provider,
    )


def main():
    DOCS_DIR.mkdir(exist_ok=True)

    # Load list of already-ingested files (to avoid duplicates)
    already = set()
    if STATE_FILE.exists():
        already = {
            line.strip()
            for line in STATE_FILE.read_text().splitlines()
            if line.strip()
        }

    pdf_paths = sorted(DOCS_DIR.glob("*.pdf"))
    new_files = [p for p in pdf_paths if p.name not in already]

    if not new_files:
        print("No new PDFs to ingest in my_docs/.")
        return

    print(f"Found {len(new_files)} new PDF(s) in my_docs/")

    processor = DocumentProcessor()
    index = get_index()

    docs = []
    for path in new_files:
        print(f"\nProcessing {path.name} ...")
        doc = processor.process_file(
            file_path=str(path),
            title=path.stem,
            metadata={"source": "my_docs", "filename": path.name},
        )

        # --- Preview: first 100 words of extracted text ---
        # Try common attribute names; fall back to empty string if missing
        text = getattr(doc, "raw_content", "") or getattr(doc, "text", "")
        if not text:
            print("  [WARNING] No text extracted from this document.")
        else:
            words = text.split()
            total_words = len(words)
            preview_words = " ".join(words[:100])
            print(f"  Extracted ~{total_words} words.")
            print("  Preview (first 100 words):")
            print("  " + preview_words)
        print("-" * 80)
        # -------------------------------------------------

        docs.append(doc)

    print(f"\nIndexing {len(docs)} document(s) into index.db ...")
    index.add_documents(docs)

    # Update state file
    with STATE_FILE.open("a") as f:
        for p in new_files:
            f.write(p.name + "\n")

    print("Done! New documents added to index.db")


if __name__ == "__main__":
    main()
