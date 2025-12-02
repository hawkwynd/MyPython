import keyboard
import sys
import os
import json
import time
import threading
import tkinter as tk
from tkinter import StringVar
from datetime import datetime

# === CONFIG ===
JOURNAL_FOLDER = os.path.expanduser(
    "~/Saved Games/Frontier Developments/Elite Dangerous/"
)

# Get the current datetime object
now = datetime.now()

# Extract the month as an integer (1-12)
current_month_number = now.month
# Extract todays date day as an integer (1-31)
current_day = now.day 

# Journal.2025-11-18xxxxxxxx.log (limit to todays logs, else we're loading the whole months worth...)
JOURNAL_PREFIX = f"Journal.2025-"

# Track processed lines
processed = set()

def exit_script():
    print("Exiting script...")
    sys.exit(0)  # Exit the program with a success status

# === JOURNAL SCANNER ===
def scan_journals():
    
    try:
            files = [
                f for f in os.listdir(JOURNAL_FOLDER)
                if f.startswith(JOURNAL_PREFIX)
            ]
            
            files.sort()
    
            for fname in files:
                
                path = os.path.join(JOURNAL_FOLDER, fname)
                
                # obtain datetime from fname Journal.2025-06-29T205852.01.log
                date_format = "%Y-%m-%d"
                fntimest = fname.split('.')
                logdate1 = fntimest[1]
                trimmed = logdate1.split('T')
                
                datetime_object = datetime.strptime(trimmed[0], date_format)
                y = datetime_object.year
                d = datetime_object.day
                m = datetime_object.month
    
                date_object = f"{m}/{d}/{y}"
               
                with open(path, "r", encoding="utf-8") as f:
                    for raw in f:
                        if raw in processed:
                            continue
                        processed.add(raw)
    
                        line = raw.strip()
                        if not line.startswith("{"):
                            continue
    
                        try:
                            # convert to json object
                            event = json.loads(line)
    
                        except json.JSONDecodeError:
                            continue
    
                        ev = event.get("event")
    
                        body_name = event.get("BodyName", "")
                        
                        # Shrogaae systems only check for SAASignalsFound 
                        if ev == "SAASignalsFound" and body_name and "Shrogaae" in body_name:
                            
                            signals = event.get("Signals")
                            BodyName = event.get("BodyName")
                            
                            if signals is not None and "Ring" in BodyName:
                                for s in signals:
    
                                    print(f"{ev} {date_object}: {BodyName} {s['Type']}:{s['Count']}" )
    except Exception as e:
        print("Error:", e)
        time.sleep(2)

keyboard.add_hotkey('esc', exit_script)
print("scanning your journal files...")
scan_journals()
