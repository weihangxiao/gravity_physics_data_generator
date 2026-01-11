"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          GRAVITY PHYSICS PROMPTS                              ║
║                                                                               ║
║  Prompts for gravity effects physics reasoning tasks.                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


def get_prompt(height: float, initial_velocity: float, gravity: float) -> str:
    """
    Generate a prompt for gravity physics task.

    Args:
        height: Initial height in meters
        initial_velocity: Initial velocity in m/s (positive=upward, negative=downward)
        gravity: Gravity acceleration in m/s²

    Returns:
        Formatted prompt string with specific parameters
    """
    # Determine velocity description
    if initial_velocity > 0.5:
        velocity_desc = f"initial upward velocity {initial_velocity:.1f} m/s"
    elif initial_velocity < -0.5:
        velocity_desc = f"initial downward velocity {abs(initial_velocity):.1f} m/s"
    else:
        velocity_desc = "dropped from rest (velocity = 0)"

    # Determine gravity environment description
    if 9.5 <= gravity <= 10.0:
        gravity_env = f"Earth-like gravity ({gravity:.1f} m/s²)"
    elif 1.0 <= gravity <= 2.0:
        gravity_env = f"Moon-like gravity ({gravity:.1f} m/s²)"
    elif 3.0 <= gravity <= 4.5:
        gravity_env = f"Mars-like gravity ({gravity:.1f} m/s²)"
    elif gravity > 12.0:
        gravity_env = f"heavy planet gravity ({gravity:.1f} m/s²)"
    else:
        gravity_env = f"gravity {gravity:.1f} m/s²"

    # Choose a random template
    templates = [
        f"Ball at height {height:.1f}m with {velocity_desc} experiences {gravity_env}. Predict the motion under gravity.",

        f"Initial conditions: height = {height:.1f}m, {velocity_desc}, gravity = {gravity:.1f} m/s². Show the trajectory and final position.",

        f"Object starts at {height:.1f}m height with {velocity_desc}. Gravity acceleration is {gravity:.1f} m/s². Animate the motion following physics.",

        f"Under {gravity_env}, a ball at {height:.1f}m with {velocity_desc} begins motion. Predict and show the complete trajectory.",
    ]

    return random.choice(templates)


def get_simple_prompt() -> str:
    """Get a simple generic prompt (for fallback)."""
    return "Predict the motion of an object under gravity following physics rules."
