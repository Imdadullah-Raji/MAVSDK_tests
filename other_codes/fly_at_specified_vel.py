import asyncio
from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed, OffboardError

async def main():
    drone = System()
    await drone.connect()

    # wait for position lock
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("GPS locked.")
            break
    #ARM
    await drone.action.arm()
    await drone.action.set_takeoff_altitude(60)
    await drone.action.takeoff()
    await asyncio.sleep(35)

    # START OFFBOARD mode with 0 velocity to prep PX4
    print("Starting offboard control...")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    try:
        await drone.offboard.start()
    except OffboardError as e:
        print(f"Offboard failed to start: {e}")
        await drone.action.disarm()
        return
    #move forward in body frame
    speed= 2
    distance= 120 
    duration = distance/speed
    print("Going forward in body coordinates...")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(speed, 0.0, 0.0, 0.0))
    await asyncio.sleep(duration)

    #stop movement
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(2)

    #stop offboard
    await drone.offboard.stop()

    print("Landing ... ")
    await drone.action.land()
    await asyncio.sleep(10);
    #await drone.action.disarm()

asyncio.run(main())