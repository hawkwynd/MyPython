import os
import re
from datetime import datetime
from pathlib import Path
import shutil


DATAFOLDER = "D:/Elite Dangerous/Archived 2023 Screenshots"
OUTFOLDER  = "D:/Elite Dangerous/Renamed"

os.makedirs(OUTFOLDER, exist_ok=True)

for index, filename in enumerate( os.listdir(DATAFOLDER) ):
     if filename.endswith(".jpg"):

        file_path = Path(os.path.join(DATAFOLDER, filename))
        ctime     = os.path.getmtime(file_path)

        timestamp = datetime.fromtimestamp(ctime)
        formatted_time = timestamp.strftime("%Y-%m-%d")

        # split on the @ sign in the filename
        part2               = filename.split('@') # 
        result_with_letter  = re.split(r'(?=[a-zA-Z])', part2[0], maxsplit=1)
        stripped            = f'{result_with_letter[1].replace("(HighRes)", "").strip()}-'
        
        destination_path = Path(os.path.join(OUTFOLDER, f'{stripped}{index}.jpg'))

        # print( destination_path )

        try:
            # Copy the file to the new location with the new name
            shutil.copy2(file_path, destination_path)
            print(f"File copied and renamed successfully to: {destination_path}")
        except FileNotFoundError:
            print(f"Error: The source file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")


