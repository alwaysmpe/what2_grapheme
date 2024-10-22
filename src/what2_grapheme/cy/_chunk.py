import numpy as np
import numpy.typing as npt

from what2_grapheme import cy

import cython

class GStr:
    ord_lookup: npt.NDArray[np.uint8]

    def __init__(self, ord_lookup: npt.NDArray[np.uint8]) -> None:
        self.ord_lookup = ord_lookup

    def length(self, data: str) -> int:
        # print("length start")
        length: cython.int = 0

        state = cy.State_default

        for ch in data:
            # print(f"length: {length}")
            ch_ord: cython.int = ord(ch)
            ord_cat = self.ord_lookup[ch_ord]
            is_break, state = cy.CyStateMachine.next_state(state, ord_cat)
            length += is_break
        
        return int(length)
    
    @staticmethod
    def is_cythed() -> bool:
        return cython.compiled and cy.CyStateMachine.is_cythed()
