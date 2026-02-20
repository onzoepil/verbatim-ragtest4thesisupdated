from pathlib import Path
import shutil
import os

DB_PATH = Path("index.db")
STATE_FILE = Path("ingested_files.txt")

# Remove the Milvus Lite index: can be either a file or a directory
if DB_PATH.exists():
    if DB_PATH.is_dir():
        shutil.rmtree(DB_PATH)
        print("Removed index.db directory")
    else:
        DB_PATH.unlink()
        print("Removed index.db file")

# Remove the ingested-files tracker
if STATE_FILE.exists():
    STATE_FILE.unlink()
    print("Removed ingested_files.txt")

print("Index reset. Next ingest_docs.py run will build a new index from my_docs/.")
