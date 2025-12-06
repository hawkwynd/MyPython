import os
import json
import time
import threading
from datetime import datetime
from decimal import Decimal, ROUND_UP

DATAFOLDER = "./bios_found"

# create data folder if not exists
os.makedirs(DATAFOLDER, exist_ok=True )
# flush data folder of txt and json files before creating new ones.
try:
    for filename in os.listdir(DATAFOLDER):
        if filename.endswith(".txt") or filename.endswith(".json"):
            file_path = os.path.join(DATAFOLDER, filename)
            os.remove(file_path)
except FileNotFoundError:
        print(f"Error: Folder not found at '{DATAFOLDER}'")
except Exception as e:
        print(f"An error occurred: {e}")


# === CONFIG ===
JOURNAL_FOLDER = os.path.expanduser(
    "~/Saved Games/Frontier Developments/Elite Dangerous/"
)

# Get the current datetime object
now = datetime.now()

# Extract the month as an integer (1-12)
current_month_number = now.month

current_year = now.year

# go back a month and we'll dig in there for data.
last_month = current_month_number -1

# Extract todays date day as an integer (1-31)
# current_day = now.day 
current_day_with_leading_zero = now.strftime('%d')

# JOURNAL_PREFIX = f"Journal.2025-{current_month_number}"

# Using last months logs because December is so new, I haven't done any bio samples yet
# JOURNAL_PREFIX = f"Journal.{current_year}-{last_month}"
JOURNAL_PREFIX = f"Journal.{current_year}-"

# uncomment the next line if you only want todays logs scanned
# JOURNAL_PREFIX = f"Journal.2025-{last_month}-{current_day_with_leading_zero}"

# Track processed lines
processed = set()

OUTPUT_FILENAME = f"{current_year}-{last_month}-biological-signals.txt"
FULL_OUTPUT_PATH = os.path.join(DATAFOLDER, OUTPUT_FILENAME)


def round_up_to_two_decimals(number):
    """
    Rounds a number up to two decimal places.
    """
    two_places = Decimal('0.01')  # Represents the precision of two decimal places
    return Decimal(str(number)).quantize(two_places, rounding=ROUND_UP)


def scanJournals():
    # while True:
			
        try:
            currentFile = ""

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
                        
                        
                        if ev == "SAASignalsFound":
                            bodyName = event.get("BodyName")
                            signals = event.get("Signals")

                            # SAA_SignalType_Biological
                            for signal in signals:
                                
                                # open the data file and begin writing data to it. 
                                with open(FULL_OUTPUT_PATH, 'a', encoding="utf-8") as p:
                                    # Only use biological signal type
                                    if "Biological" in signal['Type']:
                                            
                                            # create a timestamp which is a header to seperate 
                                            # grouping of samples based on the current logfile 
                                            # we are reading 

                                            if currentFile != fname:
                                                currentFile = fname
                                                parts = currentFile.split('T')
                                                dateStamp = parts[0].split('.')
                                                p.write(f"{dateStamp[1]}\n\n")

                                            # write body name to file
                                            p.write(f"{bodyName}\n")
                                            
                                            # get signal counter
                                            count = signal['Count']
                                         
                                            # get the genuses of the signal
                                            Genuses = event.get("Genuses")
                                        
                                            # iterate the list of genus objects and write the genus and count to file
                                            for genus in Genuses:
                                                p.write(f"{genus['Genus_Localised']}:{count}\n")
                                    
                                            # add a newline to seperate grouping in the file
                                            p.write("\n")
                                    

        except Exception as e:
            print("Error:", e)
            time.sleep(2)


# Lets fire the weapon, Mr. Sulu!

print(f"Reading journal files... writing to {filename}")
scanJournals()
print(f"All done. Check the {DATAFOLDER} folder for a list of files.")