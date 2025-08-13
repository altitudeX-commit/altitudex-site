import time
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim

# -----------------------------
# 1. Function: calculate distance between 2 GPS points
# -----------------------------
def distance(coord1, coord2):
    R = 6371  # Earth radius in km
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  # distance in km

# -----------------------------
# 2. Function: convert address → GPS coordinates
# -----------------------------
def get_coordinates(address):
    geolocator = Nominatim(user_agent="drone_delivery")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        raise ValueError("Address not found!")

# -----------------------------
# 3. Ask user for delivery address
# -----------------------------
address = input("Enter delivery address: ")
destination = get_coordinates(address)

# Define charging station (home base)
charging_station = (51.5074, -0.1278)  # Example: London center
drone_position = list(charging_station)

print(f"\nCharging station: {charging_station}")
print(f"Destination: {destination}\n")

# -----------------------------
# 4. Function: simulate drone flight
# -----------------------------
def fly_to(target):
    global drone_position
    while distance(drone_position, target) > 0.1:  # stop within 100 m
        print(f"Drone at {drone_position}, {distance(drone_position, target):.2f} km to go")
        # Move 10% closer each loop
        drone_position[0] += (target[0] - drone_position[0]) * 0.1
        drone_position[1] += (target[1] - drone_position[1]) * 0.1
        time.sleep(1)
    print("Arrived!\n")

# -----------------------------
# 5. Run the mission
# -----------------------------
print("Flying to destination...")
fly_to(destination)

print("Flying back to charging station...")
fly_to(charging_station)

print("Mission complete!")