"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       GRAVITY PHYSICS TASK CONFIGURATION                      ║
║                                                                               ║
║  Configuration for gravity effects physics reasoning tasks.                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Gravity Physics Task Configuration.

    Inherited from GenerationConfig:
        - num_samples: int          # Number of samples to generate
        - domain: str               # Task domain name
        - difficulty: Optional[str] # Difficulty level
        - random_seed: Optional[int] # For reproducibility
        - output_dir: Path          # Where to save outputs
        - image_size: tuple[int, int] # Image dimensions
    """

    # ══════════════════════════════════════════════════════════════════════════
    #  OVERRIDE DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════

    domain: str = Field(default="gravity_physics")
    image_size: tuple[int, int] = Field(default=(600, 800))  # Portrait for vertical motion

    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO SETTINGS
    # ══════════════════════════════════════════════════════════════════════════

    generate_videos: bool = Field(
        default=True,
        description="Whether to generate ground truth videos"
    )

    video_fps: int = Field(
        default=15,
        description="Video frame rate"
    )

    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC SETTINGS
    # ══════════════════════════════════════════════════════════════════════════

    # Ball properties
    ball_radius: int = Field(default=25, description="Ball radius in pixels")
    ball_color: tuple[int, int, int] = Field(default=(220, 60, 60), description="Ball color (RGB)")

    # Initial conditions
    min_height: float = Field(default=10.0, description="Minimum initial height (meters)")
    max_height: float = Field(default=25.0, description="Maximum initial height (meters)")
    min_initial_velocity: float = Field(default=-5.0, description="Minimum initial velocity (m/s, negative=downward)")
    max_initial_velocity: float = Field(default=10.0, description="Maximum initial velocity (m/s, positive=upward)")

    # Gravity settings
    min_gravity: float = Field(default=5.0, description="Minimum gravity (m/s²)")
    max_gravity: float = Field(default=15.0, description="Maximum gravity (m/s²)")

    # Visual settings
    show_velocity_arrow: bool = Field(default=True, description="Show initial velocity arrow")
    show_gravity_arrow: bool = Field(default=True, description="Show gravity direction arrow")
    show_height_markers: bool = Field(default=True, description="Show height markers")
    show_ground: bool = Field(default=True, description="Show ground line")

    # Animation settings
    simulation_duration: float = Field(default=3.0, description="Maximum simulation duration in seconds")
    pixels_per_meter: float = Field(default=25.0, description="Pixels per meter for rendering")
    ground_height_meters: float = Field(default=0.0, description="Ground height in meters")
