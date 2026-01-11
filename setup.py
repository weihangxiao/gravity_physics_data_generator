"""Setup script."""

from setuptools import setup, find_packages
from pathlib import Path

readme = Path("README.md").read_text() if Path("README.md").exists() else ""

requirements = []
if Path("requirements.txt").exists():
    with open("requirements.txt") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="gravity-physics-data-generator",
    version="1.0.0",
    description="Gravity physics reasoning task generator with realistic vertical motion simulations",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["core", "core.*", "src", "src.*"]),
    python_requires=">=3.10",
    install_requires=requirements,
)
