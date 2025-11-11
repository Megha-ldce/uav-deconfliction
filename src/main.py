"""
Main application for UAV deconfliction system
"""
import os
import sys
from typing import List

from drone import Mission
from deconfliction import DeconflictionService, Conflict
from data_generator import ScenarioGenerator
from visualizer import Visualizer


def run_scenario(scenario_name: str, primary: Mission, others: List[Mission],
                safety_buffer: float = 50.0):
    """Run a complete deconfliction scenario"""
    
    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*80}\n")
    
    # Initialize deconfliction service
    service = DeconflictionService(safety_buffer=safety_buffer)
    
    # Register other missions
    for mission in others:
        service.register_mission(mission)
    
    # Check primary mission
    is_safe, conflicts = service.check_mission(primary)
    
    # Print detailed report
    report = service.get_detailed_report(primary)
    print(report)
    
    # Create visualizations
    viz = Visualizer()
    all_missions = [primary] + others
    
    # Create output directory
    output_dir = f"outputs/{scenario_name.replace(' ', '_').lower()}"
    os.makedirs(output_dir, exist_ok=True)
    
    # 2D Plot
    print(f"\nGenerating 2D visualization...")
    fig_2d = viz.plot_2d_missions(all_missions, conflicts, 
                                   save_path=f"{output_dir}/2d_view.png")
    
    # 3D Plot
    print(f"Generating 3D visualization...")
    fig_3d = viz.plot_3d_missions(all_missions, conflicts,
                                   save_path=f"{output_dir}/3d_view.png")
    
    # Interactive 3D
    print(f"Generating interactive 3D visualization...")
    viz.plot_interactive_3d(all_missions, conflicts,
                           save_path=f"{output_dir}/interactive_3d.html")
    
    # Time-space diagram
    print(f"Generating time-space diagram...")
    viz.plot_time_space_diagram(all_missions, conflicts,
                               save_path=f"{output_dir}/time_space.png")
    
    # 4D Animation (only if conflicts exist, to save time)
    if conflicts:
        print(f"Generating 4D animation (this may take a minute)...")
        try:
            viz.create_4d_animation(all_missions, conflicts,
                                   save_path=f"{output_dir}/4d_animation.mp4",
                                   duration=8)
        except Exception as e:
            print(f"Warning: Could not create 4D animation: {e}")
            print("(FFmpeg may not be installed)")
    
    print(f"\n✓ All visualizations saved to {output_dir}/")
    
    return is_safe, conflicts, service


def main():
    """Main entry point"""
    
    print("\n" + "="*80)
    print(" UAV STRATEGIC DECONFLICTION SYSTEM")
    print(" Demonstration and Testing")
    print("="*80 + "\n")
    
    # Create main output directory
    os.makedirs("outputs", exist_ok=True)
    
    scenarios = [
        ("No Conflict", ScenarioGenerator.scenario_no_conflict),
        ("Spatial Conflict", ScenarioGenerator.scenario_spatial_conflict),
        ("Temporal Conflict", ScenarioGenerator.scenario_temporal_conflict),
        ("3D Altitude Conflict", ScenarioGenerator.scenario_3d_conflict),
        ("Complex Multi-Drone", ScenarioGenerator.scenario_complex_multi_drone),
    ]
    
    results = []
    
    for scenario_name, scenario_func in scenarios:
        try:
            primary, others = scenario_func()
            is_safe, conflicts, service = run_scenario(scenario_name, primary, others)
            results.append((scenario_name, is_safe, len(conflicts)))
        except Exception as e:
            print(f"\n✗ Error in scenario '{scenario_name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((scenario_name, False, -1))
    
    # Print summary
    print("\n" + "="*80)
    print(" SUMMARY OF ALL SCENARIOS")
    print("="*80 + "\n")
    
    print(f"{'Scenario':<30} {'Status':<15} {'Conflicts':<10}")
    print("-" * 80)
    
    for scenario_name, is_safe, num_conflicts in results:
        status = "✓ CLEAR" if is_safe else "✗ CONFLICT"
        conflicts_str = "0" if is_safe else str(num_conflicts)
        print(f"{scenario_name:<30} {status:<15} {conflicts_str:<10}")
    
    print("\n" + "="*80)
    print(" All scenarios completed!")
    print(" Check the 'outputs/' directory for visualizations")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()