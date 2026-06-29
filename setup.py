from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="mathai",
    version="1.6.3",
    description="Mathematics solving Ai tailored to NCERT",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/infinity390/mathai",
    packages=find_packages(),
    python_requires=">=3.7",
)
