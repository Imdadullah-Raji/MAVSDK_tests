import asyncio
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
    await asyncio.sleep(2)

    # Snap Turn 90°
    print("Snap 90°")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -3.0, 90.0))
    await asyncio.sleep(2)

    # Snap Turn 180°
    print("Snap 180°")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -3.0, 180.0))
    await asyncio.sleep(2)

    # Snap Turn 270°
    print("Snap 270°")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -3.0, 270.0))
    await asyncio.sleep(2)

    # Snap Back to 0°
    print("Snap back to 0°")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -3.0, 0.0))
    await asyncio.sleep(2)

    print("Landing...")
    await drone.offboard.stop()
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())