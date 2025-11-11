"""
Visualization tools for drone missions and conflicts
"""
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import List, Dict
import plotly.graph_objects as go
import plotly.express as px

from drone import Mission, Waypoint
from deconfliction import Conflict


class Visualizer:
    """Visualization tools for drone deconfliction"""
    
    def __init__(self):
        self.colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    def plot_2d_missions(self, missions: List[Mission], conflicts: List[Conflict] = None, 
                         save_path: str = None):
        """Plot missions in 2D (top-down view)"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot each mission
        for i, mission in enumerate(missions):
            color = self.colors[i % len(self.colors)]
            
            # Extract coordinates
            x_coords = [wp.x for wp in mission.waypoints]
            y_coords = [wp.y for wp in mission.waypoints]
            
            # Plot path
            ax.plot(x_coords, y_coords, '-o', color=color, 
                   label=f'{mission.drone_id}', linewidth=2, markersize=6)
            
            # Mark start and end
            ax.plot(x_coords[0], y_coords[0], 'o', color=color, 
                   markersize=12, markeredgecolor='black', markeredgewidth=2)
            ax.text(x_coords[0], y_coords[0], ' START', fontsize=10, color=color)
            
            ax.plot(x_coords[-1], y_coords[-1], 's', color=color, 
                   markersize=12, markeredgecolor='black', markeredgewidth=2)
            ax.text(x_coords[-1], y_coords[-1], ' END', fontsize=10, color=color)
        
        # Plot conflicts
        if conflicts:
            for conflict in conflicts:
                ax.plot(conflict.location.x, conflict.location.y, 'rx', 
                       markersize=15, markeredgewidth=3, label='Conflict')
                
                # Draw safety circle
                circle = plt.Circle((conflict.location.x, conflict.location.y), 
                                   conflict.distance, color='red', fill=False, 
                                   linestyle='--', alpha=0.5)
                ax.add_patch(circle)
        
        ax.set_xlabel('X Position (m)', fontsize=12)
        ax.set_ylabel('Y Position (m)', fontsize=12)
        ax.set_title('UAV Mission Deconfliction - 2D View', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved 2D plot to {save_path}")
        
        plt.tight_layout()
        return fig
    
    def plot_3d_missions(self, missions: List[Mission], conflicts: List[Conflict] = None,
                        save_path: str = None):
        """Plot missions in 3D"""
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot each mission
        for i, mission in enumerate(missions):
            color = self.colors[i % len(self.colors)]
            
            # Extract coordinates
            x_coords = [wp.x for wp in mission.waypoints]
            y_coords = [wp.y for wp in mission.waypoints]
            z_coords = [wp.z for wp in mission.waypoints]
            
            # Plot path
            ax.plot(x_coords, y_coords, z_coords, '-o', color=color,
                   label=f'{mission.drone_id}', linewidth=2, markersize=5)
            
            # Mark start and end
            ax.scatter(x_coords[0], y_coords[0], z_coords[0], 
                      color=color, s=150, marker='o', edgecolors='black', linewidths=2)
            ax.scatter(x_coords[-1], y_coords[-1], z_coords[-1],
                      color=color, s=150, marker='s', edgecolors='black', linewidths=2)
        
        # Plot conflicts
        if conflicts:
            for conflict in conflicts:
                ax.scatter(conflict.location.x, conflict.location.y, conflict.location.z,
                          color='red', s=200, marker='x', linewidths=4, label='Conflict')
        
        ax.set_xlabel('X Position (m)', fontsize=11)
        ax.set_ylabel('Y Position (m)', fontsize=11)
        ax.set_zlabel('Z Position (altitude, m)', fontsize=11)
        ax.set_title('UAV Mission Deconfliction - 3D View', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved 3D plot to {save_path}")
        
        plt.tight_layout()
        return fig
    
    def create_4d_animation(self, missions: List[Mission], conflicts: List[Conflict] = None,
                           save_path: str = None, duration: int = 10):
        """Create 4D animation (3D space + time)"""
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Find time bounds
        min_time = min(m.start_time for m in missions)
        max_time = max(m.end_time for m in missions)
        
        # Animation parameters
        fps = 30
        num_frames = duration * fps
        
        def update(frame):
            ax.clear()
            
            # Calculate current time
            current_time = min_time + (max_time - min_time) * frame / num_frames
            
            # Plot each mission's trajectory (faded)
            for i, mission in enumerate(missions):
                color = self.colors[i % len(self.colors)]
                x_coords = [wp.x for wp in mission.waypoints]
                y_coords = [wp.y for wp in mission.waypoints]
                z_coords = [wp.z for wp in mission.waypoints]
                
                ax.plot(x_coords, y_coords, z_coords, '-', color=color,
                       alpha=0.3, linewidth=1)
            
            # Plot current positions
            for i, mission in enumerate(missions):
                color = self.colors[i % len(self.colors)]
                pos, _ = mission.get_position_at_time(current_time)
                
                if pos:
                    ax.scatter(pos.x, pos.y, pos.z, color=color, s=200,
                             marker='o', edgecolors='black', linewidths=2,
                             label=f'{mission.drone_id}')
                    
                    # Draw trajectory up to current point
                    samples = mission.get_trajectory_samples(100)
                    current_samples = [(t, p) for t, p in samples if t <= current_time]
                    
                    if len(current_samples) > 1:
                        xs = [p.x for _, p in current_samples]
                        ys = [p.y for _, p in current_samples]
                        zs = [p.z for _, p in current_samples]
                        ax.plot(xs, ys, zs, color=color, linewidth=2, alpha=0.7)
            
            # Highlight conflicts at current time
            if conflicts:
                for conflict in conflicts:
                    if abs(conflict.time - current_time) < 0.5:  # Within 0.5s
                        ax.scatter(conflict.location.x, conflict.location.y, 
                                 conflict.location.z, color='red', s=300,
                                 marker='x', linewidths=5)
            
            ax.set_xlabel('X Position (m)')
            ax.set_ylabel('Y Position (m)')
            ax.set_zlabel('Z Position (altitude, m)')
            ax.set_title(f'4D Visualization (Time: {current_time:.2f}s)', 
                        fontsize=14, fontweight='bold')
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)
            
            # Set consistent axis limits
            all_x = [wp.x for m in missions for wp in m.waypoints]
            all_y = [wp.y for m in missions for wp in m.waypoints]
            all_z = [wp.z for m in missions for wp in m.waypoints]
            
            ax.set_xlim([min(all_x) - 10, max(all_x) + 10])
            ax.set_ylim([min(all_y) - 10, max(all_y) + 10])
            ax.set_zlim([min(all_z) - 10, max(all_z) + 10])
        
        anim = FuncAnimation(fig, update, frames=num_frames, interval=1000/fps)
        
        if save_path:
            writer = FFMpegWriter(fps=fps, bitrate=1800)
            anim.save(save_path, writer=writer)
            print(f"Saved 4D animation to {save_path}")
        
        return anim
    
    def plot_interactive_3d(self, missions: List[Mission], conflicts: List[Conflict] = None,
                           save_path: str = None):
        """Create interactive 3D plot using Plotly"""
        fig = go.Figure()
        
        # Plot each mission
        for i, mission in enumerate(missions):
            color = px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
            
            x_coords = [wp.x for wp in mission.waypoints]
            y_coords = [wp.y for wp in mission.waypoints]
            z_coords = [wp.z for wp in mission.waypoints]
            
            # Add trajectory line
            fig.add_trace(go.Scatter3d(
                x=x_coords, y=y_coords, z=z_coords,
                mode='lines+markers',
                name=mission.drone_id,
                line=dict(color=color, width=4),
                marker=dict(size=5)
            ))
            
            # Add start marker
            fig.add_trace(go.Scatter3d(
                x=[x_coords[0]], y=[y_coords[0]], z=[z_coords[0]],
                mode='markers',
                name=f'{mission.drone_id} start',
                marker=dict(size=12, color=color, symbol='circle',
                           line=dict(color='black', width=2)),
                showlegend=False
            ))
            
            # Add end marker
            fig.add_trace(go.Scatter3d(
                x=[x_coords[-1]], y=[y_coords[-1]], z=[z_coords[-1]],
                mode='markers',
                name=f'{mission.drone_id} end',
                marker=dict(size=12, color=color, symbol='square',
                           line=dict(color='black', width=2)),
                showlegend=False
            ))
        
        # Plot conflicts
        if conflicts:
            conflict_x = [c.location.x for c in conflicts]
            conflict_y = [c.location.y for c in conflicts]
            conflict_z = [c.location.z for c in conflicts]
            
            fig.add_trace(go.Scatter3d(
                x=conflict_x, y=conflict_y, z=conflict_z,
                mode='markers',
                name='Conflicts',
                marker=dict(size=15, color='red', symbol='x',
                           line=dict(color='darkred', width=3))
            ))
        
        fig.update_layout(
            title='Interactive 3D UAV Mission Visualization',
            scene=dict(
                xaxis_title='X Position (m)',
                yaxis_title='Y Position (m)',
                zaxis_title='Z Position (altitude, m)',
                aspectmode='data'
            ),
            width=1200,
            height=800
        )
        
        if save_path:
            fig.write_html(save_path)
            print(f"Saved interactive 3D plot to {save_path}")
        
        return fig
    
    def plot_time_space_diagram(self, missions: List[Mission], conflicts: List[Conflict] = None,
                               save_path: str = None):
        """Create time-space diagram showing when/where drones are"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot X vs Time
        for i, mission in enumerate(missions):
            color = self.colors[i % len(self.colors)]
            samples = mission.get_trajectory_samples(200)
            
            times = [t for t, _ in samples]
            x_positions = [p.x for _, p in samples]
            
            ax1.plot(times, x_positions, color=color, linewidth=2, 
                    label=mission.drone_id)
        
        if conflicts:
            for conflict in conflicts:
                ax1.plot(conflict.time, conflict.location.x, 'rx', 
                        markersize=12, markeredgewidth=3)
        
        ax1.set_xlabel('Time (s)', fontsize=11)
        ax1.set_ylabel('X Position (m)', fontsize=11)
        ax1.set_title('Time-Space Diagram (X coordinate)', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot Y vs Time
        for i, mission in enumerate(missions):
            color = self.colors[i % len(self.colors)]
            samples = mission.get_trajectory_samples(200)
            
            times = [t for t, _ in samples]
            y_positions = [p.y for _, p in samples]
            
            ax2.plot(times, y_positions, color=color, linewidth=2,
                    label=mission.drone_id)
        
        if conflicts:
            for conflict in conflicts:
                ax2.plot(conflict.time, conflict.location.y, 'rx',
                        markersize=12, markeredgewidth=3)
        
        ax2.set_xlabel('Time (s)', fontsize=11)
        ax2.set_ylabel('Y Position (m)', fontsize=11)
        ax2.set_title('Time-Space Diagram (Y coordinate)', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved time-space diagram to {save_path}")
        
        plt.tight_layout()
        return fig