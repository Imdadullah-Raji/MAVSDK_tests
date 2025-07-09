import asyncio
import math
from mavsdk import System
from mavsdk.offboard import  PositionNedYaw

async def run():
    print("hi")
    drone = System()
    await drone.connect()

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected!")
            break

    print("Arming...")
    await drone.action.arm()

    print("Taking off...")
    await drone.action.set_takeoff_altitude(3)
    await drone.action.takeoff()
    await asyncio.sleep(15)

    print("Starting Offboard mode...")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -5.0, 0.0))
    await drone.offboard.start()

    # Generate figure-8 path
    R = 5  # radius
    duration = 20  # seconds for full loop
    hz = 20
    steps = duration * hz

    for i in range(steps):
        t = 2 * math.pi * i / steps  # 0 to 2π
        x = R * math.sin(t)
        y = (R/2) * math.sin(2 * t)
        yaw= math.atan2(-y, -x)*(180/math.pi)
        await drone.offboard.set_position_ned(PositionNedYaw(x, y, -5.0, yaw))
        await asyncio.sleep(1 / hz)

    print("Stopping offboard mode")
    await drone.offboard.stop()
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())