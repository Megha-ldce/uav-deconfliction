# UAV Strategic Deconfliction System

A comprehensive system for detecting spatial and temporal conflicts in shared airspace between multiple UAV missions.

## 🎯 Features

- **Spatial Conflict Detection**: Identifies when drones' paths come within a configurable safety buffer
- **Temporal Conflict Detection**: Ensures no spatial overlap during overlapping time windows
- **3D/4D Visualization**: 
  - 2D top-down views
  - 3D spatial visualization
  - Interactive 3D plots (Plotly)
  - 4D animations (3D space + time)
  - Time-space diagrams
- **Multiple Test Scenarios**: Pre-built scenarios demonstrating various conflict types
- **Comprehensive Testing**: Automated test suite with pytest
- **Detailed Reporting**: Clear conflict explanations with locations, times, and severities

## 📋 Requirements

- Python 3.8+
- Libraries listed in `requirements.txt`

## 🚀 Installation

### 1. Clone or Download the Project

```bash
git clone < https://github.com/Megha-ldce/uav-deconfliction.git>
cd uav-deconfliction
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Optional: Install FFmpeg for 4D Animation

**Windows:**
- Download from https://ffmpeg.org/download.html
- Add to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

## 🎮 Usage

### Run All Test Scenarios

```bash
python src/main.py
```

This will:
1. Run 5 different test scenarios
2. Generate visualizations for each
3. Save outputs to `outputs/` directory
4. Print detailed reports

### Run Specific Scenario

```python
from src.drone import Mission, Waypoint
from src.deconfliction import DeconflictionService

# Create primary mission
waypoints = [
    Waypoint(0, 0, 50),
    Waypoint(50, 50, 50),
    Waypoint(100, 0, 50)
]
primary = Mission(waypoints, start_time=0, end_time=30, drone_id="drone_1")

# Create deconfliction service
service = DeconflictionService(safety_buffer=50.0)

# Register other missions (if any)
# service.register_mission(other_mission)

# Check for conflicts
is_safe, conflicts = service.check_mission(primary)

if is_safe:
    print("Mission is CLEAR!")
else:
    print(f"CONFLICT DETECTED: {len(conflicts)} conflicts")
    for conflict in conflicts:
        print(conflict)
```

### Run Tests

```bash
# Run all tests
pytest tests/test_deconfliction.py -v

# Run with coverage
pytest tests/test_deconfliction.py --cov=src --cov-report=html
```

## 📁 Project Structure

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
└── README.md                 # This file
```

## 🧪 Test Scenarios

1. **No Conflict**: Drones fly in separate areas with no overlap
2. **Spatial Conflict**: Paths cross in space at the same time
3. **Temporal Conflict**: Same path used at different times
4. **3D Altitude Conflict**: Testing vertical separation
5. **Complex Multi-Drone**: Multiple drones with various patterns

## 🎨 Visualizations

Each scenario generates:

- `2d_view.png` - Top-down 2D view
- `3d_view.png` - 3D spatial view
- `interactive_3d.html` - Interactive 3D plot (open in browser)
- `time_space.png` - Time-space diagram
- `4d_animation.mp4` - Animated 4D visualization (if conflicts exist)

## 🔧 Configuration

Key parameters in `DeconflictionService`:

- `safety_buffer`: Minimum safe distance between drones (default: 50m)
- `time_resolution`: Time step for trajectory sampling (default: 0.1s)

## 📊 Architecture Decisions

### Conflict Detection Algorithm

1. **Temporal Filtering**: First checks if missions overlap in time
2. **Trajectory Sampling**: Samples both trajectories at regular intervals
3. **Distance Calculation**: Computes 3D Euclidean distance at each time step
4. **Safety Buffer Comparison**: Flags violations of minimum distance
5. **Conflict Merging**: Groups nearby time conflicts into single events

### Data Structures

- **Waypoint**: Immutable point in 3D space
- **Mission**: Series of waypoints with time window
- **Conflict**: Detailed conflict information with location, time, severity

### Performance Optimizations

- Early temporal filtering to skip non-overlapping missions
- Configurable sampling resolution
- Conflict merging to reduce duplicate reports

## 🚀 Scalability Discussion

### Current System Limitations

- In-memory storage
- Synchronous processing
- Single-threaded computation
- Static mission registration

### Required for Large-Scale Deployment (10,000+ drones)

#### 1. **Distributed Architecture**
- Microservices for different regions/sectors
- Load balancing across multiple deconfliction servers
- Message queues (Kafka/RabbitMQ) for async processing

#### 2. **Data Storage**
- Distributed database (Cassandra/MongoDB) for mission storage
- Time-series database (InfluxDB) for trajectory data
- Redis cache for active missions

#### 3. **Spatial Indexing**
- R-tree or Quadtree for efficient spatial queries
- Geohashing for regional partitioning
- Only check missions within relevant spatial regions

#### 4. **Temporal Optimization**
- Time-window indexing
- Priority queues for near-term missions
- Archive completed missions

#### 5. **Conflict Resolution**
- Automated path re-routing algorithms
- Priority-based resolution (emergency > commercial > recreational)
- Machine learning for optimal scheduling

#### 6. **Real-time Updates**
- WebSocket connections for live position updates
- Event-driven architecture
- Stream processing (Apache Flink/Spark Streaming)

#### 7. **Fault Tolerance**
- Redundant deconfliction services
- Consensus algorithms (Raft/Paxos)
- Graceful degradation under load

#### 8. **Monitoring & Observability**
- Distributed tracing (Jaeger/Zipkin)
- Metrics collection (Prometheus/Grafana)
- Alerting for system health

## 🤖 AI Tool Usage

This project was developed with assistance from:

- **Claude AI**: Architecture design, algorithm development, code generation
- **GitHub Copilot**: Code completion and documentation
- Benefits: Rapid prototyping, comprehensive test coverage, multiple visualization approaches

## 📝 License

MIT License - See LICENSE file for details

## 👥 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

