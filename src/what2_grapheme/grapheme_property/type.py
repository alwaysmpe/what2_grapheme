from enum import CONTINUOUS, Enum, verify

import numpy as np


@verify(CONTINUOUS)
class Break(np.uint8, Enum):
    CR = np.uint8(0)
    """Carriage return"""
    LF = np.uint8(1)
    """Line feed"""
    Control = np.uint8(2)
    """Control character"""
    L = np.uint8(3)
    """Conjoining Jamo - Leading consonant"""
    V = np.uint8(4)
    """Conjoining Jamo - Vowel"""
    LV = np.uint8(5)
    """Hangul - precomposed jamo Leading consonant/Vowel sequence"""
    T = np.uint8(6) # type: ignore reportAssignmentIssues
    """Conjoining Jamo - Trailing consonant"""
    LVT = np.uint8(7)
    """Hangul - precomposed jamo Leading consonant/Vowel/Trailing consonant sequence"""
    Prepend = np.uint8(8)
    InCB_Consonant = np.uint8(9)
    Extended_Pictographic = np.uint8(10)
    Regional_Indicator = np.uint8(11)
    Other = np.uint8(12)
    Extend = np.uint8(13)
    SpacingMark = np.uint8(14)
    ZWJ = np.uint8(15)
    """Zero width join"""
    InCB_Linker = np.uint8(16)
    InCB_Extend = np.uint8(17)
