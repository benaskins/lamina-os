# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

from setuptools import find_packages, setup

setup(
    name="lamina-llm-serve",
    version="0.1.0",
    description="Centralized model caching and serving layer for Lamina OS",
    packages=find_packages(),
    install_requires=["PyYAML>=6.0", "Flask>=2.0.0", "requests>=2.25.0"],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "lamina-llm-server=lamina_llm_serve.server:main",
            "lamina-model-manager=lamina_llm_serve.model_manager_cli:main",
        ]
    },
)
