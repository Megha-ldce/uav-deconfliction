"""
Deconfliction engine for detecting spatial and temporal conflicts
"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from drone import Mission, Waypoint


@dataclass
class Conflict:
    """Represents a detected conflict between drones"""
    primary_drone: str
    conflicting_drone: str
    time: float
    location: Waypoint
    distance: float
    severity: str  # "critical", "warning"
    
    def __repr__(self):
        return (f"Conflict at t={self.time:.2f}s: {self.primary_drone} vs {self.conflicting_drone} "
                f"at {self.location} (distance={self.distance:.2f}m, severity={self.severity})")


class DeconflictionService:
    """
    Central deconfliction service for UAV conflict detection
    """
    
    def __init__(self, safety_buffer: float = 50.0, time_resolution: float = 0.1):
        """
        Initialize deconfliction service
        
        Args:
            safety_buffer: Minimum safe distance between drones (meters)
            time_resolution: Time step for sampling trajectories (seconds)
        """
        self.safety_buffer = safety_buffer
        self.time_resolution = time_resolution
        self.registered_missions: Dict[str, Mission] = {}
    
    def register_mission(self, mission: Mission):
        """Register a mission in the system"""
        self.registered_missions[mission.drone_id] = mission
    
    def clear_missions(self):
        """Clear all registered missions"""
        self.registered_missions.clear()
    
    def check_mission(self, primary_mission: Mission) -> Tuple[bool, List[Conflict]]:
        """
        Check if a primary mission conflicts with registered missions
        
        Args:
            primary_mission: The mission to check
            
        Returns:
            (is_safe, conflicts): Boolean indicating safety and list of conflicts
        """
        conflicts = []
        
        # Check against each registered mission
        for drone_id, registered_mission in self.registered_missions.items():
            if drone_id == primary_mission.drone_id:
                continue  # Don't check against itself
            
            mission_conflicts = self._check_mission_pair(primary_mission, registered_mission)
            conflicts.extend(mission_conflicts)
        
        is_safe = len(conflicts) == 0
        return is_safe, conflicts
    
    def _check_mission_pair(self, mission1: Mission, mission2: Mission) -> List[Conflict]:
        """
        Check for conflicts between two missions
        """
        conflicts = []
        
        # Find overlapping time window
        overlap_start = max(mission1.start_time, mission2.start_time)
        overlap_end = min(mission1.end_time, mission2.end_time)
        
        if overlap_start >= overlap_end:
            return conflicts  # No temporal overlap
        
        # Sample both trajectories during overlap period
        num_samples = int((overlap_end - overlap_start) / self.time_resolution)
        num_samples = max(num_samples, 10)  # At least 10 samples
        
        for i in range(num_samples + 1):
            t = overlap_start + i * (overlap_end - overlap_start) / num_samples
            
            pos1, seg1 = mission1.get_position_at_time(t)
            pos2, seg2 = mission2.get_position_at_time(t)
            
            if pos1 and pos2:
                distance = pos1.distance_to(pos2)
                
                if distance < self.safety_buffer:
                    # Determine severity
                    severity = "critical" if distance < self.safety_buffer * 0.5 else "warning"
                    
                    conflict = Conflict(
                        primary_drone=mission1.drone_id,
                        conflicting_drone=mission2.drone_id,
                        time=t,
                        location=pos1,
                        distance=distance,
                        severity=severity
                    )
                    conflicts.append(conflict)
        
        # Remove duplicate conflicts (merge close time points)
        conflicts = self._merge_close_conflicts(conflicts)
        
        return conflicts
    
    def _merge_close_conflicts(self, conflicts: List[Conflict], time_threshold: float = 1.0) -> List[Conflict]:
        """
        Merge conflicts that are close in time (within time_threshold seconds)
        Returns only the most severe conflict in each time window
        """
        if not conflicts:
            return conflicts
        
        # Sort by time
        conflicts.sort(key=lambda c: c.time)
        
        merged = []
        current_group = [conflicts[0]]
        
        for conflict in conflicts[1:]:
            if conflict.time - current_group[0].time <= time_threshold:
                current_group.append(conflict)
            else:
                # Pick the most severe conflict from the group
                most_severe = min(current_group, key=lambda c: c.distance)
                merged.append(most_severe)
                current_group = [conflict]
        
        # Add last group
        if current_group:
            most_severe = min(current_group, key=lambda c: c.distance)
            merged.append(most_severe)
        
        return merged
    
    def get_detailed_report(self, primary_mission: Mission) -> str:
        """
        Generate a detailed report of the conflict check
        """
        is_safe, conflicts = self.check_mission(primary_mission)
        
        report = f"\n{'='*70}\n"
        report += f"DECONFLICTION REPORT for {primary_mission.drone_id}\n"
        report += f"{'='*70}\n\n"
        
        report += f"Mission Details:\n"
        report += f"  - Waypoints: {len(primary_mission.waypoints)}\n"
        report += f"  - Time Window: {primary_mission.start_time:.1f}s - {primary_mission.end_time:.1f}s\n"
        report += f"  - Duration: {primary_mission.duration():.1f}s\n"
        report += f"  - Total Distance: {primary_mission.total_distance():.1f}m\n\n"
        
        report += f"Safety Buffer: {self.safety_buffer}m\n"
        report += f"Registered Missions: {len(self.registered_missions)}\n\n"
        
        if is_safe:
            report += "✓ STATUS: CLEAR - No conflicts detected\n"
            report += "Mission is safe to execute.\n"
        else:
            report += f"✗ STATUS: CONFLICT DETECTED - {len(conflicts)} conflict(s) found\n\n"
            report += "Conflict Details:\n"
            report += "-" * 70 + "\n"
            
            for i, conflict in enumerate(conflicts, 1):
                report += f"\nConflict #{i}:\n"
                report += f"  Time: {conflict.time:.2f}s\n"
                report += f"  Location: ({conflict.location.x:.2f}, {conflict.location.y:.2f}, {conflict.location.z:.2f})\n"
                report += f"  Conflicting Drone: {conflict.conflicting_drone}\n"
                report += f"  Distance: {conflict.distance:.2f}m\n"
                report += f"  Severity: {conflict.severity.upper()}\n"
                report += f"  Safety Margin: {conflict.distance - self.safety_buffer:.2f}m (VIOLATED)\n"
        
        report += "\n" + "="*70 + "\n"
        
        return report