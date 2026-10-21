from pathlib import Path
from setuptools import setup, find_packages

setup(
    name="mathai",
    version="2.4.8",
    description="Mathematics solving Ai tailored to NCERT",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/infinity390/mathai",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "mathai": ["ncert_data.txt"],
    },
    python_requires=">=3.7",
)
