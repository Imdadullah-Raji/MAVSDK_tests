
import asyncio
from mavsdk import System


async def run():
    drone = System()
    await drone.connect(system_address="udp://127.0.0.1:14580")

    print("Waiting for drone to connect...")
    await drone.action.arm()
    await drone.action.takeoff()
    await drone.action.set_current_speed(1)
    
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    info = await drone.info.get_version()
    print(info)


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())