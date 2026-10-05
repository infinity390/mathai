from pathlib import Path
from setuptools import setup, find_packages

setup(
    name="mathai",
    version="2.2.8",
    description="Mathematics solving Ai tailored to NCERT",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/infinity390/mathai",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "more_itertools"
    ],
)
