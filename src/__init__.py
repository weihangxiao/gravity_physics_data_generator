"""
Gravity Physics Task Generator.

Generates vertical motion scenarios with gravity effects using pymunk physics engine.

Main components:
    - config.py   : Task-specific configuration (TaskConfig)
    - generator.py: Gravity physics generation logic (GravityPhysicsGenerator)
    - prompts.py  : Dynamic prompt generation with physics parameters (get_prompt)
"""

from .config import TaskConfig
from .generator import GravityPhysicsGenerator, TaskGenerator
from .prompts import get_prompt

__all__ = ["TaskConfig", "GravityPhysicsGenerator", "TaskGenerator", "get_prompt"]
