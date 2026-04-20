import os
import sys
import json
import time
import threading
import tkinter as tk
from tkinter import StringVar
from datetime import datetime
import requests


# === CONFIG ===
JOURNAL_FOLDER = os.path.expanduser(
    "~/Saved Games/Frontier Developments/Elite Dangerous/"
)

NAVROUTE_FILE = "navroute.json"
EDSM_LOG_FOLDER = "./route_log"
HISTORY_LOG_FODLER = EDSM_LOG_FOLDER
RING_LOG_FOLDER = EDSM_LOG_FOLDER
RING_LOG_FILE = "rings_log.json"


os.makedirs(EDSM_LOG_FOLDER, exist_ok=True )

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
EDSM_LOG_PREFIX = f"edsm.log.{current_year}-{current_month_number}-{current_day_with_leading_zero}.json"
HISTORY_LOG_PREFIX = f"history.log.{current_year}.json"

# === PER-COMMANDER COUNTERS ===
commanders = {}

# Track processed lines
processed = set()

# array of scoopable stars
scoopableStarTypes = ['O', 'B', 'A', 'F', 'G', 'K', 'M' ]

def fuelPercentage( level ):
    percentage = (level/16) * 100

    return f"{percentage:.0f}"


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
    var.set( f"{pretty_date}\nWaiting for data\n" )

    label = tk.Label(
        root,
        textvariable=var,
        font=("Euro Caps", 10, "normal"),
        fg="cyan",
        bg="black",
        padx=10,      # widened
        pady=10,
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

# submit push to pushURL with system name for insert of new system in db
def pushToFourth( system ):

    if system:

        pushUrl = f"https://www.afourthdimension.com/projects/eliteDangerous/edsm/results.php?sysName={system}"
        response = requests.get(pushUrl)
    
        if response.status_code == 200:
            print(f"{system} pushed successfully.")
            return True
        else:
            print(f"{system} was not successfully pushed!")
            return False
    else:
        return False
    

def inEDSM(system):
    
    edsmUrl = f"https://www.edsm.net/api-system-v1/bodies?systemName={system}"
    response = requests.get(edsmUrl)
    discovery_commander = None
    disovery_date = None 

    if response.status_code == 200:

        print(f"Getting EDSM results from {system}")

        data = response.json()

        if data:

            # save EDSM response to log
            output_json_filename = os.path.join(EDSM_LOG_FOLDER,EDSM_LOG_PREFIX)
            
            write_historyJson(output_json_filename, data)
            print(f"Updated {output_json_filename}")

        else:
            print(f"{system} is NOT in EDSM")
            return False
        
    else:
        return False


def load_navroute():
    navpath = os.path.join(JOURNAL_FOLDER, NAVROUTE_FILE)
    print(f"loading {navpath}")

    with open(navpath, "r", encoding="utf-8") as navfile:
        nav_dict = json.load(navfile)
        jumpCount = len(nav_dict['Route'])

        print(f"{jumpCount} jumps in navroute")




def writeHistoryLog( data ):

    # print(data)

    logPayload = {}
    logPayload['timestamp']     = data['timestamp']
    logPayload['StarSystem']    = data['StarSystem']
    
    if "StarClass" in data:
        logPayload['StarClass']     = data['StarClass']

    if "discovery" in data:
        logPayload['discovery']     = data['discovery']
        
    logPayload['bodyCount']     = data['bodyCount']
    logPayload["bodies"]        = data['bodies']

    output_json_filename = os.path.join(HISTORY_LOG_FODLER,HISTORY_LOG_PREFIX)

    # read in the history into a dict and append logPayload
    write_historyJson(output_json_filename, logPayload)
    
    print(f"History log updated for {logPayload['StarSystem']}")
    historyPayload = {}


def write_historyJson(filename, new_data):

    # Check if file is empty or doesn't exist
    if not os.path.isfile(filename) or os.path.getsize(filename) == 0:
        # if empty, start with a list containing the new data
        data_to_write = [new_data]
    else:
        # if not empty, read existing data
        with open(filename, 'r+') as file:
            existing_data = json.load(file)
        
        # check if the existing data is a list and append
        if isinstance(existing_data, list):
            existing_data.append(new_data)
            data_to_write = existing_data
        else:
            #handle error
            print(f"Error: JSON file '{filename}' does not contain a list")
            return
    
    # Write the entire updated data back into the file, overwriting the entire file with the new data.
    with open(filename, 'w') as file:
        json.dump(data_to_write, file, indent=4)



# === JOURNAL SCANNER ===
def scan_journals( var ):

    global commanders
    
    curSystem = str()
    jumpsRemaining = int()
    JumpDist = int()
    StarClass = str()
    NextSystemText = str()
    NextSystemName = str()
    JumpTime = False
    NextJump = False
    isInEDSM = False
    discoveryStatus = str()
    scoopable = None
    FuelLevel = str()
    location = str()
    jumpsRemainingText = ""
    pushed = False
    historyPayload = {}
    bodies = []
    bodydata = {}
    FSSFlag = None 
    

    while True:
               
        try:
            files = [
                f for f in os.listdir( JOURNAL_FOLDER )
                if f.startswith( JOURNAL_PREFIX )
            ]
            
            # reverse sort to get the last file if more than one 
            # are on the same JOURNAL_PREFIX 

            files.sort( reverse=True )

            for fname in files:
                path = os.path.join( JOURNAL_FOLDER, fname )
                print(f"Opening journal for read: {path}")

                with open(path, "r", encoding="utf-8") as f:

                    loglines = follow(f)
                    
                    for raw in loglines:

                        line = raw.strip()
                        if not line.startswith("{"):
                            continue

                        try:
                            event = json.loads(line)
                            

                        except:
                            continue

                        ev = event.get("event")

                        if ev == "Shutdown":
                            sys.exit()
                        
                        if ev == "Scan" and event.get("ScanType") == "AutoScan":
                            # refresh location starsystem
                            location = f"Location:{event.get("StarSystem")}"
                            historyPayload["StarSystem"] = event.get("StarSystem")
                            
                            if "StarType" in event:
                                historyPayload["StarClass"] = f"{event.get("StarType")} {event.get("Luminosity")}"

                        if ev == "FSDJump":
                            location = f"Location: {event.get("StarSystem")} {round(event.get("JumpDist"))}ly"
                            FuelLevel = f"Fuel: { round(event.get("FuelLevel"))}"

                            historyPayload["JumpDist"]      = round(event.get("JumpDist"))
                            historyPayload["StarSystem"]    = event.get("StarSystem")
                            bodydata["BodyName"]            = event.get("Body")
                            bodydata["PlanetClass"]         = event.get("BodyType")
                        

                        if ev == "SAASignalsFound":
                            bodydata['Signals'] = event.get("Signals")


                        if ev == "Scan" and event.get("ScanType") == "Detailed":
                            
                            if "PlanetClass" in event:
                            #    historyPayload["StarSystem"] = event.get("StarSystem")
                               bodydata["bodyID"]         = event.get("BodyID")
                               bodydata["BodyName"]       = event.get("BodyName")
                               bodydata["PlanetClass"]    = event.get("PlanetClass")
                               bodydata["landable"]       = event.get("Landable")
                               bodydata["SurfaceGravity"] = event.get("SurfaceGravity")

                            if "Rings" in event:
                                bodydata["Rings"] = event.get("Rings")


                            if bodydata:
                                bodies.append(bodydata)
                                # print(bodydata)
                                # empty bodydata array for next body
                                bodydata = {}
                            

                        # update fuel level display
                        if ev == "FuelScoop":
                            FuelLevel = f"Fuel: {round(event.get("Total"))}"
                        if ev == "ReservoirReplenished":
                            FuelLevel = f"Fuel: {round(event.get("FuelMain"))}"

                        # when jumping update location and push system to 4th
                        if ev == "StartJump" and event.get("JumpType") == "Hyperspace":
                            pushed   = False 
                            location = f"Jumping to {event.get("StarSystem")}"
                            NextSystemText = ""
                            pushed   = pushToFourth( event.get("StarSystem") ) 
                            print(f"{location} pushed successfully at StartJump.")
                            
                        if ev == "NavRoute":
                            n = load_navroute()

                        if ev == "NavRouteClear":
                            location = f"Location: {curSystem}"
                            NextSystemText = ""
                            jumpsRemainingText = ""
                            discoveryStatus = ""

                        # get cursystem when scanning to update location
                        if ev == "Scan" and event.get("ScanType") == "Detailed":
                            curSystem = event.get("StarSystem")
                            location = f"Location: {curSystem}"

                        # Discovery Scan - set location HONK
                        if ev == "FSSDiscoveryScan":
                            historyPayload["StarSystem"] = event.get("SystemName")
                            curSystem = event.get("SystemName")
                            location = f"Location: {curSystem}"

                        # FSDTarget
                        # { "timestamp":"2026-04-08T15:44:17Z", "event":"FSDTarget", "Name":"Roefoea YB-S d5-10", "SystemAddress":356524202547, "StarClass":"F" }
                        
                        if ev == "FSDTarget":
                            NextSystemName = event.get("Name")
                            NextSystemText = f"Next: {NextSystemName}"

                            historyPayload["StarSystem"] = event.get("Name")
                            historyPayload["timestamp"] = event.get("timestamp")
                            historyPayload["StarClass"] = event.get("StarClass")

                            if event.get("RemainingJumpsInRoute") is not None:
                                jumpsRemaining = event.get("RemainingJumpsInRoute")
                                jumpsRemainingText = f"Jumps: {jumpsRemaining}"
                            else:
                                jumpsRemainingText = ""
                                # if jumpsRemaining > 1 :
                            
                                #   else:
                                
                                #     jumpsRemainingText = "No Jumps set"
                                
                                if curSystem != NextSystemName:
                                    # NextSystemText = ""
                                    discoveryStatus = ""

                            isInEDSM = inEDSM( NextSystemName )
                            
                            if not isInEDSM :
                                discoveryStatus  = "Undiscovered"
                                historyDiscovery = "Undiscovered"
                            else:
                                historyDiscovery = {}
                                discoveredBy = f"{isInEDSM['discovery']['commander']}"
                                discoveryDt  = f"{isInEDSM['discovery']['date']}"
                                discoveryStatus = f"{discoveredBy} {discoveryDt}"
                                historyDiscovery["commander"] = discoveredBy
                                historyDiscovery["date"] = discoveryDt

        
                            StarClass = event.get("StarClass")
                            scoopable = "*" if StarClass in scoopableStarTypes else ""

                            historyPayload['discovery'] = historyDiscovery
                            
                        # === grab system name when jumping into it ===
											
                        # On completion of scanning a system Lets write to the historyLog
                        if ev == "FSSAllBodiesFound" and FSSFlag == None:
                            FSSFlag = True
                            Count = event.get("Count")
                            historyPayload["bodyCount"] = Count
                            
                            # if we have the Star system in historyPayload, we can write the array
                            if historyPayload["StarSystem"]:
                                historyPayload["timestamp"] = event.get("timestamp")
                                historyPayload["bodies"] = bodies
                                bodies = []

                                writeHistoryLog( historyPayload )
                                FSSFlag = None 

                            else:
                                print("There is no StarSystem set... Try again, slapnut")
                               

                            if pushed == False:
                                pushed = pushToFourth( event.get("SystemName") ) 
                                               
                        # === Update overlay text ===
                        var.set(
                            f"{location}\n"
                            f"{FuelLevel}\n"
                            f"{NextSystemText}\n"
                            f"{discoveryStatus}\n"
                            f"{jumpsRemainingText}"
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
