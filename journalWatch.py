import requests
import json
import os 
import sys

JOURNAL_FOLDER = os.path.expanduser(
    "~/Saved Games/Frontier Developments/Elite Dangerous/"
)

JOURNAL_PREFIX = f"Journal.2025-12-22"

files = [
            f for f in os.listdir( JOURNAL_FOLDER )
                if f.startswith( JOURNAL_PREFIX )
        ]
          

body = ""
files.sort()

# Track processed lines
processed = set()

for fname in files:
                path = os.path.join(JOURNAL_FOLDER, fname)
                print(path)
                
                with open(path, "r", encoding="utf-8") as f:
                    for raw in f:
                        if raw in processed:
                            continue
                        processed.add(raw)
                        line = raw.strip()

                        if not line.startswith("{"):
                            continue

                        try:
                            event = json.loads(line)
                        except:
                            continue

                    ev = event.get("event")
                    print(ev)