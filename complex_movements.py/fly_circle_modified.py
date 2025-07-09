import asyncio
import math
from mavsdk import System
from mavsdk.offboard import PositionNedYaw

def rad2deg(r):
    return r * 180.0 / math.pi

async def wait_until_near_position(drone, target_n, target_e, target_d, tolerance=0.5, timeout_sec=10):
    import time
    start = time.time()
    async for pos in drone.telemetry.position_velocity_ned():
        n = pos.position.north_m
        e = pos.position.east_m
        d = pos.position.down_m

        dist = ((n - target_n)**2 + (e - target_e)**2 + (d - target_d)**2)**0.5
        if dist < tolerance:
            break

        if time.time() - start > timeout_sec:
            print("Warning: Timeout while waiting to reach position.")
            break

        await asyncio.sleep(0.1)

async def run():
    drone = System()
    await drone.connect()

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected!")
            break

    await drone.action.arm()
    await drone.action.set_takeoff_altitude(2.5)
    await drone.action.takeoff()
    await asyncio.sleep(15)

    radius = 6
    altitude = -2.5  # constant height
    hz = 20
    duration = 15    # seconds for full circle
    steps = hz * duration

    # Start Offboard
    await drone.offboard.set_position_ned(PositionNedYaw(radius, 0.0, altitude, 180.0))
    await drone.offboard.start()
    #await wait_until_near_position(drone, radius, 0.0, altitude, 180.0)
    await asyncio.sleep(20)

    # Circular orbit
    for i in range(steps):
        theta = 2 * math.pi * i / steps
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        yaw = rad2deg(math.atan2(-y, -x))  # face center (0,0)
        await drone.offboard.set_position_ned(PositionNedYaw(x, y, altitude, yaw))
        await asyncio.sleep(1 / hz)

    await asyncio.sleep(2)
    await drone.offboard.stop()
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())