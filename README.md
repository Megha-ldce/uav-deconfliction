# UAV Strategic Deconfliction System

A comprehensive system for detecting spatial and temporal conflicts in shared airspace between multiple UAV missions.

# Overview

This project implements a deconfliction service that identifies when drone flight paths come into conflict. It handles both spatial conflicts (when paths physically intersect) and temporal conflicts (when drones use the same airspace at different times). The system includes visualization tools for analyzing conflicts in 2D, 3D, and 4D (space + time).

# Key Features

- Spatial Conflict Detection - Identifies when drones' paths come within a configurable safety buffer
- Temporal Conflict Detection - Ensures no spatial overlap during overlapping time windows
- Multiple Visualization Options - 2D top-down views, 3D spatial plots, interactive Plotly visualizations, 4D animations, and time-space diagrams
- Pre-built Test Scenarios - Demonstrates various conflict types including crossing paths, altitude conflicts, and multi-drone scenarios
- Automated Testing - Comprehensive test suite with pytest
- Detailed Conflict Reports - Clear explanations with locations, times, and severity levels

# Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`
- FFmpeg (optional, for 4D animation generation)

# Installation

# Clone the Repository

```bash
git clone https://github.com/Megha-ldce/uav-deconfliction.git
cd uav-deconfliction
```

# Set Up Virtual Environment

It's recommended to use a virtual environment to manage dependencies:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

# Install Dependencies

```bash
pip install -r requirements.txt
```

# Optional: Install FFmpeg

FFmpeg is required if you want to generate 4D animation videos.

Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your system PATH

macOS:
```bash
brew install ffmpeg
```

Linux:
```bash
sudo apt-get install ffmpeg
```

# Usage

# Running Test Scenarios

To run all five test scenarios and generate visualizations:

```bash
python src/main.py
```

This will execute all scenarios, generate visualizations for each, save outputs to the `outputs/` directory, and print detailed conflict reports.

# Using the API

Here's a basic example of how to use the deconfliction service in your own code:

```python
from src.drone import Mission, Waypoint
from src.deconfliction import DeconflictionService

# Define a flight path with waypoints
waypoints = [
    Waypoint(0, 0, 50),
    Waypoint(50, 50, 50),
    Waypoint(100, 0, 50)
]

# Create a mission with time window
primary = Mission(waypoints, start_time=0, end_time=30, drone_id="drone_1")

# Initialize the deconfliction service
service = DeconflictionService(safety_buffer=50.0)

# Register additional missions if needed
# service.register_mission(other_mission)

# Check for conflicts
is_safe, conflicts = service.check_mission(primary)

if is_safe:
    print("Mission is CLEAR")
else:
    print(f"CONFLICT DETECTED: {len(conflicts)} conflicts found")
    for conflict in conflicts:
        print(conflict)
```

# Running Tests

```bash
# Run all tests
pytest tests/test_deconfliction.py -v

# Run with coverage report
pytest tests/test_deconfliction.py --cov=src --cov-report=html
```

# Project Structure

```
uav-deconfliction/
├── src/
│   ├── drone.py              # Drone and mission data structures
│   ├── deconfliction.py      # Core conflict detection engine
│   ├── data_generator.py     # Test data and scenario generation
│   ├── visualizer.py         # Visualization tools
│   └── main.py               # Main application
├── tests/
│   └── test_deconfliction.py # Comprehensive test suite
├── outputs/                   # Generated visualizations
├── requirements.txt          # Python dependencies
└── README.md
```

# Test Scenarios

The system includes five pre-built scenarios:

1. No Conflict - Drones fly in separate areas with no overlap
2. Spatial Conflict - Paths cross in space at the same time
3. Temporal Conflict - Same path used at different times
4. 3D Altitude Conflict - Testing vertical separation
5. Complex Multi-Drone - Multiple drones with various flight patterns

# Visualization Output

Each scenario generates the following files:

- `2d_view.png` - Top-down 2D view of flight paths
- `3d_view.png` - 3D spatial view showing altitude
- `interactive_3d.html` - Interactive 3D plot (open in browser)
- `time_space.png` - Time-space diagram
- `4d_animation.mp4` - Animated 4D visualization (when conflicts exist)

# Configuration

The `DeconflictionService` class accepts the following parameters:

- `safety_buffer` - Minimum safe distance between drones in meters (default: 50m)
- `time_resolution` - Time step for trajectory sampling in seconds (default: 0.1s)

# Architecture

# Conflict Detection Algorithm

The conflict detection process works as follows:

1. Temporal Filtering - First checks if missions overlap in time
2. Trajectory Sampling - Samples both trajectories at regular time intervals
3. Distance Calculation - Computes 3D Euclidean distance at each sampled time step
4. Safety Buffer Comparison - Flags violations of minimum distance requirement
5. Conflict Merging - Groups nearby time conflicts into single events

# Data Structures

- Waypoint - Immutable point in 3D space (x, y, z coordinates)
- Mission - Series of waypoints with associated time window and drone ID
- Conflict - Detailed conflict information including location, time, and severity

# Design Decisions

The current implementation prioritizes clarity and correctness. Key optimizations include:

- Early temporal filtering to skip non-overlapping missions
- Configurable sampling resolution to balance accuracy and performance
- Conflict merging to reduce duplicate reports

# Scalability Considerations

The current system is designed for development and testing purposes. For large-scale deployment with thousands of drones, the following enhancements would be necessary:

# Architecture Changes

Distributed Processing
- Microservices architecture for different geographic regions
- Load balancing across multiple deconfliction servers
- Message queues (Kafka/RabbitMQ) for asynchronous processing

Data Storage
- Distributed database (Cassandra/MongoDB) for mission storage
- Time-series database (InfluxDB) for trajectory data
- Redis cache for active missions

Spatial Indexing
- R-tree or Quadtree data structures for efficient spatial queries
- Geohashing for regional partitioning
- Only checking missions within relevant spatial regions

Temporal Optimization
- Time-window indexing
- Priority queues for near-term missions
- Archival system for completed missions

# Operational Enhancements

Conflict Resolution
- Automated path re-routing algorithms
- Priority-based resolution (emergency > commercial > recreational)
- Machine learning for optimal scheduling

Real-time Updates
- WebSocket connections for live position updates
- Event-driven architecture
- Stream processing frameworks (Apache Flink/Spark Streaming)

Fault Tolerance
- Redundant deconfliction services
- Consensus algorithms (Raft/Paxos)
- Graceful degradation under load

Monitoring
- Distributed tracing (Jaeger/Zipkin)
- Metrics collection (Prometheus/Grafana)
- Alerting for system health and performance issues

# Development Notes

This project was developed with assistance from AI tools including Claude AI for architecture design and algorithm development, and GitHub Copilot for code completion. This approach enabled rapid prototyping, comprehensive test coverage, and implementation of multiple visualization methods.

# License

This project is licensed under the MIT License. See the LICENSE file for details.

# Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch
3. Add tests for any new features
4. Submit a pull request
