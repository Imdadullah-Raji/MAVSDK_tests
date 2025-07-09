import asyncio
import math
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected!")
            break

    print("Arming...")
    await drone.action.arm()

    print("Taking off...")
    await drone.action.takeoff()
    await asyncio.sleep(8)

    print("Starting Offboard mode...")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -3.0, 0.0))
    await drone.offboard.start()

    # Spiral in while going up
    radius_start = 6.0
    radius_end = 2.0
    total_turns = 2
    height_per_turn = 2
    hz = 20
    duration = 20  # seconds for spiral
    steps = duration * hz

    print("Spiraling in & up...")
    for i in range(steps):
        t = 2 * math.pi * total_turns * i / steps  # angle
        r = radius_start - (radius_start - radius_end) * (i / steps)
        x = r * math.cos(t)
        y = r * math.sin(t)
        z = -3.0 - (height_per_turn * total_turns) * (i / steps)
        yaw_deg = math.degrees(t)
        await drone.offboard.set_position_ned(PositionNedYaw(x, y, z, yaw_deg))
        await asyncio.sleep(1 / hz)

    print("Spiraling out & down...")
    for i in range(steps):
        t = 2 * math.pi * total_turns * i / steps
        r = radius_end + (radius_start - radius_end) * (i / steps)
        x = r * math.cos(t)
        y = r * math.sin(t)
        z = -3.0 - (height_per_turn * total_turns) + (height_per_turn * total_turns) * (i / steps)
        yaw_deg = math.degrees(t)
        await drone.offboard.set_position_ned(PositionNedYaw(x, y, z, yaw_deg))
        await asyncio.sleep(1 / hz)

    print("Stopping offboard mode")
    await drone.offboard.stop()
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())