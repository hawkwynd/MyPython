# api call to edastro, obtain all rare POIs from API

import requests
import json
import os 
import sys


regionWanted = []
DATAFOLDER = "./gec_by_region"

# create data folder if not exists
os.makedirs(DATAFOLDER, exist_ok=True )


# flush data folder of txt files before creating new ones.
try:
    for filename in os.listdir(DATAFOLDER):
        if filename.endswith(".txt") or filename.endswith(".json"):
            file_path = os.path.join(DATAFOLDER, filename)
            os.remove(file_path)
except FileNotFoundError:
        print(f"Error: Folder not found at '{DATAFOLDER}'")
except Exception as e:
        print(f"An error occurred: {e}")


# call edastro api and overwrite .json file in data directory
try:

    # response = requests.get("https://edastro.com/gec/json/rare")
    response = requests.get("https://edastro.com/gec/json/all")
    
    if response.status_code == 200:
        data = response.json()
        output_json_filename = os.path.join(DATAFOLDER,'rare-edastro-gec.json')

        with open(output_json_filename, 'w') as f:
            json.dump(data, f, indent=4) # indent for pretty-printing
            # print(f"JSON data saved to {output_filename}")
    else:

        print(f"Error: request failure with status code {response.status_code}")
        print(f"Response text: {response.text}")

except  requests.exceptions.RequestException as e:
    print(f"An error was discovered during the request: {e}")


# iterate data and collect regions
my_regions = regionWanted
for item in data:
     if item not in my_regions:
          my_regions.append(item['region'])


# store my_regions as json file in data_all directory
file_path = os.path.join(DATAFOLDER, 'my_regions.json')

# remove duplicates from my_regions
unique_regions = list(set(my_regions))
regionCount = len(unique_regions)

# Display count of regions to process
print(f"processing {regionCount} regions")

with open(file_path, 'w') as json_file:
     json.dump(unique_regions, json_file, indent=4)

# iterate my_regions and write data to region file
for region in my_regions:
    
    # print(f"Region Processed:{region}")
    poi_list_filename = os.path.join(DATAFOLDER, f"{region}.txt")
    index = 1 

    for item in data:
        if region in item['region']:
            
            # append to region txt file
            with open(poi_list_filename, 'a', encoding="utf-8") as p:
                p.write(f"{str(index)} Region: {item['region']}\nSystem: {item['galMapSearch']}\nName: {item['name']}\nRating: {item['rating']} Type: {item['type']}\nSummary: {item['summary']}\n\n")

            index += 1