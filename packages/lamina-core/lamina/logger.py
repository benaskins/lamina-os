# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

import warnings

from lamina.logging_config import get_logger as new_get_logger

# Deprecation warning
warnings.warn(
    "lamina.logger is deprecated. Use lamina.logging_config.get_logger instead.",
    DeprecationWarning,
    stacklevel=2,
)


def get_logger(name: str):
    """
    DEPRECATED: Use lamina.logging_config.get_logger instead.

    This function is kept for backward compatibility but will be removed
    in a future version.
    """
    warnings.warn(
        "lamina.logger.get_logger is deprecated. Use lamina.logging_config.get_logger instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return new_get_logger(name)
