from setuptools import setup, find_packages

setup(
    name="autonomous-code-verification",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
    ],
    extras_require={
        "dev": ["pytest>=7.3.0", "matplotlib>=3.7.0", "seaborn>=0.12.0"],
        "llm": ["anthropic>=0.25.0", "openai>=1.12.0", "google-generativeai>=0.5.0"],
    },
)
