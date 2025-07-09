from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed, OffboardError

import random
import asyncio
import math

async def get_geofence_center():
    drone = System()
    await drone.connect()  # or whatever you're using

    print("Waiting for GPS fix...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            break

    async for position in drone.telemetry.position():
        lat_center = position.latitude_deg
        lon_center = position.longitude_deg
        #print(f"Geofence center set at: {lat_center}, {lon_center}")
        return lat_center, lon_center

def haversine_distance_m(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def within_limits(current_lat, current_lon, center_lat, center_lon, radius_m=100):
    return haversine_distance_m(current_lat, current_lon, center_lat, center_lon) <= radius_m

async def initialize_drone(drone:System):
    await drone.connect()
        # wait for position lock
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("GPS locked.")
            break
    await drone.action.arm()
    await drone.action.set_takeoff_altitude(60)
    await drone.action.takeoff()
    await asyncio.sleep(35)
    # START OFFBOARD mode with 0 velocity to prep PX4
    print("Starting offboard control...")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    try:
        await drone.offboard.start()
    except OffboardError as e:
        print(f"Offboard failed to start: {e}")
        await drone.action.disarm()
        return
async def move_forward(drone:System):
    speed= 2
    distance= 10+10*random.random() 
    duration = (distance+5)/speed
    print("Going forward in body coordinates...")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(speed, 0.0, 0.0, 0.0))
    await asyncio.sleep(duration)
    #stop movement
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(2)
async def turn(drone:System):
    angular_speed = 20
    duration = 5*random.random()
    print("Turning")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, angular_speed))
    await asyncio.sleep(duration)
    #stop movement
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0,0.0,0.0,0.0))
    await asyncio.sleep(2)

    



async def main():
    x,y = await get_geofence_center()
    print("x:",x)
    print("y:", y)

    drone = System()
    await initialize_drone(drone)
    for i in range(10):
        await move_forward(drone)
        await turn(drone)
    #stop offboard
    await drone.offboard.stop()

    await drone.action.land()



asyncio.run(main())