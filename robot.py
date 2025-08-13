# mission_tracker.py
import asyncio
from math import radians, sin, cos, sqrt, atan2
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan

# Great-circle distance in meters (haversine)
def distance_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(p1) * cos(p2) * sin(dlambda/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))

async def main():
    drone = System()
    # Connect to PX4 SITL or a real autopilot that forwards to UDP/14540
    await drone.connect(system_address="udp://:14540")

    print("Waiting for the drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected!")
            break

    # Wait until the estimator has a good global position & home set
    print("Waiting for a good GPS lock and home position...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("GPS & home OK")
            break

    # Define your mission waypoints (lat, lon, rel_alt_m, speed_m_s, fly_through, gimbal_pitch, gimbal_yaw, camera_action, loiter_s, photo_interval_s)
    items = [
        MissionItem(47.3981703271, 8.54564902186, 20, 5, True, 0, 0,
                    MissionItem.CameraAction.NONE, 0, 0),
        MissionItem(47.3982413381, 8.54475557926, 20, 5, True, 0, 0,
                    MissionItem.CameraAction.NONE, 0, 0),
        MissionItem(47.3981393638, 8.54538461551, 20, 5, True, 0, 0,
                    MissionItem.CameraAction.NONE, 0, 0),
    ]
    plan = MissionPlan(items)

    print("Uploading mission...")
    await drone.mission.upload_mission(plan)

    print("Arming...")
    await drone.action.arm()

    print("Starting mission...")
    await drone.mission.start_mission()

    # Track progress + distance to current waypoint
    current_wp_idx = 0
    total_wps = len(items)

    async def watch_progress():
        nonlocal current_wp_idx
        async for progress in drone.mission.mission_progress():
            current_wp_idx = progress.current
            print(f"Mission progress: {progress.current}/{progress.total}")

    async def watch_position():
        # print live distance to the active waypoint
        while True:
            pos = await drone.telemetry.position().__anext__()
            if current_wp_idx < total_wps:
                wp = items[current_wp_idx]
                d = distance_m(pos.latitude_deg, pos.longitude_deg, wp.latitude_deg, wp.longitude_deg)
                print(f"Dist to WP{current_wp_idx}: {d:.1f} m")
            await asyncio.sleep(0.5)

    progress_task = asyncio.create_task(watch_progress())
    position_task = asyncio.create_task(watch_position())

    # Wait until mission finishes (very simple wait loop)
    while True:
        is_finished = await drone.mission.is_mission_finished()
        if is_finished:
            print("Mission finished. RTL...")
            await drone.action.return_to_launch()
            break
        await asyncio.sleep(1)

    # Cleanup
    progress_task.cancel()
    position_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())