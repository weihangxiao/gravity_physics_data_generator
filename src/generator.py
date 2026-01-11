"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     GRAVITY PHYSICS TASK GENERATOR                            ║
║                                                                               ║
║  Generates gravity effects physics tasks using pymunk physics engine.         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pymunk

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class GravityPhysicsGenerator(BaseGenerator):
    """
    Gravity Physics Task Generator.

    Generates vertical motion scenarios with gravity effects.
    """

    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)

        # Initialize video generator if enabled
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")

        # Visual settings
        self.bg_color = (255, 255, 255)  # White background
        self.ground_color = (100, 100, 100)  # Gray ground
        self.velocity_arrow_color = (60, 180, 60)  # Green for velocity
        self.gravity_arrow_color = (60, 60, 220)  # Blue for gravity
        self.text_color = (40, 40, 40)
        self.grid_color = (200, 200, 200)  # Light gray for height markers

    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one gravity physics task."""

        # Generate random gravity scenario
        gravity_data = self._generate_gravity_scenario()

        # Run physics simulation to get trajectory
        trajectory = self._simulate_gravity(gravity_data)

        # Render first and final frames
        first_image = self._render_initial_state(gravity_data)
        final_image = self._render_final_state(gravity_data, trajectory)

        # Generate video if enabled
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(gravity_data, trajectory, task_id)

        # Get prompt with specific parameters
        prompt = get_prompt(
            gravity_data["initial_height"],
            gravity_data["initial_velocity"],
            gravity_data["gravity"]
        )

        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  PHYSICS SIMULATION
    # ══════════════════════════════════════════════════════════════════════════

    def _generate_gravity_scenario(self) -> dict:
        """Generate random gravity parameters."""

        # Random initial conditions
        initial_height = random.uniform(self.config.min_height, self.config.max_height)
        initial_velocity = random.uniform(self.config.min_initial_velocity,
                                         self.config.max_initial_velocity)
        gravity = random.uniform(self.config.min_gravity, self.config.max_gravity)

        return {
            "initial_height": initial_height,
            "initial_velocity": initial_velocity,
            "gravity": gravity,
            "ball_radius": self.config.ball_radius,
        }

    def _simulate_gravity(self, scenario: dict) -> dict:
        """
        Simulate gravity motion using pymunk physics engine.

        Returns trajectory (positions and velocities over time).
        """
        # Create pymunk space
        space = pymunk.Space()
        space.gravity = (0, -scenario["gravity"] * self.config.pixels_per_meter)  # Negative Y is up

        # Create ball as pymunk body
        mass = 1.0  # Mass doesn't affect free fall in constant gravity
        radius_meters = scenario["ball_radius"] / self.config.pixels_per_meter
        moment = pymunk.moment_for_circle(mass, 0, radius_meters)
        body = pymunk.Body(mass, moment)

        # Set initial position (in physics space coordinates)
        # Y increases upward in pymunk
        body.position = (0, scenario["initial_height"] * self.config.pixels_per_meter)

        # Set initial velocity (positive = upward)
        body.velocity = (0, scenario["initial_velocity"] * self.config.pixels_per_meter)

        # Add shape
        shape = pymunk.Circle(body, radius_meters)
        shape.elasticity = 0.6  # Some bounce when hitting ground
        shape.friction = 0.5
        space.add(body, shape)

        # Add ground as static body
        ground_body = space.static_body
        ground_y = self.config.ground_height_meters * self.config.pixels_per_meter
        ground_shape = pymunk.Segment(ground_body, (-1000, ground_y), (1000, ground_y), 0.1)
        ground_shape.friction = 0.5
        ground_shape.elasticity = 0.6
        space.add(ground_shape)

        # Run simulation
        dt = 1.0 / self.config.video_fps  # Time step per frame
        num_steps = int(self.config.simulation_duration * self.config.video_fps)

        trajectory = {
            "heights": [],
            "velocities": [],
        }

        for _ in range(num_steps):
            space.step(dt)
            # Convert from pymunk coordinates back to meters
            height = body.position[1] / self.config.pixels_per_meter
            velocity = body.velocity[1] / self.config.pixels_per_meter

            trajectory["heights"].append(height)
            trajectory["velocities"].append(velocity)

            # Stop if ball has settled on ground
            if height <= self.config.ground_height_meters + 0.1 and abs(velocity) < 0.1:
                # Pad remaining frames with final state
                for _ in range(len(trajectory["heights"]), num_steps):
                    trajectory["heights"].append(height)
                    trajectory["velocities"].append(0.0)
                break

        return trajectory

    # ══════════════════════════════════════════════════════════════════════════
    #  RENDERING
    # ══════════════════════════════════════════════════════════════════════════

    def _render_initial_state(self, scenario: dict) -> Image.Image:
        """Render initial state with arrows and labels."""
        img = Image.new("RGB", self.config.image_size, self.bg_color)
        draw = ImageDraw.Draw(img)

        # Draw ground
        if self.config.show_ground:
            self._draw_ground(draw)

        # Draw height markers
        if self.config.show_height_markers:
            self._draw_height_markers(draw, scenario["initial_height"])

        # Get ball position in pixels
        ball_x, ball_y = self._meters_to_pixels(0, scenario["initial_height"])

        # Draw ball
        self._draw_ball(draw, ball_x, ball_y, scenario["ball_radius"])

        # Draw initial velocity arrow
        if self.config.show_velocity_arrow and abs(scenario["initial_velocity"]) > 0.1:
            self._draw_velocity_arrow(draw, ball_x, ball_y, scenario["initial_velocity"],
                                     scenario["ball_radius"])

        # Draw gravity arrow
        if self.config.show_gravity_arrow:
            self._draw_gravity_arrow(draw, scenario["gravity"])

        return img

    def _render_final_state(self, scenario: dict, trajectory: dict) -> Image.Image:
        """Render final state after gravity motion."""
        img = Image.new("RGB", self.config.image_size, self.bg_color)
        draw = ImageDraw.Draw(img)

        # Draw ground
        if self.config.show_ground:
            self._draw_ground(draw)

        # Find a good frame for final state (where ball is clearly visible)
        final_frame_idx = self._find_final_frame_index(scenario, trajectory)

        # Draw height markers
        if self.config.show_height_markers:
            final_height = trajectory["heights"][final_frame_idx]
            self._draw_height_markers(draw, max(scenario["initial_height"], final_height))

        # Get final position at the selected frame
        final_height = trajectory["heights"][final_frame_idx]
        final_velocity = trajectory["velocities"][final_frame_idx]
        ball_x, ball_y = self._meters_to_pixels(0, final_height)

        # Draw ball
        self._draw_ball(draw, ball_x, ball_y, scenario["ball_radius"])

        # Draw final velocity arrow (if still moving)
        if self.config.show_velocity_arrow and abs(final_velocity) > 0.5:
            self._draw_velocity_arrow(draw, ball_x, ball_y, final_velocity,
                                     scenario["ball_radius"])

        return img

    def _find_final_frame_index(self, scenario: dict, trajectory: dict) -> int:
        """
        Find the best frame for the final state image.

        Criteria:
        1. Ball is visible (not below ground or off-screen)
        2. Prefer when ball has settled or is at lowest bounce point
        3. Ensure ball is well-positioned in frame

        Returns the frame index to use for the final state.
        """
        heights = trajectory["heights"]
        velocities = trajectory["velocities"]

        width, height = self.config.image_size
        ball_radius_meters = scenario["ball_radius"] / self.config.pixels_per_meter

        # Find when ball settles (velocity near zero and on ground)
        for i in range(len(heights) - 1, -1, -1):
            h = heights[i]
            v = velocities[i]

            # Ball on ground and settled
            if h <= ball_radius_meters * 1.5 and abs(v) < 1.0:
                # Check if ball is visible in frame
                _, ball_y = self._meters_to_pixels(0, h)
                ground_y = height - 50

                # Make sure ball is above ground visual element
                if ball_y < ground_y - scenario["ball_radius"]:
                    return i

        # Fallback 1: Find lowest point that's visible
        for i in range(len(heights) - 1, -1, -1):
            h = heights[i]
            _, ball_y = self._meters_to_pixels(0, h)
            ground_y = height - 50

            # Ball is visible (above ground line with margin)
            if ball_y < ground_y - scenario["ball_radius"] - 5 and h >= 0:
                return i

        # Fallback 2: Use frame at 80% through simulation
        return int(len(heights) * 0.8)

    def _draw_ball(self, draw: ImageDraw.Draw, x: float, y: float, radius: float):
        """Draw a ball."""
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                    fill=self.config.ball_color, outline=(0, 0, 0), width=2)

    def _draw_ground(self, draw: ImageDraw.Draw):
        """Draw ground line."""
        width, height = self.config.image_size
        ground_y = height - 50  # 50 pixels from bottom
        draw.rectangle([0, ground_y, width, height], fill=self.ground_color)
        draw.line([(0, ground_y), (width, ground_y)], fill=(60, 60, 60), width=3)

    def _draw_height_markers(self, draw: ImageDraw.Draw, max_height: float):
        """Draw height markers on the left side."""
        width, height = self.config.image_size
        font = self._get_font(14)

        # Draw markers every 5 meters
        for h in range(0, int(max_height) + 6, 5):
            _, y = self._meters_to_pixels(0, h)
            if 20 < y < height - 60:  # Keep within visible area
                # Draw line
                draw.line([(10, y), (30, y)], fill=self.grid_color, width=2)
                # Draw label
                draw.text((35, y - 8), f"{h}m", fill=self.text_color, font=font)

    def _draw_velocity_arrow(self, draw: ImageDraw.Draw, x: float, y: float,
                            velocity: float, radius: float):
        """Draw initial velocity arrow."""
        # Arrow length proportional to velocity
        arrow_scale = 5  # pixels per m/s
        arrow_length = velocity * arrow_scale

        # Arrow starts from edge of ball
        if velocity > 0:  # Upward
            start_y = y - radius
            end_y = start_y - arrow_length
        else:  # Downward
            start_y = y + radius
            end_y = start_y - arrow_length  # arrow_length is negative

        # Don't draw if velocity is too small
        if abs(arrow_length) < 5:
            return

        # Draw arrow line
        draw.line([x, start_y, x, end_y], fill=self.velocity_arrow_color, width=3)

        # Draw arrowhead
        arrow_size = 8
        if velocity > 0:  # Upward arrow
            draw.polygon([
                (x, end_y),
                (x - arrow_size // 2, end_y + arrow_size),
                (x + arrow_size // 2, end_y + arrow_size)
            ], fill=self.velocity_arrow_color)
        else:  # Downward arrow
            draw.polygon([
                (x, end_y),
                (x - arrow_size // 2, end_y - arrow_size),
                (x + arrow_size // 2, end_y - arrow_size)
            ], fill=self.velocity_arrow_color)

        # Draw velocity label
        font = self._get_font(14)
        vel_text = f"v={abs(velocity):.1f} m/s"
        label_x = x + 15
        label_y = (start_y + end_y) / 2 - 8
        draw.text((label_x, label_y), vel_text, fill=self.velocity_arrow_color, font=font)

    def _draw_gravity_arrow(self, draw: ImageDraw.Draw, gravity: float):
        """Draw gravity indicator in top-right corner."""
        width, height = self.config.image_size
        font = self._get_font(16)

        # Position in top-right
        x = width - 80
        y = 30

        # Draw downward arrow
        arrow_length = 40
        draw.line([x, y, x, y + arrow_length], fill=self.gravity_arrow_color, width=3)
        draw.polygon([
            (x, y + arrow_length),
            (x - 6, y + arrow_length - 10),
            (x + 6, y + arrow_length - 10)
        ], fill=self.gravity_arrow_color)

        # Draw label
        text = f"g={gravity:.1f}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text((x - text_width // 2, y + arrow_length + 5), text,
                 fill=self.gravity_arrow_color, font=font)

    def _meters_to_pixels(self, x_meters: float, y_meters: float) -> tuple[float, float]:
        """Convert meters to pixel coordinates."""
        width, height = self.config.image_size

        # X: center of image
        pixel_x = width // 2 + x_meters * self.config.pixels_per_meter

        # Y: bottom is ground (height - 50), top is higher
        ground_pixel_y = height - 50
        pixel_y = ground_pixel_y - (y_meters - self.config.ground_height_meters) * self.config.pixels_per_meter

        return (pixel_x, pixel_y)

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get a font for text rendering."""
        font_paths = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "Arial.ttf",
        ]

        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue

        return ImageFont.load_default()

    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO GENERATION
    # ══════════════════════════════════════════════════════════════════════════

    def _generate_video(self, scenario: dict, trajectory: dict, task_id: str) -> str:
        """Generate ground truth video showing gravity motion."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"

        # Create animation frames
        frames = self._create_animation_frames(scenario, trajectory)

        result = self.video_generator.create_video_from_frames(frames, video_path)
        return str(result) if result else None

    def _create_animation_frames(self, scenario: dict, trajectory: dict) -> list:
        """Create animation frames showing gravity motion."""
        frames = []
        width, height = self.config.image_size

        num_frames = len(trajectory["heights"])

        for i in range(num_frames):
            # Create frame
            img = Image.new("RGB", self.config.image_size, self.bg_color)
            draw = ImageDraw.Draw(img)

            # Draw ground
            if self.config.show_ground:
                self._draw_ground(draw)

            # Draw height markers
            if self.config.show_height_markers:
                max_height = max(scenario["initial_height"], max(trajectory["heights"]))
                self._draw_height_markers(draw, max_height)

            # Get position for this frame
            current_height = trajectory["heights"][i]
            ball_x, ball_y = self._meters_to_pixels(0, current_height)

            # Draw ball
            self._draw_ball(draw, ball_x, ball_y, scenario["ball_radius"])

            # Draw gravity arrow (constant throughout)
            if self.config.show_gravity_arrow:
                self._draw_gravity_arrow(draw, scenario["gravity"])

            frames.append(img)

        return frames


# Backward compatibility alias
TaskGenerator = GravityPhysicsGenerator
