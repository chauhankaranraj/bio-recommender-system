from setuptools import setup, find_packages

setup(
    name="biology-recommender",
    version="1.0.0",
    author="ShivaniPimparkar111",
    description="PhD-level gene–disease recommender system",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pandas>=2.1.0",
        "numpy>=1.26.0",
        "scipy>=1.11.0",
        "scikit-learn>=1.3.0",
        "networkx>=3.2.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.4.0",
        "requests>=2.31.0",
        "tqdm>=4.66.0",
        "loguru>=0.7.2",
    ],
)
