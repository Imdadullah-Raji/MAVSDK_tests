import asyncio
from mavsdk import System
import math
from mavsdk.mission import MissionItem

# Target: South-East corner of BUET central Field
TARGET_LAT = 23.725091 
TARGET_LON = 90.395163
TARGET_ALT = 10.0  
TAKEOFF_ALT = 5.0
CRUISE_SPEED = 2.0  

# Function to calculate distance between two GPS coords in meters
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

async def wait_until_arrived(drone, target_lat, target_lon, target_alt, pos_tol=1.5, alt_tol=1):
    """
    Wait until drone is within pos_tol (meters) and alt_tol (meters) of target.
    """
    async for pos in drone.telemetry.position():
        dist = haversine_distance(pos.latitude_deg, pos.longitude_deg, target_lat, target_lon)
        alt_diff = abs(pos.relative_altitude_m - target_alt)

        if dist <= pos_tol and alt_diff <= alt_tol:
            print(f"Arrived at target (distance: {dist:.2f} m, altitude diff: {alt_diff:.2f} m)")
            break

async def run():
    drone = System()
    await drone.connect(system_address='serial:///dev/ttyAMA0')  

    print("Waiting for drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break

    print("Waiting for global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate ok")
            break

    # Set the cruise speed (max horizontal speed)
    print(f"Setting max speed to {CRUISE_SPEED} m/s...")
    #await drone.action.set_maximum_speed(CRUISE_SPEED)
    await drone.action.set_current_speed(CRUISE_SPEED)

    # Arm and takeoff
    print("Arming...")
    await drone.action.arm()
    await drone.action.set_takeoff_altitude(TAKEOFF_ALT)
    print(f"Taking off to {TAKEOFF_ALT} meters...")
    await drone.action.takeoff()
    await asyncio.sleep(20)  # wait for takeoff

    # Fly to GPS location
    print(f"Going to: {TARGET_LAT}, {TARGET_LON}, {TARGET_ALT}m")
    await drone.action.goto_location(TARGET_LAT, TARGET_LON, TARGET_ALT, 0)

    # Wait a bit before landing
    await wait_until_arrived(target_lat=TARGET_LAT, target_lon=TARGET_LON, target_alt=TARGET_ALT)

    print("Landing...")
    await drone.action.land()
    
    

    #Wait until landed
    # async for in_air in drone.telemetry.in_air():
    #     if not in_air:
    #         print("Landed.")
    #         break

    await asyncio.sleep(30)
    
    await drone.action.disarm()
    print("Disarmed.")

if __name__ == "__main__":
    asyncio.run(run())
