import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem

# Target: South-East corner of BUET central Field
TARGET_LAT = 23.725091 
TARGET_LON = 90.395163
TARGET_ALT = 10.0  
TAKEOFF_ALT = 5.0
CRUISE_SPEED = 2.0  

async def run():
    drone = System()
    await drone.connect(system_address='serial:///dev/ttyAMA0')  

    print("Waiting for drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break

    print("Waiting for global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate ok")
            break

    # Set the cruise speed (max horizontal speed)
    print(f"Setting max speed to {CRUISE_SPEED} m/s...")
    #await drone.action.set_maximum_speed(CRUISE_SPEED)
    await drone.action.set_current_speed(CRUISE_SPEED)

    # Arm and takeoff
    print("Arming...")
    await drone.action.arm()
    await drone.action.set_takeoff_altitude(TAKEOFF_ALT)
    print(f"Taking off to {TAKEOFF_ALT} meters...")
    await drone.action.takeoff()
    await asyncio.sleep(20)  # wait for takeoff

    # Fly to GPS location
    print(f"Going to: {TARGET_LAT}, {TARGET_LON}, {TARGET_ALT}m")
    await drone.action.goto_location(TARGET_LAT, TARGET_LON, TARGET_ALT, 0)

    # Wait a bit before landing
    await asyncio.sleep(40)  # adjust depending on distance

    print("Landing...")
    await drone.action.land()
    await asyncio.sleep(30)
    await drone.action.disarm()
    print("Disarmed.")

    # Wait until landed
    # async for in_air in drone.telemetry.in_air():
    #     if not in_air:
    #         print("Landed.")
    #         break

if __name__ == "__main__":
    asyncio.run(run())
