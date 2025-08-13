import time
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim

# -----------------------------
# Helper Functions
# -----------------------------

def distance(coord1, coord2):
    """Calculate distance in km between two lat/lon coordinates"""
    R = 6371  # Earth radius in km
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def get_coordinates(address):
    """Convert address string to lat/lon coordinates"""
    geolocator = Nominatim(user_agent="drone_delivery_system")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        raise ValueError("Address not found!")

def calculate_eta_km(distance_km, speed_kmh):
    """Calculate estimated time of arrival in minutes"""
    hours = distance_km / speed_kmh
    return hours * 60

def fly_to(start, target, speed_kmh):
    """Simulate drone flying from start to target"""
    drone_position = list(start)
    while distance(drone_position, target) > 0.05:  # stop within 50m
        dist_left = distance(drone_position, target)
        print(f"Drone at {drone_position}, {dist_left:.2f} km to go")
        # Move 10% closer each loop
        drone_position[0] += (target[0] - drone_position[0]) * 0.1
        drone_position[1] += (target[1] - drone_position[1]) * 0.1
        time.sleep(0.5)
    print(f"Arrived at {target}\n")
    return drone_position

# -----------------------------
# Main Program
# -----------------------------
print("=== AltitudeX Pharmacy Drone Delivery ===")

# Input addresses
pharmacy_address = input("Enter pharmacy address: ")
customer_address = input("Enter customer delivery address: ")

# Get coordinates
pharmacy_coords = get_coordinates(pharmacy_address)
customer_coords = get_coordinates(customer_address)

# Privacy: clear raw text addresses
del pharmacy_address
del customer_address

# Calculate distance
trip_distance = distance(pharmacy_coords, customer_coords)
print(f"\nDelivery distance: {trip_distance:.2f} km")

# Check if within 5 km
if trip_distance > 5:
    print("❌ Delivery not allowed: Destination is more than 5 km from this pharmacy.")
    exit()

# Define legal max altitude and default speed
MAX_ALTITUDE_M = 120  # UK legal height
cruise_speed_kmh = 37.5  # ~23 mph to meet 8 min delivery target

# Calculate ETA
eta_minutes = calculate_eta_km(trip_distance, cruise_speed_kmh)
print(f"Estimated flight time one-way: {eta_minutes:.1f} minutes at {cruise_speed_kmh} km/h")
if eta_minutes <= 8:
    print("✅ Delivery time meets 8-minute target.")
else:
    print("⚠️ Delivery time exceeds 8 minutes target. Consider faster speed if safe/legal.")

# Simulate mission
print("\n🚁 Flying to customer...")
fly_to(pharmacy_coords, customer_coords, cruise_speed_kmh)

print("🚁 Returning to pharmacy...")
fly_to(customer_coords, pharmacy_coords, cruise_speed_kmh)

print("✅ Mission complete! Drone returned safely.")
