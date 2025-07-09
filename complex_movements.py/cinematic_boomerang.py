import asyncio
import math
from mavsdk import System
from mavsdk.offboard import PositionNedYaw

def rad2deg(r):
    return r * 180.0 / math.pi

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected!")
            break

    await drone.action.arm()
    await drone.action.set_takeoff_altitude(1.5)
    await drone.action.takeoff()
    await asyncio.sleep(10)

    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -1.5, 0.0))
    await drone.offboard.start()

    a, b = 8, 4    # ellipse dimensions
    z_min = -10   # max descent
    z_start = -1.5
    hz = 20
    duration = 6   # seconds for each direction
    steps = hz * duration

    # === Outward Arc with Rise ===
    for i in range(steps):
        t = math.pi * i / steps  # 0 → π
        x = a * math.cos(t) - a
        y = b * math.sin(t)
        z = z_start + (z_min - z_start) * (i / steps)
        yaw = rad2deg(math.atan2(-y, -x))  # face origin
        await drone.offboard.set_position_ned(PositionNedYaw(x, y, z, yaw))
        await asyncio.sleep(1 / hz)

    await asyncio.sleep(0.5)

    # === Return Arc with Climb ===
    for i in range(steps):
        t = math.pi * (steps - i) / steps
        x = a * math.cos(t) - a
        y = -b * math.sin(t)
        z = z_min + (z_start - z_min) * (i / steps)
        yaw = rad2deg(math.atan2(-y, -x))  # still face origin
        await drone.offboard.set_position_ned(PositionNedYaw(x, y, z, yaw))
        await asyncio.sleep(1 / hz)

    await asyncio.sleep(2)
    await drone.offboard.stop()
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())