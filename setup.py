from setuptools import setup, find_packages

setup(
    name="ngrok_service",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyngrok>=5.0.0",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0"
    ],
    author="Caringmind",
    description="A service for handling ngrok tunnel management",
    python_requires=">=3.8",
)
