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
    await asyncio.sleep(5)

    print("Starting Offboard mode...")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -3.0, 0.0))
    await drone.offboard.start()

    # Spiral up
    radius = 5.0
    total_turns = 4
    height_per_turn = 2.0
    hz = 20
    duration = 20  # seconds for full spiral
    steps = duration * hz

    print("Spiraling up...")
    for i in range(steps):
        t = 2 * math.pi * total_turns * i / steps  # angle
        x = radius * math.cos(t)
        y = radius * math.sin(t)
        z = -3.0 - (height_per_turn * total_turns) * (i / steps)  # NED: up = more negative
        yaw_deg = math.degrees(t)
        await drone.offboard.set_position_ned(PositionNedYaw(x, y, z, yaw_deg))
        await asyncio.sleep(1 / hz)

    print("Spiraling down...")
    for i in range(steps):
        t = 2 * math.pi * total_turns * i / steps
        x = radius * math.cos(t)
        y = radius * math.sin(t)
        z = -3.0 - (height_per_turn * total_turns) + (height_per_turn * total_turns) * (i / steps)
        yaw_deg = math.degrees(t)
        await drone.offboard.set_position_ned(PositionNedYaw(x, y, z, yaw_deg))
        await asyncio.sleep(1 / hz)

    print("Stopping offboard mode")
    await drone.offboard.stop()
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())