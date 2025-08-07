import asyncio
import csv
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan

CSV_PATH = "/home/raji/MAVSDK_tests/rb_project/waypoints.csv"
CRUISE_SPEED = 2.0  # m/s
FLIGHT_ALT = 30.0   # Used if alt not in CSV

def load_waypoints_from_csv(path):
    mission_items = []
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            lat = float(row[0])
            lon = float(row[1])
            alt = float(row[2]) if len(row) > 2 else FLIGHT_ALT

            print("lat: ", lat)

            mission_items.append(
                MissionItem(
                    latitude_deg=lat,
                    longitude_deg=lon,
                    relative_altitude_m=alt,
                    speed_m_s=CRUISE_SPEED,
                    is_fly_through=True,
                    gimbal_pitch_deg=0.0,
                    gimbal_yaw_deg=0.0,
                    loiter_time_s=0.0,
                    camera_action=MissionItem.CameraAction.NONE,
                    acceptance_radius_m=1.0,
                    yaw_deg=float('nan'),
                    camera_photo_interval_s=0.0,
                    camera_photo_distance_m=0.0,
                    vehicle_action=MissionItem.VehicleAction.NONE,
                )
            )
    return mission_items

async def run():
    drone = System()
    await drone.connect()  # change if needed

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break

    print("Waiting for global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position ok")
            break

    print(f"Setting cruise speed to {CRUISE_SPEED} m/s...")
    await drone.action.set_current_speed(CRUISE_SPEED)

    print("Loading waypoints from CSV...")
    mission_items = load_waypoints_from_csv(CSV_PATH)
    mission_plan = MissionPlan(mission_items)

    print("Uploading mission...")
    await drone.mission.set_return_to_launch_after_mission(False)
    await drone.mission.upload_mission(mission_plan)

    print("Arming drone...")
    await drone.action.arm()

    print("Starting mission...")
    await drone.mission.start_mission()

    # Wait until mission is finished
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")
        if mission_progress.current == mission_progress.total:
            print("Mission complete.")
            break

    print("Landing...")
    await drone.action.land()

    # Wait for landing
    async for in_air in drone.telemetry.in_air():
        if not in_air:
            print("Landed.")
            break

if __name__ == "__main__":
    asyncio.run(run())
