"""
Test suite for UAV deconfliction system
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from drone import Mission, Waypoint
from deconfliction import DeconflictionService, Conflict
from data_generator import DataGenerator, ScenarioGenerator


class TestWaypoint:
    """Test Waypoint class"""
    
    def test_waypoint_creation(self):
        wp = Waypoint(10, 20, 30)
        assert wp.x == 10
        assert wp.y == 20
        assert wp.z == 30
    
    def test_waypoint_distance(self):
        wp1 = Waypoint(0, 0, 0)
        wp2 = Waypoint(3, 4, 0)
        assert wp1.distance_to(wp2) == 5.0
    
    def test_waypoint_3d_distance(self):
        wp1 = Waypoint(0, 0, 0)
        wp2 = Waypoint(1, 1, 1)
        distance = wp1.distance_to(wp2)
        assert abs(distance - 1.732) < 0.01


class TestMission:
    """Test Mission class"""
    
    def test_mission_creation(self):
        waypoints = [Waypoint(0, 0, 0), Waypoint(100, 0, 0)]
        mission = Mission(waypoints, 0, 20, "test_drone")
        assert len(mission.waypoints) == 2
        assert mission.drone_id == "test_drone"
    
    def test_mission_invalid_waypoints(self):
        with pytest.raises(ValueError):
            Mission([Waypoint(0, 0, 0)], 0, 20, "test")
    
    def test_mission_invalid_time(self):
        waypoints = [Waypoint(0, 0, 0), Waypoint(100, 0, 0)]
        with pytest.raises(ValueError):
            Mission(waypoints, 20, 10, "test")
    
    def test_mission_total_distance(self):
        waypoints = [Waypoint(0, 0, 0), Waypoint(3, 4, 0)]
        mission = Mission(waypoints, 0, 20, "test")
        assert mission.total_distance() == 5.0
    
    def test_mission_duration(self):
        waypoints = [Waypoint(0, 0, 0), Waypoint(100, 0, 0)]
        mission = Mission(waypoints, 5, 25, "test")
        assert mission.duration() == 20
    
    def test_position_at_time(self):
        waypoints = [Waypoint(0, 0, 0), Waypoint(100, 0, 0)]
        mission = Mission(waypoints, 0, 20, "test")
        
        # At start
        pos, seg = mission.get_position_at_time(0)
        assert pos.x == 0
        
        # At midpoint
        pos, seg = mission.get_position_at_time(10)
        assert abs(pos.x - 50) < 1
        
        # At end
        pos, seg = mission.get_position_at_time(20)
        assert abs(pos.x - 100) < 1
        
        # Outside time window
        pos, seg = mission.get_position_at_time(30)
        assert pos is None


class TestDeconflictionService:
    """Test DeconflictionService class"""
    
    def test_service_creation(self):
        service = DeconflictionService(safety_buffer=50.0)
        assert service.safety_buffer == 50.0
    
    def test_no_conflict_scenario(self):
        service = DeconflictionService(safety_buffer=50.0)
        
        # Two parallel paths, far apart
        primary = DataGenerator.generate_straight_line_mission(
            (0, 0, 50), (100, 0, 50), 0, 20, "primary"
        )
        other = DataGenerator.generate_straight_line_mission(
            (0, 100, 50), (100, 100, 50), 0, 20, "other"
        )
        
        service.register_mission(other)
        is_safe, conflicts = service.check_mission(primary)
        
        assert is_safe
        assert len(conflicts) == 0
    
    def test_spatial_conflict_scenario(self):
        service = DeconflictionService(safety_buffer=50.0)
        
        # Two crossing paths
        primary = DataGenerator.generate_straight_line_mission(
            (0, 0, 50), (100, 100, 50), 0, 20, "primary"
        )
        other = DataGenerator.generate_straight_line_mission(
            (0, 100, 50), (100, 0, 50), 0, 20, "other"
        )
        
        service.register_mission(other)
        is_safe, conflicts = service.check_mission(primary)
        
        assert not is_safe
        assert len(conflicts) > 0
    
    def test_temporal_no_conflict(self):
        service = DeconflictionService(safety_buffer=50.0)
        
        # Same path, different times
        primary = DataGenerator.generate_straight_line_mission(
            (0, 0, 50), (100, 0, 50), 0, 20, "primary"
        )
        other = DataGenerator.generate_straight_line_mission(
            (0, 0, 50), (100, 0, 50), 30, 50, "other"
        )
        
        service.register_mission(other)
        is_safe, conflicts = service.check_mission(primary)
        
        assert is_safe
        assert len(conflicts) == 0
    
    def test_altitude_separation(self):
        service = DeconflictionService(safety_buffer=50.0)
        
        # Same XY path, different altitudes (sufficient separation)
        primary = DataGenerator.generate_straight_line_mission(
            (0, 0, 50), (100, 0, 50), 0, 20, "primary"
        )
        other = DataGenerator.generate_straight_line_mission(
            (0, 0, 150), (100, 0, 150), 0, 20, "other"
        )
        
        service.register_mission(other)
        is_safe, conflicts = service.check_mission(primary)
        
        assert is_safe  # 100m vertical separation should be safe
    
    def test_multiple_drones(self):
        service = DeconflictionService(safety_buffer=50.0)
        
        primary = DataGenerator.generate_straight_line_mission(
            (0, 0, 50), (100, 0, 50), 0, 20, "primary"
        )
        
        # Multiple other drones
        other1 = DataGenerator.generate_straight_line_mission(
            (0, 100, 50), (100, 100, 50), 0, 20, "other1"
        )
        other2 = DataGenerator.generate_straight_line_mission(
            (0, 200, 50), (100, 200, 50), 0, 20, "other2"
        )
        
        service.register_mission(other1)
        service.register_mission(other2)
        
        is_safe, conflicts = service.check_mission(primary)
        assert is_safe


class TestDataGenerator:
    """Test data generation utilities"""
    
    def test_straight_line_generation(self):
        mission = DataGenerator.generate_straight_line_mission(
            (0, 0, 50), (100, 100, 50), 0, 20, "test", num_waypoints=5
        )
        assert len(mission.waypoints) == 5
        assert mission.waypoints[0].x == 0
        assert mission.waypoints[-1].x == 100
    
    def test_circular_mission_generation(self):
        mission = DataGenerator.generate_circular_mission(
            (50, 50, 50), 30, 0, 20, "test", num_waypoints=8
        )
        assert len(mission.waypoints) == 9  # 8 + 1 to close circle
    
    def test_grid_pattern_generation(self):
        mission = DataGenerator.generate_grid_pattern_mission(
            (0, 0, 50), 100, 100, 5, 0, 60, "test"
        )
        assert len(mission.waypoints) == 10  # 5 rows * 2 waypoints per row


class TestScenarios:
    """Test predefined scenarios"""
    
    def test_no_conflict_scenario(self):
        primary, others = ScenarioGenerator.scenario_no_conflict()
        assert len(others) == 2
        assert len(primary.waypoints) >= 2
    
    def test_spatial_conflict_scenario(self):
        primary, others = ScenarioGenerator.scenario_spatial_conflict()
        assert len(others) >= 1
    
    def test_3d_conflict_scenario(self):
        primary, others = ScenarioGenerator.scenario_3d_conflict()
        # Check that missions have different altitudes
        assert primary.waypoints[0].z != others[0].waypoints[0].z


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_registered_missions(self):
        service = DeconflictionService(safety_buffer=50.0)
        primary = DataGenerator.generate_straight_line_mission(
            (0, 0, 50), (100, 0, 50), 0, 20, "primary"
        )
        is_safe, conflicts = service.check_mission(primary)
        assert is_safe
        assert len(conflicts) == 0
    
    def test_very_small_safety_buffer(self):
        service = DeconflictionService(safety_buffer=1.0)
        
        # Paths that would conflict with normal buffer
        primary = DataGenerator.generate_straight_line_mission(
            (0, 0, 50), (100, 0, 50), 0, 20, "primary"
        )
        other = DataGenerator.generate_straight_line_mission(
            (0, 10, 50), (100, 10, 50), 0, 20, "other"
        )
        
        service.register_mission(other)
        is_safe, conflicts = service.check_mission(primary)
        assert is_safe  # 10m separation should be safe with 1m buffer
    
    def test_very_large_safety_buffer(self):
        service = DeconflictionService(safety_buffer=200.0)
        
        # Paths that would be safe with normal buffer
        primary = DataGenerator.generate_straight_line_mission(
            (0, 0, 50), (100, 0, 50), 0, 20, "primary"
        )
        other = DataGenerator.generate_straight_line_mission(
            (0, 100, 50), (100, 100, 50), 0, 20, "other"
        )
        
        service.register_mission(other)
        is_safe, conflicts = service.check_mission(primary)
        assert not is_safe  # Should conflict with 200m buffer


if __name__ == "__main__":
    pytest.main([__file__, "-v"])