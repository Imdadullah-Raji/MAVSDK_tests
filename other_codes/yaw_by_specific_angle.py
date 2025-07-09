import math
from mavsdk import System
from mavsdk.offboard import Attitude, VelocityBodyYawspeed, OffboardError
import asyncio

async def initialize_drone(drone:System):
    await drone.connect()
    # wait for position lock
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("GPS locked.")
            break
    await drone.action.arm()
    await drone.action.set_takeoff_altitude(6)
    await drone.action.takeoff()
    await asyncio.sleep(15)
    # START OFFBOARD mode with 0 velocity to prep PX4
    print("Starting offboard control...")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    try:
        await drone.offboard.start()
    except OffboardError as e:
        print(f"Offboard failed to start: {e}")
        await drone.action.disarm()
        return

async def yaw_by_angle(drone:System, delta_deg):
    # Get current yaw from attitude_euler
    async for euler in drone.telemetry.attitude_euler():
        current_yaw = euler.yaw_deg
        break

    target_yaw = (current_yaw + delta_deg) % 360
    await yaw_to_heading(drone, target_yaw)

async def yaw_to_heading(drone:System, target_yaw_deg):
    # Normalize yaw angle
    if target_yaw_deg > 180:
        target_yaw_deg -= 360

    await drone.offboard.set_attitude(
        Attitude(
            roll_deg=0.0,
            pitch_deg=0.0,
            yaw_deg=target_yaw_deg,
            thrust_value=0.65
        )
    )
    await drone.offboard.start()
    await asyncio.sleep(2)  # let it rotate
    await drone.offboard.stop()

async def main():
    drone = System()

    print("Connecting, arming and taking off")
    await initialize_drone(drone)

    print("Yawing 180 degrees")
    await yaw_by_angle(drone, 180)

    await drone.offboard.stop()

asyncio.run(main())
