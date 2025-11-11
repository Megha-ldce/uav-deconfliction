"""
Drone data structures and mission representation
"""
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass
class Waypoint:
    """Represents a single waypoint in 3D space"""
    x: float
    y: float
    z: float = 0.0  # altitude, default 0 for 2D
    
    def to_array(self) -> np.ndarray:
        """Convert waypoint to numpy array"""
        return np.array([self.x, self.y, self.z])
    
    def distance_to(self, other: 'Waypoint') -> float:
        """Calculate Euclidean distance to another waypoint"""
        return np.linalg.norm(self.to_array() - other.to_array())
    
    def __repr__(self):
        return f"Waypoint(x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f})"


@dataclass
class Mission:
    """Represents a drone mission with waypoints and time window"""
    waypoints: List[Waypoint]
    start_time: float  # seconds
    end_time: float    # seconds
    drone_id: str = "primary"
    speed: float = 10.0  # m/s, default speed
    
    def __post_init__(self):
        if len(self.waypoints) < 2:
            raise ValueError("Mission must have at least 2 waypoints")
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
    
    def total_distance(self) -> float:
        """Calculate total mission distance"""
        distance = 0.0
        for i in range(len(self.waypoints) - 1):
            distance += self.waypoints[i].distance_to(self.waypoints[i + 1])
        return distance
    
    def duration(self) -> float:
        """Get mission duration"""
        return self.end_time - self.start_time
    
    def get_position_at_time(self, t: float) -> Tuple[Waypoint, int]:
        """
        Get drone position at a specific time
        Returns: (position, segment_index)
        """
        if t < self.start_time or t > self.end_time:
            return None, -1
        
        # Calculate elapsed time
        elapsed = t - self.start_time
        total_distance = self.total_distance()
        total_duration = self.duration()
        
        # Assume constant speed throughout mission
        distance_traveled = (elapsed / total_duration) * total_distance
        
        # Find which segment the drone is on
        current_distance = 0.0
        for i in range(len(self.waypoints) - 1):
            segment_distance = self.waypoints[i].distance_to(self.waypoints[i + 1])
            
            if current_distance + segment_distance >= distance_traveled:
                # Drone is on this segment
                segment_progress = (distance_traveled - current_distance) / segment_distance
                
                # Interpolate position
                wp1 = self.waypoints[i]
                wp2 = self.waypoints[i + 1]
                
                x = wp1.x + (wp2.x - wp1.x) * segment_progress
                y = wp1.y + (wp2.y - wp1.y) * segment_progress
                z = wp1.z + (wp2.z - wp1.z) * segment_progress
                
                return Waypoint(x, y, z), i
            
            current_distance += segment_distance
        
        # If we're at the end
        return self.waypoints[-1], len(self.waypoints) - 2
    
    def get_trajectory_samples(self, num_samples: int = 100) -> List[Tuple[float, Waypoint]]:
        """
        Sample the trajectory at regular time intervals
        Returns: List of (time, position) tuples
        """
        samples = []
        time_step = self.duration() / num_samples
        
        for i in range(num_samples + 1):
            t = self.start_time + i * time_step
            pos, _ = self.get_position_at_time(t)
            if pos:
                samples.append((t, pos))
        
        return samples