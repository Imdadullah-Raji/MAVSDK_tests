import asyncio
import math
from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw

def rad2deg(r):
    return r * 180.0 / math.pi

async def wait(duration):
    await asyncio.sleep(duration)

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
    await drone.action.set_takeoff_altitude(1.5)
    await drone.action.takeoff()
    await wait(7)

    print("Starting Offboard mode...")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -1.5, 0.0))
    await drone.offboard.start()

    # === 25s–45s: Setup Phase ===
    print("Setup: slow rise")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.5, 0.0))
    await wait(5)

    print("Yaw 45°")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.5, 45.0))
    await wait(3)

    print("Yaw back to 0° and hold")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.5, 0.0))
    await wait(7)

    # === 45s–70s: Dance Segment ===
    print("Snap yaw +90°")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.5, 90.0))
    await wait(1.5)

    print("Snap yaw -90°")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.5, -90.0))
    await wait(1.5)

    print("Drop to 1.5m")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -1.5, -90.0))
    await wait(2)

    print("Slow rise to 2.8m")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.8, -90.0))
    await wait(3)

    print("Start circular orbit")
    radius = 3
    hz = 20
    duration = 6
    steps = hz * duration
    for i in range(steps):
        theta = 2 * math.pi * i / steps
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        yaw = rad2deg(math.atan2(-y, -x))
        await drone.offboard.set_position_ned(PositionNedYaw(x, y, -2.8, yaw))
        await asyncio.sleep(1 / hz)

    print("Freeze hover")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.8, 0.0))
    await wait(3)

    print("Snap yaw 180°")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.8, 180.0))
    await wait(2)

    print("Rise + spin")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -3.2, 270.0))
    await wait(2)

    print("Face center and hover")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -3.2, 0.0))
    await wait(2)

    print("Gentle descent")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -1.5, 0.0))
    await wait(3)

    print("Dance complete. Landing...")
    await drone.offboard.stop()
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())