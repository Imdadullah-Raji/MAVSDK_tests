import asyncio
from mavsdk import System

async def main():
    drone = System()
    await drone.connect()

    info = await drone.info.get_version()
    print("Flight firmware version:",info.flight_sw_major, info.flight_sw_minor,info.flight_sw_patch)

    uuid= await drone.info.get_identification()
    print("UUID:", uuid)

asyncio.run(main())