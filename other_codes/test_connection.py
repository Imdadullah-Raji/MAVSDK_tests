import asyncio
from mavsdk import System

async def main():
    drone = System()
    await drone.connect()

    #this will be true/false based on connection
    async for states in drone.core.connection_state():
        print("Connected", states.is_connected)
        break
asyncio.run(main())