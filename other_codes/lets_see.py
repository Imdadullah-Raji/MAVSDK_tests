from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed
import asyncio

async def main():
    drone = System()
    await drone.connect()

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate OK")
            break

    await drone.action.set_takeoff_altitude(80)
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(40)

    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(forward_m_s=0.5, right_m_s=0, down_m_s=0, yawspeed_deg_s=0)
    )

    await drone.offboard.start()
    print("Offboard mode started. Moving forward...")

    for _ in range(200):  # 10 Hz for 150 seconds
        await drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(forward_m_s=5, right_m_s=0, down_m_s=0, yawspeed_deg_s=0)
        )
        await asyncio.sleep(0.1)

    print("Stopping movement")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0, 0, 0, 0)
    )

    await drone.offboard.stop()
    await drone.action.land()

asyncio.run(main())
