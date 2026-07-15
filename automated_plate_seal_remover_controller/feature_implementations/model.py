# -*- coding: utf_8 -*-
"""The module of the model classes."""

from enum import Enum

"""The status of the instrument. These values are common to all instruments."""
class Status(Enum):
    NotConnected = 0
    Idle = 1
    Running = 2
    Error = 3
