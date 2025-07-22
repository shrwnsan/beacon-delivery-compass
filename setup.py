from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="beaconled",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Your delivery compass for empowered product builders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shrwnsan/beaconled-delivery-compass",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "colorama>=0.4.4",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "beaconled=beaconled.cli:main",
        ],
    },
)
