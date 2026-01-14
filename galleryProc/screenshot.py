import os
import re
from datetime import datetime

# list of directories where our screenshots are kept
DATAFOLDERS = ["D:/Elite Dangerous/Screenshots", "D:/Elite Dangerous/Archived 2023 Screenshots", "D:/Elite Dangerous/Archived Screenshots" ]
# location of dump file
OUTFOLDER  = "./galleryProc"

myFileList = []

now = datetime.now()

print(now.strftime("%Y-%m-%d %H:%M:%S"))

# flush data folder of txt and json files before creating new ones.
try:
    for filename in os.listdir(OUTFOLDER):
        if filename.endswith(".txt"):
            file_path = os.path.join(OUTFOLDER, filename)
            os.remove(file_path)
except FileNotFoundError:
        print(f"Error: Folder not found at '{OUTFOLDER}'")
except Exception as e:
        print(f"An error occurred: {e}")


# Begin processing files in datafolders

try:
     for folder in DATAFOLDERS:
        for filename in os.listdir(folder):
            if filename.endswith(".jpg"):
                
                file_path = os.path.join(folder, filename)
                ctime     = os.path.getmtime(file_path)

                timestamp = datetime.fromtimestamp(ctime)
                formatted_time = timestamp.strftime("%Y-%m-%d")

                part1     = filename.split('.') # drops the .jpg
                part2     = part1[0].split('@') # 
                
                result_with_letter = re.split(r'(?=[a-zA-Z])', part2[0], maxsplit=1)
                stripped = formatted_time + " " + result_with_letter[1].replace("(HighRes)", "").strip()
               
                myFileList.append( stripped )



except FileNotFoundError:
        print(f"Error: Folder not found at '{folder}'")
except Exception as e:
        print(f"An error occurred: {e}")


# remove the duplicates from the list
distinctList = list(set(myFileList))

# Sort oldest to newest
distinctList.sort(reverse=False)

poi_list_filename = os.path.join(OUTFOLDER, "systems.txt")


with open(poi_list_filename, 'a', encoding="utf-8") as p:

    p.write(f'### Last run {now.strftime("%Y-%m-%d %H:%M:%S")} : {len(distinctList)} screenshot systems found ###\n\n')

    for row in distinctList:
      
    #   print(row)
      p.write( row + '\n')


print(f'{poi_list_filename} is ready to view.')