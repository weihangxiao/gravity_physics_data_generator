# Gravity Physics Data Generator 🌍

A synthetic reasoning task generator that creates gravity physics problems with realistic vertical motion simulations using the pymunk physics engine.

---

## 🎯 What It Generates

This generator creates tasks where a ball undergoes vertical motion under gravity. Each task includes:
- **Initial state**: Ball at a specific height with initial velocity (upward, downward, or at rest)
- **Gravity acceleration**: Varying gravity (5-15 m/s²) representing different planetary environments
- **Final state**: Ball position after motion (may bounce on ground)
- **Ground truth video**: Complete trajectory animation showing the motion

### Example Task

**Prompt:**
> "Under gravity 8.5 m/s², a ball at 20.2m with initial downward velocity 2.9 m/s begins motion. Predict and show the complete trajectory."

**Initial State**: Ball at 20.2m with downward velocity indicator
**Final State**: Ball at rest on ground or at a lower position
**Video**: 3-second animation showing complete vertical motion with bounces

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/gravity-physics-data-generator.git
cd gravity-physics-data-generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python examples/generate.py --num-samples 50
```

---

## 📋 Requirements

- **Python**: 3.10+
- **Key Dependencies**:
  - `pymunk==6.9.0` - Physics simulation engine
  - `Pillow>=10.0.0` - Image rendering
  - `opencv-python>=4.8.0` - Video generation
  - `pydantic>=2.0.0` - Configuration validation

See `requirements.txt` for full dependencies.

---

## 📁 Output Format

Each generated task creates a folder with:

```
data/questions/gravity_physics_task/{task_id}/
├── first_frame.png          # Initial state with ball, velocity arrow, gravity indicator
├── final_frame.png          # Final state showing ball at lower position or on ground
├── prompt.txt               # Task description with specific parameters
└── ground_truth.mp4         # Video showing complete vertical motion trajectory
```

### Visual Elements

**First Frame**:
- Ball at initial height
- Green velocity arrow (if moving initially)
- Blue gravity indicator in top-right corner
- Height markers on left side (every 5m)
- Gray ground at bottom

**Final Frame**:
- Ball at final position
- Velocity arrow (if still moving)
- Same visual layout for consistency

**Video**:
- 3-second animation at 15 FPS
- Shows complete trajectory: rise/fall, bounces, settling
- Consistent physics using pymunk engine

---

## ⚙️ Configuration

### Task Parameters (in `src/config.py`)

```python
class TaskConfig(GenerationConfig):
    # Layout (portrait for vertical motion)
    domain: str = "gravity_physics"
    image_size: tuple[int, int] = (600, 800)  # Portrait orientation

    # Physics parameters
    min_height: float = 10.0      # Minimum initial height (meters)
    max_height: float = 25.0      # Maximum initial height (meters)
    min_initial_velocity: float = -5.0   # Min velocity (negative = downward)
    max_initial_velocity: float = 10.0   # Max velocity (positive = upward)
    min_gravity: float = 5.0      # Minimum gravity (m/s²)
    max_gravity: float = 15.0     # Maximum gravity (m/s²)

    # Visual settings
    ball_radius: int = 20         # Ball radius in pixels
    ball_color: tuple[int, int, int] = (220, 80, 80)  # Red ball
    show_velocity_arrow: bool = True     # Show velocity indicator
    show_gravity_arrow: bool = True      # Show gravity indicator
    show_height_markers: bool = True     # Show height scale

    # Simulation
    simulation_duration: float = 3.0     # Simulation length (seconds)
    video_fps: int = 15                  # Video frame rate
    pixels_per_meter: float = 20.0       # Scale factor
```

### Generation Parameters

```bash
# Basic generation
python examples/generate.py --num-samples 100

# Custom output directory
python examples/generate.py --num-samples 50 --output-dir ./my_data

# Set random seed for reproducibility
python examples/generate.py --num-samples 50 --seed 42

# Adjust image size (portrait recommended)
python examples/generate.py --num-samples 50 --image-size 800 1200
```

---

## 🎨 Physics Simulation Details

### Gravity Scenarios

The generator creates diverse scenarios with:

1. **Initial Height**: 10-25 meters above ground
2. **Initial Velocity**:
   - Upward: +2 to +10 m/s (ball thrown upward)
   - Downward: -5 to -2 m/s (ball thrown downward)
   - At rest: ~0 m/s (ball dropped)
3. **Gravity**: 5-15 m/s² (represents different planetary environments)

### Prompt Variations

Prompts are dynamically generated with environment descriptions:

- **Earth-like gravity** (9.5-10.0 m/s²)
- **Moon-like gravity** (1.0-2.0 m/s²)
- **Mars-like gravity** (3.0-4.5 m/s²)
- **Heavy planet gravity** (>12.0 m/s²)
- Generic description for other values

Example prompts:
- "Ball at height 20.3m with initial upward velocity 2.7 m/s experiences gravity 5.6 m/s². Predict the motion under gravity."
- "Initial conditions: height = 15.8m, dropped from rest (velocity = 0), gravity = 9.8 m/s². Show the trajectory and final position."
- "Object starts at 12.5m height with initial downward velocity 3.2 m/s. Gravity acceleration is 7.4 m/s². Animate the motion following physics."

### Physics Engine

Uses **pymunk** for accurate physics simulation:
- Realistic free fall motion following kinematic equations
- Elastic bounces when hitting ground (elasticity = 0.6)
- Friction effects (coefficient = 0.5)
- Proper mass and moment of inertia
- Conservation of energy and momentum

Kinematic equations:
- Velocity: `v = v₀ + gt`
- Position: `h = h₀ + v₀t - ½gt²`

---

## 📊 Example Tasks

### Task 1: Drop from Rest
- Initial: Ball at 12.7m, velocity = 0, gravity = 11.4 m/s²
- Prompt: "Ball at height 12.7m with dropped from rest (velocity = 0) experiences gravity 11.4 m/s². Predict the motion under gravity."
- Result: Ball accelerates downward, bounces on ground, settles

### Task 2: Upward Launch
- Initial: Ball at 20.3m, upward velocity = 2.7 m/s, gravity = 5.6 m/s²
- Prompt: "Ball at height 20.3m with initial upward velocity 2.7 m/s experiences gravity 5.6 m/s². Predict the motion under gravity."
- Result: Ball rises to peak, falls back down, bounces, settles

### Task 3: Downward Launch
- Initial: Ball at 20.2m, downward velocity = 2.9 m/s, gravity = 8.5 m/s²
- Prompt: "Under gravity 8.5 m/s², a ball at 20.2m with initial downward velocity 2.9 m/s begins motion. Predict and show the complete trajectory."
- Result: Ball accelerates downward, hits ground harder, bounces higher, settles

---

## 🔧 Customization

### Modify Physics Parameters

Edit `src/config.py` to change:
- Height range
- Velocity range
- Gravity range
- Ball properties (size, color, elasticity)
- Simulation duration

### Modify Visual Appearance

In `src/generator.py`, customize:
- Colors (ball, ground, arrows, text)
- Arrow styles and sizes
- Height marker spacing
- Ground appearance

### Add Custom Prompts

Edit `src/prompts.py` to add new prompt templates:

```python
templates = [
    f"Your custom prompt with {height:.1f}m and {velocity:.1f} m/s",
    # Add more templates
]
```

---

## 📁 Project Structure

```
gravity-physics-data-generator/
├── core/                      # Standard utilities (shared across generators)
│   ├── base_generator.py     # Abstract base class
│   ├── schemas.py            # Pydantic models (TaskPair, etc.)
│   ├── image_utils.py        # Image rendering helpers
│   ├── video_utils.py        # Video generation utilities
│   └── output_writer.py      # File output handler
├── src/                       # Gravity physics task implementation
│   ├── generator.py          # GravityPhysicsGenerator class
│   ├── prompts.py            # Dynamic prompt generation
│   └── config.py             # Task configuration
├── examples/
│   └── generate.py           # Main entry point
├── data/questions/           # Generated output
│   └── gravity_physics_task/
└── requirements.txt          # Dependencies
```

---

## 🧪 Testing

```bash
# Generate 1 sample to verify setup
python examples/generate.py --num-samples 1

# Check output
ls -la data/questions/gravity_physics_task/gravity_physics_0000/
# Should contain: first_frame.png, final_frame.png, prompt.txt, ground_truth.mp4

# View the video
open data/questions/gravity_physics_task/gravity_physics_0000/ground_truth.mp4
```

---

## 🚨 Troubleshooting

### Video generation fails
- Install ffmpeg: `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux)
- Or disable videos: Set `generate_videos: False` in config

### Import errors
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall: `pip install -e .`

### Ball not visible in final frame
- The generator automatically selects the best final frame where the ball is visible
- If issues persist, adjust `simulation_duration` or `video_fps` in config

### Physics looks wrong
- Check `pixels_per_meter` scaling factor in config
- Verify pymunk is installed: `pip install pymunk==6.9.0`
- Ensure gravity and velocity ranges are reasonable

---

## 📖 Physics Concepts

This generator is useful for:
- Testing AI understanding of vertical motion
- Evaluating trajectory prediction
- Assessing understanding of gravity effects
- Teaching kinematics and dynamics
- Generating training data for physics reasoning models

Key concepts tested:
- Free fall motion
- Projectile motion (vertical)
- Acceleration due to gravity
- Elastic collisions with ground
- Energy conservation
- Velocity and position relationships

---

## 📝 License

MIT License - See LICENSE file for details