import asyncio
import math
from mavsdk import System
from mavsdk.offboard import PositionNedYaw

def rad2deg(r):
    return r * 180.0 / math.pi

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