import asyncio
from mavsdk import System

async def main():
    drone= System()
    await drone.connect()

    #wait for the drone to be ready 
    print("Waiting for the drone to have GPS estimates...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global Position is OK.")
            break
    
    print("Arming...")
    await drone.action.arm()

    takeoff_alt= 5.0
    await drone.action.set_takeoff_altitude(takeoff_alt)

    print(f'Taking off to {takeoff_alt} meters')
    await drone.action.takeoff()
    await asyncio.sleep(20) #give the drone time to takeoff

    #LAND
    print("Landing...")
    await drone.action.land()

asyncio.run(main())