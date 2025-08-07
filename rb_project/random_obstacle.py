import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import heapq
from matplotlib.widgets import Button

# ================ Configuration ================
WORLD_SIZE = (100, 100, 50)  # (x, y, z) dimensions in meters
RESOLUTION = 1.0  # Grid resolution in meters
BUFFER_DISTANCE = 2.0  # Safety margin around obstacles
MAIN_PATH_HEIGHT = 5.0  # Fixed altitude for all paths


# ================ Obstacle Setup ================
class Obstacle:
    def __init__(self, center, size, obstacle_type):
        self.center = np.array(center)
        self.size = np.array(size)
        self.type = obstacle_type
        self.min_corner = self.center - self.size / 2
        self.max_corner = self.center + self.size / 2

    def contains_point(self, point):
        """Check if a point is inside this obstacle"""
        return (np.all(point >= self.min_corner) and
                np.all(point <= self.max_corner))

    def get_buffered_corners(self, buffer):
        """Get expanded bounds with safety buffer"""
        return (self.center - self.size / 2 - buffer,
                self.center + self.size / 2 + buffer)


def generate_obstacles(num_obstacles=10):
    """Create a random set of obstacles (buildings, no-fly zones, ground obstacles)"""
    np.random.seed()  # Use system time as seed
    obstacles = []
    types = ["building", "no_fly_zone", "ground_obstacle"]

    for _ in range(num_obstacles):
        obstacle_type = np.random.choice(types)

        # Set size ranges based on type
        if obstacle_type == "building":
            size = np.random.uniform([10, 10, 20], [30, 30, 40])
            z_base = size[2] / 2
        elif obstacle_type == "no_fly_zone":
            size = np.random.uniform([10, 10, 10], [25, 25, 25])
            z_base = size[2] / 2
        else:  # ground_obstacle
            size = np.random.uniform([5, 5, 2], [15, 15, 8])
            z_base = size[2] / 2

        # Choose a center that stays within bounds
        margin = BUFFER_DISTANCE + size / 2
        x = np.random.uniform(margin[0], WORLD_SIZE[0] - margin[0])
        y = np.random.uniform(margin[1], WORLD_SIZE[1] - margin[1])
        z = z_base

        center = [x, y, z]
        obstacles.append(Obstacle(center=center, size=size, obstacle_type=obstacle_type))

    return obstacles


# ================ Grid Operations ================
def initialize_grid(obstacles):
    """Create 3D navigation grid with obstacle markings"""
    grid_shape = (int(WORLD_SIZE[0] / RESOLUTION),
                  int(WORLD_SIZE[1] / RESOLUTION),
                  int(WORLD_SIZE[2] / RESOLUTION))
    grid = np.zeros(grid_shape, dtype=np.uint8)
    origin = np.array([0.0, 0.0, 0.0])

    for obs in obstacles:
        min_corner, max_corner = obs.get_buffered_corners(BUFFER_DISTANCE)
        min_idx = world_to_grid(min_corner, origin, RESOLUTION)
        max_idx = world_to_grid(max_corner, origin, RESOLUTION)

        # Clip to grid bounds
        min_idx = np.clip(min_idx, 0, np.array(grid.shape) - 1)
        max_idx = np.clip(max_idx, 0, np.array(grid.shape) - 1)

        # Mark 3D obstacle area
        grid[min_idx[0]:max_idx[0] + 1,
        min_idx[1]:max_idx[1] + 1,
        min_idx[2]:max_idx[2] + 1] = 1

    return grid, origin


def world_to_grid(point, origin, resolution):
    """Convert world coordinates to grid indices"""
    return tuple(((point - origin) / resolution).astype(int))


def grid_to_world(index, origin, resolution):
    """Convert grid indices to world coordinates"""
    return np.array(index) * resolution + origin + resolution / 2


# ================ Pathfinding ================
def astar_2d_fixed_z(grid, start_idx, goal_idx, origin, resolution, fixed_z):
    """2D A* at fixed altitude with 3D safety checks"""

    def heuristic(a, b):
        # Euclidean distance for accurate costing
        return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    # 8-directional movement
    neighbors = [(dx, dy) for dx in [-1, 0, 1]
                 for dy in [-1, 0, 1]
                 if (dx, dy) != (0, 0)]

    # Get Z-level index
    z_level = int((fixed_z - origin[2]) / resolution)

    open_set = []
    heapq.heappush(open_set, (0, 0, (start_idx[0], start_idx[1])))
    came_from = {}
    g_score = {(start_idx[0], start_idx[1]): 0}

    while open_set:
        _, cost, current = heapq.heappop(open_set)

        if (current[0], current[1]) == (goal_idx[0], goal_idx[1]):
            # Reconstruct path with fixed Z
            path = []
            while current in came_from:
                path.append((current[0], current[1], z_level))
                current = came_from[current]
            path.append((start_idx[0], start_idx[1], z_level))
            return path[::-1]

        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)

            # Boundary checks
            if not (0 <= neighbor[0] < grid.shape[0] and
                    0 <= neighbor[1] < grid.shape[1]):
                continue

            # Obstacle check at fixed Z and below (for overhangs)
            if grid[neighbor[0], neighbor[1], z_level] == 1:
                continue

            # Check for overhanging obstacles below current altitude
            if any(grid[neighbor[0], neighbor[1], z] == 1
                   for z in range(z_level, grid.shape[2])):
                continue

            # Movement cost
            move_cost = 1 if (dx == 0 or dy == 0) else 1.414  # Straight vs diagonal
            tentative_g = g_score[current] + move_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor, (goal_idx[0], goal_idx[1]))
                heapq.heappush(open_set, (f, tentative_g, neighbor))
                came_from[neighbor] = current

    return None  # No path found


# ================ Visualization ================
def generate_box_faces(center, size):
    """Generate faces for 3D box visualization"""
    cx, cy, cz = center
    dx, dy, dz = size
    x = [cx - dx / 2, cx + dx / 2]
    y = [cy - dy / 2, cy + dy / 2]
    z = [cz - dz / 2, cz + dz / 2]

    vertices = [
        [x[0], y[0], z[0]], [x[1], y[0], z[0]],
        [x[1], y[1], z[0]], [x[0], y[1], z[0]],
        [x[0], y[0], z[1]], [x[1], y[0], z[1]],
        [x[1], y[1], z[1]], [x[0], y[1], z[1]]
    ]

    faces = [
        [vertices[i] for i in [0, 1, 2, 3]],  # bottom
        [vertices[i] for i in [4, 5, 6, 7]],  # top
        [vertices[i] for i in [0, 1, 5, 4]],  # front
        [vertices[i] for i in [2, 3, 7, 6]],  # back
        [vertices[i] for i in [1, 2, 6, 5]],  # right
        [vertices[i] for i in [4, 7, 3, 0]],  # left
    ]
    return faces


def plot_scenario(ax, obstacles, path=None):
    """Create 3D visualization"""
    ax.clear()

    # Plot obstacles
    colors = {'building': 'red', 'no_fly_zone': 'blue', 'ground_obstacle': 'brown'}
    alphas = {'building': 0.7, 'no_fly_zone': 0.3, 'ground_obstacle': 0.5}

    for obs in obstacles:
        faces = generate_box_faces(obs.center, obs.size)
        ax.add_collection3d(Poly3DCollection(faces,
                                             color=colors[obs.type],
                                             alpha=alphas[obs.type],
                                             label=obs.type.replace('_', ' ').title()))

    # Start and end points
    start = np.array([10, 10, MAIN_PATH_HEIGHT])
    end = np.array([90, 90, MAIN_PATH_HEIGHT])
    ax.scatter(*start, color='green', s=100, label='Start')
    ax.scatter(*end, color='red', s=100, label='End')

    # Plot ideal path
    ideal_path = np.linspace(start, end, 100)
    ax.plot(ideal_path[:, 0], ideal_path[:, 1], ideal_path[:, 2],
            'k--', linewidth=1, label='Ideal Path')

    # Plot computed path
    if path:
        path_array = np.array(path)
        ax.plot(path_array[:, 0], path_array[:, 1], path_array[:, 2],
                'g-', linewidth=2, label='Safe Path')

    # Configure plot
    ax.set_xlim(0, WORLD_SIZE[0])
    ax.set_ylim(0, WORLD_SIZE[1])
    ax.set_zlim(0, WORLD_SIZE[2])
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title(f'Path Planning at Fixed Altitude: {MAIN_PATH_HEIGHT}m')
    ax.legend()
    ax.view_init(elev=30, azim=45)


# ================ Main Execution ================
def run_planner():
    # Generate obstacles
    obstacles = generate_obstacles()

    # Initialize grid
    grid, origin = initialize_grid(obstacles)

    # Set start and goal at fixed altitude
    start = np.array([10.0, 10.0, MAIN_PATH_HEIGHT])
    end = np.array([90.0, 90.0, MAIN_PATH_HEIGHT])
    start_idx = world_to_grid(start, origin, RESOLUTION)
    end_idx = world_to_grid(end, origin, RESOLUTION)

    # Find 2D path at fixed Z
    path_idx = astar_2d_fixed_z(grid, start_idx, end_idx, origin, RESOLUTION, MAIN_PATH_HEIGHT)

    if path_idx:
        path = [grid_to_world(idx, origin, RESOLUTION) for idx in path_idx]
        print(f"Safe path found with {len(path)} waypoints")
        np.savetxt("safe_path.csv", path, delimiter=",", header="x,y,z", fmt="%.2f")
    else:
        path = None
        print("No safe path found at this altitude!")

    # Visualization
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    plot_scenario(ax, obstacles, path)

    # Add regenerate button
    ax_button = plt.axes([0.7, 0.05, 0.2, 0.05])
    button = Button(ax_button, 'New Scenario')
    button.on_clicked(lambda event: run_planner())

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_planner()