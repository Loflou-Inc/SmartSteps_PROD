from setuptools import setup, find_packages
import os
import re

# Try to find version in src/__init__.py
try:
    with open(os.path.join("src", "smart_steps_ai", "__init__.py"), encoding="utf-8") as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            version = version_match.group(1)
        else:
            version = "0.1.0"
except (FileNotFoundError, IOError):
    version = "0.1.0"

setup(
    name="smart_steps_ai",
    version=version,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "anthropic>=0.13.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "matplotlib>=3.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
        "pdf": ["weasyprint>=58.0"],
    },
    author="Smart Steps Team",
    author_email="team@smartsteps.ai",
    description="AI Professional Persona module for Smart Steps application",
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "smart-steps-ai=smart_steps_ai.__main__:app",
        ],
    },
)
