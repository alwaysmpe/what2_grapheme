from dataclasses import dataclass
from collections.abc import Sequence
from typing import Self
from collections import defaultdict

@dataclass
class FactChain:
    fact_map: dict[str, dict[str, float]]

    @classmethod
    def from_facts(cls, facts: Sequence[tuple[str, float, str]]) -> Self:
        fact_map: defaultdict[str, dict[str, float]] = defaultdict(dict)

        for in_unit, factor, out_unit in facts:
            fact_map[in_unit][out_unit] = factor
            fact_map[out_unit][in_unit] = 1 / factor
        
        changed = True

        while changed:
            changed = False

            for in_unit, conversions in fact_map.items():
                for out_unit, conversion in conversions.items():
                    for chain_unit, chain_conversion in fact_map[out_unit].items():
                        if chain_unit in conversions:
                            continue
                        changed = True
                        conversions[chain_unit] = conversion * chain_conversion

        return cls(fact_map)
    
    def convert(self, value: float, in_unit: str, out_unit: str) -> float | None:
        if out_unit not in self.fact_map[in_unit]:
            return None
        
        return value * self.fact_map[in_unit][out_unit]

def tests():
    
    pass

if __name__ == "__main__":
    tests()