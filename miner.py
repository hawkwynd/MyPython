import os
import json
import time
import threading
from datetime import datetime
from decimal import Decimal, ROUND_UP


# === CONFIG ===
JOURNAL_FOLDER = os.path.expanduser(
    "~/Saved Games/Frontier Developments/Elite Dangerous/"
)

# Get the current datetime object
now = datetime.now()

# Extract the month as an integer (1-12)
current_month_number = now.month
# Extract todays date day as an integer (1-31)
# current_day = now.day 
current_day_with_leading_zero = now.strftime('%d')

# Journal.2025-11-18xxxxxxxx.log (limit to todays logs, else we're loading the whole months worth...)
# JOURNAL_PREFIX = f"Journal.2025-{current_month_number}-{current_day}"
JOURNAL_PREFIX = f"Journal.2025-{current_month_number}-{current_day_with_leading_zero}T"

# Track processed lines
processed = set()


def round_up_to_two_decimals(number):
    """
    Rounds a number up to two decimal places.
    """
    two_places = Decimal('0.01')  # Represents the precision of two decimal places
    return Decimal(str(number)).quantize(two_places, rounding=ROUND_UP)


def scanJournals():
    # while True:
			
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
                        
                        if ev == "ProspectedAsteroid":
                            materials = event.get("Materials")
                            # print(materials)
                            for m in materials:
                                if m['Name'] == "tritium":
                                    content = event.get("Content_Localised")
                                    prop = round_up_to_two_decimals(m['Proportion'])
                                    print(f"Tritium: {prop}% {content}" )

        except Exception as e:
            print("Error:", e)
            time.sleep(2)


scanJournals()