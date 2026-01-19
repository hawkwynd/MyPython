import time
import os
import json

JOURNAL_FOLDER = os.path.expanduser("~/Saved Games/Frontier Developments/Elite Dangerous/")
JOURNAL_PREFIX = f"Journal.2026-01-18"

files = [
            f for f in os.listdir( JOURNAL_FOLDER )
                if f.startswith( JOURNAL_PREFIX )
        ]
          

body = ""
files.sort()



def follow(thefile):
    # Seek to the end of the file initially
    thefile.seek(0, os.SEEK_END)
    
    while True:
        line = thefile.readline()
        if not line:
            # If no new line is found, sleep briefly to prevent high CPU usage
            time.sleep(0.1)
            continue
        yield line

if __name__ == "__main__":
    
    for fname in files:
        log_file_path = os.path.join(JOURNAL_FOLDER, fname)
        
    # Open the file in read mode
    with open(log_file_path, "r") as logfile:
        # Iterate over new lines as they are added
        for line in follow(logfile):

            logline = line.strip() # strip newline characters for clean output
            if not line.startswith("{"):
                continue
            try:
               event = json.loads(line)
            except:
                continue

            ev = event.get("event")
            
            if "FSDJump" in ev:
                
                print( event.get("StarSystem"), event.get("StarPos") )
                # print( event )
                

            if "Scan" in ev:
                
                print( event )
               
