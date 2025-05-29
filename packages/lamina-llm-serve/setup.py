from setuptools import setup, find_packages

setup(
    name="lamina-llm-serve",
    version="0.1.0",
    description="Centralized model caching and serving layer for Lamina OS",
    packages=find_packages(),
    install_requires=[
        "PyYAML>=6.0",
        "Flask>=2.0.0", 
        "requests>=2.25.0"
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "lamina-llm-server=lamina_llm_serve.server:main",
            "lamina-model-manager=lamina_llm_serve.model_manager_cli:main"
        ]
    }
)