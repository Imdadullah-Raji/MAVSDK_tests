import asyncio
from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw

async def zigzag_up(drone, num_zigs=4, horizontal_step=6.0, vertical_step=2.5, pause_sec=2.0):
    print("Arming...")
    await drone.action.arm()
    await drone.action.set_takeoff_altitude(2.0)
    await drone.action.takeoff()
    await asyncio.sleep(15)

    print("Setting initial setpoint for offboard...")
    initial_position = PositionNedYaw(0.0, 0.0, -2.0, 0.0)
    await drone.offboard.set_position_ned(initial_position)

    try:
        await drone.offboard.start()
        print("Offboard started.")
    except OffboardError as e:
        print(f"Offboard start failed: {e._result.result}")
        print("Disarming...")
        await drone.action.disarm()
        return

    current_x = 0.0
    current_y = 0.0
    current_z = -2.0  # negative for upward in NED
    direction = 1

    print("Starting zigzag climb...")
    for i in range(num_zigs):
        current_x += direction * horizontal_step
        current_z -= vertical_step  # up in NED = more negative

        target = PositionNedYaw(current_x, current_y, current_z, 0.0)
        print(f"Moving to: x={target.north_m}, y={target.east_m}, z={target.down_m}")
        await drone.offboard.set_position_ned(target)
        await asyncio.sleep(5)

        direction *= -1  # alternate direction

    print("Landing...")
    await drone.action.land()
    await asyncio.sleep(30)

    try:
        await drone.offboard.stop()
    except OffboardError as e:
        print(f"Offboard stop failed: {e._result.result}")

async def main():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break

    await zigzag_up(drone)

if __name__ == "__main__":
    asyncio.run(main())