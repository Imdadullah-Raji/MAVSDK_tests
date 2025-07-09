import asyncio
import math
from mavsdk import System
from mavsdk.offboard import PositionNedYaw

async def run():
    drone = System()
    await drone.connect()

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected!")
            break

    await drone.action.arm()
    await drone.action.set_takeoff_altitude(4)
    await drone.action.takeoff()
    await asyncio.sleep(8)

    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -4.0, 0.0))
    await drone.offboard.start()

    # Fly Out on Arc
    print("Flying out (boomerang forward)...")
    a, b = 10, 5   # a = length, b = lateral deviation
    hz = 20
    steps = hz * 5
    for i in range(steps):
        t = math.pi * i / steps  # 0 → π
        x = a * math.cos(t) - a  # shift to start at x=0
        y = b * math.sin(t)
        await drone.offboard.set_position_ned(PositionNedYaw(x, y, -4.0, 0.0))
        await asyncio.sleep(1 / hz)

    # Snap Turn 180°
    print("Snap 180°")
    await drone.offboard.set_position_ned(PositionNedYaw(x, y, -4.0, 180.0))
    await asyncio.sleep(2)

    # Fly Back on Mirror Arc
    print("Flying back (boomerang return)...")
    for i in range(steps):
        t = math.pi * (steps - i) / steps
        x = a * math.cos(t) - a
        y = -b * math.sin(t)
        await drone.offboard.set_position_ned(PositionNedYaw(x, y, -4.0, 180.0))
        await asyncio.sleep(1 / hz)

    print("Hovering...")
    await asyncio.sleep(2)

    await drone.offboard.stop()
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())