import json
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
import asyncio

async def run():
    
    drone = System()
    await drone.connect()
    

    print("Waiting for drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break
    

    # print("Uploading mission...")
    # await drone.mission.upload_mission(mission_plan)

    print("Arming...")
    await drone.action.arm()

    print("Starting mission...")
    await drone.mission.start_mission()

    # async for mission_progress in drone.mission.mission_progress():
    #     print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")
    #     if mission_progress.current==0.7:
    #         await drone.mission.pause_mission()
    #         await asyncio.sleep(30)
    #         await drone.mission.start_mission()
    counter=0
    while True:
        await asyncio.sleep(1)
        counter+=1
        print("Count:", counter)
        if( counter>=200):
            await drone.mission.pause_mission()
            await drone.action.land()
            break


asyncio.run(run())

