import os
import json
import time
import threading
import requests
import tkinter as tk
from tkinter import StringVar
from datetime import datetime
import pytz

# Shortcut target 
# "pythonw.exe" C:\Users\hawkw\projects\MyPython\weather.pyw"

# create exe for distribution
# python -m PyInstaller --noconsole --onefile .\weather.pyw

# Get the current datetime object
now = datetime.now()
# Extract the month as an integer (1-12)
current_month_number = now.month
current_year = now.year 
# Extract todays date day as an integer (1-31)
current_day = now.day 
current_day_with_leading_zero = now.strftime('%d')
pretty_date = now.strftime('%m/%d/%y %I:%M')
pretty_time = now.strftime('%I:%M')

apiKey          = "d1f8d26f2a1347488a757da2e6011989b45884dd5df14b70bf4106480bd25440"
applicationKey  = "3d6e4c73c0c4420aa1043ae70892357a4d1200e7604543faa3b089a95a7d37ef"
userUrl         = f"https://rt.ambientweather.net/v1/devices?applicationKey={applicationKey}&apiKey={apiKey}"

# Wind Directions
windDirs = ['North', 'NNE', 'NE', 'ENE', 'East', 'ESE', 'SE', 'SSE', 'South', 'SSW', 'SW', 'WSW', 'West', 'WNW', 'NW', 'NNW']

def get_ordinal_suffix(day_num):
    """
    Returns the ordinal suffix for a given day number.
    """
    # Convert to integer if it's not already
    day_num = int(day_num)
    
    # Handle numbers 11-13 specifically, as they all end in 'th'
    if 11 <= (day_num % 100) <= 13:
        suffix = 'th'
    else:
        # Check the last digit
        if day_num % 10 == 1:
            suffix = 'st'
        elif day_num % 10 == 2:
            suffix = 'nd'
        elif day_num % 10 == 3:
            suffix = 'rd'
        else:
            suffix = 'th'
    return suffix



DATAFOLDER = "./weatherData"
# create data folder if not exists
os.makedirs(DATAFOLDER, exist_ok=True )


# === DRAGGABLE OVERLAY ===
def create_overlay():
    root = tk.Tk()
    root.title("Weather Monitor")
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
        root.x = event.x # type: ignore
        root.y = event.y # type: ignore

    def do_move(event):
        x = root.winfo_x() + (event.x - root.x) # type: ignore
        y = root.winfo_y() + (event.y - root.y) # type: ignore
        root.geometry(f"+{x}+{y}")

    label.bind("<Button-1>", start_move)
    label.bind("<B1-Motion>", do_move)
    
    return root, var



def getWeather(var):
    
    while True:
       
        try:

            response = requests.get(userUrl)

            if response.status_code == 200:

                data = response.json()

                for item in data:
                    # Access specific values using keys
                    macAddress  = item['macAddress']
                    lastData    = item['lastData']
                    timestamp   = lastData['date']
                    
                    # Wind
                    windDirection = degreesToCardinal( lastData['winddir_avg10m'])
                    windgustmph   = lastData['windgustmph']

                    #Humidity
                    humidity      = lastData['humidity']

                    #Rainfall
                    hourlyrainin = lastData['hourlyrainin']
                    eventrainin  = lastData['eventrainin']
                    dailyrainin  = lastData['dailyrainin']



                    # dt_object_utc = datetime.fromisoformat(timestamp[:-1]).replace(tzinfo=pytz.utc)
                    dt_object_utc   = datetime.fromisoformat(timestamp)
                    my_timezone     = pytz.timezone('America/Chicago')
                    date_chicago    = dt_object_utc.astimezone(my_timezone)
                    suffix = get_ordinal_suffix(date_chicago.day)
                    formatted_date  = date_chicago.strftime("%A, %b")
                    formatted_time = date_chicago.strftime("%I:%M %p")
                    formatted_date_with_suffix = f"{formatted_date} {date_chicago.day}{suffix} {formatted_time}"

                    # uv_index
                    sky_conditions = uv_index( lastData['uv'])
                
                output_json_filename = os.path.join(DATAFOLDER,'myweather.json')

                with open(output_json_filename, 'w') as f:
                    json.dump(data, f, indent=4) # indent for pretty-printing
                    
                    # print(f"JSON data saved to {output_json_filename} at {formatted_date} began {pretty_time}")
                    todayRain = f"Rain Today: {dailyrainin} Hourly: {hourlyrainin} Now: { eventrainin }"

                    sky_conditions = "Rain" if eventrainin > 0 else sky_conditions

                    var.set(
                        f"{formatted_date_with_suffix}\n"
                        f"Sky: {sky_conditions}\n" 
                        f"Temp: {round(lastData['tempf'])}\u00b0\n"
                        f"Wind: {windDirection} at { round(lastData['windspeedmph'])}mph\n"
                        f"Gust: { round(windgustmph)}mph Max: {round(lastData['maxdailygust'])}mph\n"
                        f"Humidity: {humidity}%\n"
                        f"{todayRain}"
                        )

                
                # repeat every 15 minutes = 900
                time.sleep( 300 )

            else:

                print(f"Error: request failure with status code {response.status_code}")
                print(f"Response text: {response.text}")
                time.sleep(10)

        except  requests.exceptions.RequestException as e:
                print(f"An error was discovered during the request: {e}")



# Convert degrees to string direction from array of directions
def degreesToCardinal(degrees):

    index = (int)((degrees + 11.25) / 22.5) % 16
    return windDirs[index]


def uv_index( uv_index ):

    if uv_index is not None:
        if 0 <= uv_index <= 2:
            sky_condition = "Cloudy"
        elif 3 <= uv_index <= 5:
            sky_condition = "Mostly Cloudy" 
        elif 6<= uv_index <= 7:
            sky_condition = "Sun and Clouds"
        elif 8<= uv_index <= 10:
            sky_condition = "Mostly Sunny"
        else:
            sky_condition = "Extreme UV/Cloud Cover Low"

        return f"{sky_condition}"
    
    else:
        return "UV data not found in measurement"






# Run it all man.

if __name__ == "__main__":
    root, var = create_overlay()

    t = threading.Thread( target=getWeather, args=(var,), daemon=True)

    t.start()
    
    root.mainloop()