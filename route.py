import os
import json
import requests
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
current_month_number = now.strftime('%m')
current_year = now.year 

# Extract todays date day as an integer (1-31)
current_day = now.day 
current_day_with_leading_zero = now.strftime('%d')
pretty_date = now.strftime('%m/%d/%y')
# Journal.2025-11-18xxxxxxxx.log (limit to todays logs, else we're loading the whole months worth...)
# JOURNAL_PREFIX = f"Journal.2025-{current_month_number}-{current_day}"

JOURNAL_PREFIX = f"Journal.{current_year}-{current_month_number}-{current_day_with_leading_zero}"

# The targeted biological genus.
TARGET_GENUS = "Radicoida"

# === PER-COMMANDER COUNTERS ===
commanders = {}

# Track processed lines
processed = set()

# array of scoopable stars
scoopableStarTypes = ['O', 'B', 'A', 'F', 'G', 'K', 'M' ]

def follow(thefile):
    # Seek to the end of the file
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            # Sleep briefly when no new data is found
            time.sleep(0.1)
            continue
        yield line

# === DRAGGABLE OVERLAY ===
def create_overlay():
    root = tk.Tk()
    root.title("Router")
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.attributes("-alpha", 0.80)

    # Move overlay left so extra text fits
    root.geometry("+30+400")
    
    # Esc key exits the application
    root.bind("<Escape>", lambda e: root.destroy())

    var = StringVar()
    var.set( f"{pretty_date}\nWaiting for data" )

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
    StarClass = ""
    NextSystemName = ""
    JumpTime = False
    NextJump = False
    ThisSystem = None 

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
                    loglines = follow(f)
                    
                    for raw in loglines:
                        # if raw in processed:
                        #     continue
                        # processed.add(raw)

                        line = raw.strip()
                        if not line.startswith("{"):
                            continue

                        try:
                            event = json.loads(line)

                        except:
                            continue

                        ev = event.get("event")


                        if ev == "FSSAllBodiesFound" or ev == "FSSDiscoveryScan" and ThisSystem == None:
                            
                            sn = event.get("SystemName")
                            url = f"https://www.afourthdimension.com/projects/eliteDangerous/edsm/results.php?sysName={event.get("SystemName")}"
                            response = requests.get(url)
                            
                            if response.status_code == 200:
                                print(f'FSSAllBodiesFound sent request for {sn}')
                                ThisSystem = event.get("SystemName")

                            else:
                                print(response.status_code)
                        
                        # FSDTarget
                        if ev == "FSDTarget":

                            jumpsRemaining = event.get("RemainingJumpsInRoute")
                            NextSystemName = event.get("Name")
                            # print(NextSystemName)
                            StarClass = event.get("StarClass")
                            scoopable = "*" if StarClass in scoopableStarTypes else ""


                        # === grab system name when jumping into it ===
                        if ev == "FSDJump":
                             jumpsRemaining = (jumpsRemaining -1) if jumpsRemaining == 1 else jumpsRemaining
                             curSystem = event.get("StarSystem")
                             JumpDist = round( event.get("JumpDist") )
											
                        if ev == "CarrierJumpRequest":
                            NextJump = event.get("SystemName")
                            JumpTime = event.get("DepartureTime")

                        # === Update overlay text ===
                        if JumpDist > 0:
                            var.set(
                                f"Location: {curSystem} ({JumpDist}ly)\n"
                                f"Next: {NextSystemName} ({StarClass}) {scoopable}\n"
                                f"Jumps remaining: {jumpsRemaining}"
                            )   
                        else:
                            if JumpTime:
                                var.set(
                                    f"Carrier jump to: {NextJump}\n"
                                    f"Schedule: {JumpTime}"
                                )
                        

            time.sleep(2)

        except Exception as e:
            print("Error:", e)
            time.sleep(2)


# === MAIN ===
if __name__ == "__main__":
    root, var = create_overlay()
    t = threading.Thread( target=scan_journals, args=(var,), daemon=True)
    t.start()
    root.mainloop()
