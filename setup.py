"""
Mrliouword Agent SDK - 安裝配置
"""
from setuptools import setup, find_packages
from pathlib import Path

# 讀取 README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# 讀取版本
version = {}
with open("mrliouword_agents/version.py") as f:
    exec(f.read(), version)

setup(
    name="mrliouword-agent-sdk",
    version=version["__version__"],
    description="Mrliouword Agent SDK - 智能 AI Agent 開發套件",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mrliou",
    author_email="contact@mrliou.com",
    url="https://github.com/dofaromg/mrliouword-system",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.18.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.14.2",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mrliouword=mrliouword_agents.cli.main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="ai agent sdk claude anthropic mrliouword",
    project_urls={
        "Documentation": "https://github.com/dofaromg/mrliouword-system/docs",
        "Source": "https://github.com/dofaromg/mrliouword-system",
        "Tracker": "https://github.com/dofaromg/mrliouword-system/issues",
    },
)
