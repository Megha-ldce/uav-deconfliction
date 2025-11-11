"""
Generate test data for drone missions
"""
import numpy as np
from typing import List
from drone import Mission, Waypoint


class DataGenerator:
    """Generate test scenarios for drone missions"""
    
    @staticmethod
    def generate_straight_line_mission(
        start: tuple,
        end: tuple,
        start_time: float,
        end_time: float,
        drone_id: str,
        num_waypoints: int = 5
    ) -> Mission:
        """Generate a straight line mission"""
        waypoints = []
        
        for i in range(num_waypoints):
            t = i / (num_waypoints - 1)
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t
            z = start[2] + (end[2] - start[2]) * t if len(start) > 2 else 0
            waypoints.append(Waypoint(x, y, z))
        
        return Mission(waypoints, start_time, end_time, drone_id)
    
    @staticmethod
    def generate_circular_mission(
        center: tuple,
        radius: float,
        start_time: float,
        end_time: float,
        drone_id: str,
        num_waypoints: int = 12
    ) -> Mission:
        """Generate a circular patrol mission"""
        waypoints = []
        
        for i in range(num_waypoints):
            angle = 2 * np.pi * i / num_waypoints
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            z = center[2] if len(center) > 2 else 0
            waypoints.append(Waypoint(x, y, z))
        
        # Close the circle
        waypoints.append(waypoints[0])
        
        return Mission(waypoints, start_time, end_time, drone_id)
    
    @staticmethod
    def generate_grid_pattern_mission(
        start: tuple,
        width: float,
        height: float,
        rows: int,
        start_time: float,
        end_time: float,
        drone_id: str
    ) -> Mission:
        """Generate a grid/lawn mower pattern mission"""
        waypoints = []
        z = start[2] if len(start) > 2 else 0
        
        for row in range(rows):
            y = start[1] + row * (height / (rows - 1)) if rows > 1 else start[1]
            
            if row % 2 == 0:  # Left to right
                x_start, x_end = start[0], start[0] + width
            else:  # Right to left
                x_start, x_end = start[0] + width, start[0]
            
            waypoints.append(Waypoint(x_start, y, z))
            waypoints.append(Waypoint(x_end, y, z))
        
        return Mission(waypoints, start_time, end_time, drone_id)
    
    @staticmethod
    def generate_random_mission(
        bounds: tuple,
        num_waypoints: int,
        start_time: float,
        end_time: float,
        drone_id: str,
        seed: int = None
    ) -> Mission:
        """Generate a random mission within bounds"""
        if seed is not None:
            np.random.seed(seed)
        
        x_min, x_max, y_min, y_max = bounds[:4]
        z_min = bounds[4] if len(bounds) > 4 else 0
        z_max = bounds[5] if len(bounds) > 5 else 0
        
        waypoints = []
        for _ in range(num_waypoints):
            x = np.random.uniform(x_min, x_max)
            y = np.random.uniform(y_min, y_max)
            z = np.random.uniform(z_min, z_max) if z_max > z_min else 0
            waypoints.append(Waypoint(x, y, z))
        
        return Mission(waypoints, start_time, end_time, drone_id)


class ScenarioGenerator:
    """Generate complete test scenarios"""
    
    @staticmethod
    def scenario_no_conflict():
        """Scenario with no conflicts"""
        primary = DataGenerator.generate_straight_line_mission(
            start=(0, 0, 50),
            end=(100, 0, 50),
            start_time=0,
            end_time=20,
            drone_id="primary"
        )
        
        other1 = DataGenerator.generate_straight_line_mission(
            start=(0, 100, 50),
            end=(100, 100, 50),
            start_time=0,
            end_time=20,
            drone_id="drone_1"
        )
        
        other2 = DataGenerator.generate_circular_mission(
            center=(200, 200, 75),
            radius=50,
            start_time=5,
            end_time=25,
            drone_id="drone_2"
        )
        
        return primary, [other1, other2]
    
    @staticmethod
    def scenario_spatial_conflict():
        """Scenario with spatial conflict (paths cross)"""
        primary = DataGenerator.generate_straight_line_mission(
            start=(0, 0, 50),
            end=(100, 100, 50),
            start_time=0,
            end_time=20,
            drone_id="primary"
        )
        
        # This drone crosses the primary's path
        other1 = DataGenerator.generate_straight_line_mission(
            start=(0, 100, 50),
            end=(100, 0, 50),
            start_time=0,
            end_time=20,
            drone_id="drone_1"
        )
        
        other2 = DataGenerator.generate_circular_mission(
            center=(200, 200, 75),
            radius=30,
            start_time=5,
            end_time=25,
            drone_id="drone_2"
        )
        
        return primary, [other1, other2]
    
    @staticmethod
    def scenario_temporal_conflict():
        """Scenario with temporal conflict (same path, different times)"""
        primary = DataGenerator.generate_straight_line_mission(
            start=(0, 0, 50),
            end=(100, 0, 50),
            start_time=0,
            end_time=15,
            drone_id="primary"
        )
        
        # This drone uses same path but later
        other1 = DataGenerator.generate_straight_line_mission(
            start=(0, 0, 50),
            end=(100, 0, 50),
            start_time=20,
            end_time=35,
            drone_id="drone_1"
        )
        
        # This drone has overlapping time and path
        other2 = DataGenerator.generate_straight_line_mission(
            start=(10, -10, 50),
            end=(90, 10, 50),
            start_time=5,
            end_time=25,
            drone_id="drone_2"
        )
        
        return primary, [other1, other2]
    
    @staticmethod
    def scenario_3d_conflict():
        """Scenario with 3D altitude conflict"""
        primary = DataGenerator.generate_straight_line_mission(
            start=(0, 0, 50),
            end=(100, 0, 50),
            start_time=0,
            end_time=20,
            drone_id="primary"
        )
        
        # This drone flies at same location but different altitude (should be safe)
        other1 = DataGenerator.generate_straight_line_mission(
            start=(0, 0, 150),
            end=(100, 0, 150),
            start_time=0,
            end_time=20,
            drone_id="drone_1"
        )
        
        # This drone has altitude too close
        other2 = DataGenerator.generate_straight_line_mission(
            start=(0, 0, 60),
            end=(100, 0, 60),
            start_time=0,
            end_time=20,
            drone_id="drone_2"
        )
        
        return primary, [other1, other2]
    
    @staticmethod
    def scenario_complex_multi_drone():
        """Complex scenario with multiple drones and patterns"""
        primary = DataGenerator.generate_grid_pattern_mission(
            start=(0, 0, 50),
            width=100,
            height=100,
            rows=5,
            start_time=0,
            end_time=60,
            drone_id="primary"
        )
        
        other1 = DataGenerator.generate_circular_mission(
            center=(50, 50, 50),
            radius=40,
            start_time=10,
            end_time=40,
            drone_id="drone_1"
        )
        
        other2 = DataGenerator.generate_straight_line_mission(
            start=(0, 50, 50),
            end=(100, 50, 50),
            start_time=20,
            end_time=40,
            drone_id="drone_2"
        )
        
        other3 = DataGenerator.generate_random_mission(
            bounds=(0, 100, 0, 100, 40, 60),
            num_waypoints=8,
            start_time=5,
            end_time=55,
            drone_id="drone_3",
            seed=42
        )
        
        return primary, [other1, other2, other3]