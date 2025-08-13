import requests
import re

START_TIME = str(input("INPUT DESIRED DATE (yyyy-mm-dd)\n"))

url = "https://ssd.jpl.nasa.gov/api/horizons.api"
params = {
    "format": "text",
    "COMMAND": "'499'",           # Mars
    "CENTER": "'500@10'",         # Sun as reference
    "MAKE_EPHEM": "YES",
    "EPHEM_TYPE": "VECTORS",     # Cartesian state vectors
    "START_TIME": "'2025-08-12'",
    "STOP_TIME": "'2025-08-13'",
    "STEP_SIZE": "'1d'",
}

response = requests.get(url, params=params)
data = response.text
print(data)
# Extract lines after $$SOE
lines = data.splitlines()
start_idx = next(i for i, line in enumerate(lines) if "$$SOE" in line) + 1


x = y = z = vx = vy = vz = None
for line in lines[start_idx:]:
    if line.startswith(" X ="):
        numbers = re.findall(r"[-+]?\d*\.\d+E[+-]\d+", line)
        x, y, z = map(float, numbers)
    elif line.startswith(" VX="):
        numbers = re.findall(r"[-+]?\d*\.\d+E[+-]\d+", line)
        vx, vy, vz = map(float, numbers)
        break  # Stop after first velocity line—first day done



KM_TO_M = 1000
x, y, z, = x*KM_TO_M, y*KM_TO_M, z*KM_TO_M
vx, vy, vz, = vx*KM_TO_M, vy*KM_TO_M, vz*KM_TO_M
print("Position:", x, y, z)
print("Velocity:", vx, vy, vz)
