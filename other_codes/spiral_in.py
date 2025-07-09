from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed, OffboardError, Attitude
import asyncio
import math

def haversine_distance_m(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

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
async def move_forward(drone:System, distance:float, speed=8):
    duration= distance/speed
    # print("Move forward duration:", duration )
    # duration= int(duration)+1
    # for _ in range(10*duration):  # 10 Hz for 15 seconds
    #     await drone.offboard.set_velocity_body(
    #         VelocityBodyYawspeed(forward_m_s=speed, right_m_s=0, down_m_s=0, yawspeed_deg_s=0)
    #     )
    #     await asyncio.sleep(0.1)

    #stop movement
    print("Going forward in body coordinates...")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(speed, 0.0, 0.0, 0.0))
    await asyncio.sleep(1.25*duration)
    print("Stopping forward movement!")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(2)
async def get_current_yaw(drone):
    async for euler in drone.telemetry.attitude_euler():
        current_yaw = euler.yaw_deg
        return current_yaw
    
async def yaw_by_angle(drone:System, delta_deg):
    # Get current yaw from attitude_euler
    print("Yawing by angle...")
    current_yaw= await get_current_yaw(drone)
    target_yaw = (current_yaw + delta_deg) % 360
    yaw_error = delta_deg

    while(True):
        
        if(abs(yaw_error)<10):
            break
        await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0,0,0, 20))
        await asyncio.sleep(0.1)
        current_yaw= await get_current_yaw(drone)
        yaw_error = (target_yaw - current_yaw + 540) % 360 - 180      #normalize between -180 and 180   
        
    #await yaw_to_heading(drone, target_yaw)
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0,0,0,0))
    await asyncio.sleep(2)

async def orbit(drone:System, x_0, y_0, speed=6):
    print("Started Orbitting")
    async for position in drone.telemetry.position():
        x= position.latitude_deg
        y= position.longitude_deg
        break
    radius= haversine_distance_m(x,y, x_0, y_0)
    print(radius)
    angular_speed= math.degrees(speed/radius)
    duration= 360/angular_speed
    print("Flying Circles in sideways...")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, -speed, 0.0, angular_speed))
    await asyncio.sleep(1.75*duration)

    #stop orbitting
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0,0,0,0))
    await asyncio.sleep(2)

    # await drone.offboard.set_velocity_body(
    #     VelocityBodyYawspeed(0.0, -5.0, 0.0, 30.0))
    # await asyncio.sleep(15)



async def main():
    radius= 110
    drone = System()
    x0, y0= await get_geofence_center()
    await initialize_drone(drone)
    await move_forward(drone, radius, speed=10)

    #turn around 180 degrees
    await  yaw_by_angle(drone, 180)
    #orbit
    for i in range(3):
        await orbit(drone, x0, y0, speed=5)
        await move_forward(drone, radius/4, speed=10)
    await drone.offboard.stop()

asyncio.run(main())



