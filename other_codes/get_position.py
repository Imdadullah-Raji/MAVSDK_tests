from mavsdk import System
import asyncio

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")  # adjust this to match your setup

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Connected to drone!")
            break

    print("Waiting for GPS fix...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("GPS fix acquired!")
            break

    async for position in drone.telemetry.position():
        print(f"Latitude: {position.latitude_deg}, Longitude: {position.longitude_deg}, Altitude: {position.relative_altitude_m}")
        break  # Remove this if you want to keep printing in a loop

if __name__ == "__main__":
    asyncio.run(run())
