import asyncio
import math
from mavsdk import System
from mavsdk.offboard import OffboardError, VelocityNedYaw

def rad2deg(r):
    return r * 180.0 / math.pi

async def wait(seconds):
    await asyncio.sleep(seconds)

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            break

    print("Arming...")
    await drone.action.arm()
    await drone.action.set_takeoff_altitude(2)
    await drone.action.takeoff()
    await wait(20)

    print("Starting Offboard mode...")
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    await drone.offboard.start()

    print("Slow steady rise (0:20–0:35)")
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, -0.2, 0.0))
    await wait(15)

    print("Sudden snap yaw + altitude burst (0:35–0:50)")
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, -1.0, 90.0))
    await wait(2)
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, -1.5, 180.0))
    await wait(3)
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 180.0))
    await wait(2)

    print("Final slow spiral descent (1:10–end)")
    radius = 2.5
    base_alt = -4.0
    final_alt = -2.0
    duration = 10
    hz = 20
    steps = hz * duration
    for i in range(steps):
        t = 2 * math.pi * i / steps
        frac = i / steps
        vx = -radius * math.sin(t) * 0.4
        vy =  radius * math.cos(t) * 0.4
        vz = (final_alt - base_alt) / duration  # smooth rise
        yaw = rad2deg(math.atan2(-vy, -vx))
        await drone.offboard.set_velocity_ned(VelocityNedYaw(vx, vy, vz, yaw))
        await asyncio.sleep(1 / hz)

    print("Hover and land slowly")
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.2, 0.0))
    await wait(4)
    await drone.offboard.stop()
    await drone.action.land()


if __name__ == "__main__":
    asyncio.run(run())