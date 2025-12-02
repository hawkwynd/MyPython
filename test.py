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
JOURNAL_PREFIX = f"Journal.2025-{current_month_number}-{current_day}"

# JOURNAL_PREFIX = f"Journal.2025-{current_month_number}-"

# The targeted biological genus.
TARGET_GENUS = "Radicoida"

# === PER-COMMANDER COUNTERS ===
commanders = {}

# Track processed lines
processed = set()


# === DRAGGABLE OVERLAY ===
def create_overlay():
    root = tk.Tk()
    root.title("Genus Sampler for Radicoida")
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.attributes("-alpha", 0.80)

    # Move overlay left so extra text fits
    root.geometry("+30+400")
    
    # Esc key exits the application
    root.bind("<Escape>", lambda e: root.destroy())

    var = StringVar()
    var.set( JOURNAL_PREFIX )

    label = tk.Label(
        root,
        textvariable=var,
        font=("Euro Caps", 12, "normal"),
        fg="cyan",
        bg="black",
        padx=40,      # widened
        pady=20,
        justify="left",
        anchor="w",   # align text left
    )
    label.pack()

    # === DRAG LOGIC ===
    def start_move(event):
        root.x = event.x
        root.y = event.y

    def do_move(event):
        x = root.winfo_x() + (event.x - root.x)
        y = root.winfo_y() + (event.y - root.y)
        root.geometry(f"+{x}+{y}")

    label.bind("<Button-1>", start_move)
    label.bind("<B1-Motion>", do_move)
    
    return root, var


# === JOURNAL SCANNER ===
def scan_journals(var):

    global commanders
    current_cmr = None
    curSystem = None
    jumpsRemaining = 0
    JumpDist = 0
    
    while True:
			
        try:
            files = [
                f for f in os.listdir( JOURNAL_FOLDER )
                if f.startswith( JOURNAL_PREFIX )
            ]
            
            files.sort()
    

            for fname in files:
                path = os.path.join(JOURNAL_FOLDER, fname)

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
                        sampleName = ""
                        
                        # FSDTarget
                        if ev == "FSDTarget":
                            jumpsRemaining = event.get("RemainingJumpsInRoute")


                        # === grab system name when jumping into it ===
                        if ev == "FSDJump":
                             curSystem = event.get("StarSystem")
                             JumpDist = round( event.get("JumpDist") )
											
                        
                        # === Detect commander via LoadGame ===
                        if ev == "LoadGame":
                            cmr = event.get("Commander")
                            
                            if cmr:
                                current_cmr = cmr.title()

                                if cmr not in commanders:
                                    commanders[cmr] = {"on_hand": 0, "submitted": 0, "samples": 0 }
                            continue

                        # === Skip until LoadGame detected ===
                        if not current_cmr:
                            continue  

                        # === Add commander to commander list ===
                        if current_cmr not in commanders:
                            commanders[current_cmr] = {"on_hand": 0, "submitted": 0,"samples": 0}

                        # === Get Current Commander Data===
                        cmrdata = commanders[current_cmr]
                        
						# === Sample scan in gun === 
                        if (event.get("ScanType") == "Log" or event.get("ScanType") == "Sample" and event.get("Genus_Localised") == TARGET_GENUS):
                            cmrdata["samples"] += 1
                        						
                        # === Analyse scan ===
                        if ev == "ScanOrganic":
                            if (event.get("ScanType") == "Analyse" and
                                event.get("Genus_Localised") == TARGET_GENUS):
                                cmrdata["on_hand"] += 1
                                # reset gun sample count
                                cmrdata["samples"] = 0

                        # === SellOrganicData reset variables ===
                        if ev == "SellOrganicData":
                            cmrdata["submitted"] += cmrdata["on_hand"]
                            cmrdata["on_hand"] = 0
                            cmrdata["samples"] = 0

                               
                        # === Update overlay text ===
                        var.set(
                            # f"{current_cmr} {TARGET_GENUS} Tracker\n\n"
                            f"Location: {curSystem}\n"
                            f"Distance this jump: {JumpDist}ly\n"
                            # f"Total submitted: {cmrdata['submitted']}\n"
                            # f"Samples To Turn in: {cmrdata['on_hand']}\n"
                            # f"Samples In-Gun: {cmrdata['samples']} of 3\n"
                            f"Jumps Remaining in route: {jumpsRemaining}"
                        )

            time.sleep(1)

        except Exception as e:
            print("Error:", e)
            time.sleep(2)


# === MAIN ===
if __name__ == "__main__":
    root, var = create_overlay()
    t = threading.Thread( target=scan_journals, args=(var,), daemon=True)
    t.start()
    root.mainloop()
