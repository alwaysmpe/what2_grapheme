from dataclasses import dataclass, field
from what2_time.counter import TimeCounter
from what2_time.timer import BaseTimer
import numpy as np
from collections import defaultdict
# from collections.abc import MutableMapping, Mapping
from collections.abc import Callable
from rich.table import Table
from typing import Any, ClassVar, Final
# import timeit
import gc
from contextlib import ExitStack


@dataclass
class Run:
    times: list[TimeCounter]
    iterations: int

    units: Final[ClassVar[tuple[tuple[int, str], ...]]] = (
        (TimeCounter.nanosecond_base, "ns"),
        (TimeCounter.microsecond_base, "μs"),
        (TimeCounter.millisecond_base, "ms"),
        (TimeCounter.second_base, "s"),
    )

    @property
    def base_choice(self) -> tuple[int, str]:
        return (TimeCounter.second_base, "s")

        # for unit_value, unit_name in self.units:
        #     max_duration = max(
        #         t.as_unit(unit_value)
        #         for t in self.times
        #     )
        #     if (max_duration / self.iterations) <= 1000_000:
        #         return unit_value, unit_name
        # return self.units[-1]

    @property
    def base(self) -> int:
        return self.base_choice[0]

    @property
    def rounds(self) -> int:
        return len(self.times)

    @property
    def unit(self) -> str:
        return self.base_choice[1]

    @property
    def samples(self) -> list[float]:
        base = self.base
        return [
            t.as_unit(base) / self.iterations
            for t in self.times
        ]

    @property
    def mean(self) -> float:
        return float(np.mean(self.samples))

    @property
    def std_dev(self) -> float:
        return float(np.std(self.samples))

    @property
    def min(self) -> float:
        return min(self.samples)

    @property
    def max(self) -> float:
        return max(self.samples)
    @property
    def median(self) -> float:
        return float(np.median(self.samples))



@dataclass
class Group:
    name: str
    short_name: str
    runs: dict[str, Run] = field(default_factory=dict)
    description: str | None = None

    def add_run(self, name: str, run: Run):
        self.runs[name] = run
    
    def get_run(self, name: str):
        return self.runs[name]

    # def to_row(self, run: Run):
    #     return [
    #         f"{run.mean:,.2f}{run.unit}",
    #         f"{run.median:,.2f}{run.unit}",
    #         f"{run.std_dev:,.2f}{run.unit}",
    #         f"{run.min:,.2f}{run.unit}",
    #         f"{run.max:,.2f}{run.unit}",
    #         # f"{run.rounds * run.iterations}",
    #     ]
    def to_row(self, run: Run):
        return [
            f"{run.mean:,.2e}s",
            f"{run.median:,.2e}s",
            f"{run.std_dev:,.2e}s",
            f"{run.min:,.2e}s",
            f"{run.max:,.2e}s",
            # f"{run.rounds * run.iterations}",
        ]

    def to_table(self) -> Table:
        table = Table(
            "Name",
            "Mean",
            "Median",
            "StdDev",
            "Min",
            "Max",
            # "Run Count",
            title=self.name,
            caption=self.description,
            # show_lines=True,
        )

        for name, run in self.runs.items():
            table.add_row(
                name,
                *self.to_row(run),
            )

        return table

type Timer = BaseTimer[Timer]

@dataclass
class Benchmark:
    _group_map: dict[str, Group] = field(default_factory=dict)
    _summary_map: dict[str, Group] = field(default_factory=dict)

    def add_group(self, group: Group):
        self._group_map[group.name] = group

    def add_run(self, group: str, name: str, run: Run | None = None, iterations: int | None = None) -> None:
        if run is None:
            assert iterations is not None
            run = Run(
                [],
                iterations,
            )

        group_data = self._group_map[group]
        group_data.add_run(name, run)

        if name not in self._summary_map:
            self._summary_map[name] = Group(name, short_name="Summary")
        self._summary_map[name].add_run(group_data.short_name, run)

    def table(self, group: str) -> Table:
        return self._group_map[group].to_table()

    def summary(self, name: str) -> Table:
        return self._summary_map[name].to_table()

    def summaries(self) -> list[Table]:
        return [
            self.summary(name)
            for name in sorted(self._summary_map.keys())
        ]

    def tables(self) -> list[Table]:
        return [
            group.to_table()
            for group in self._group_map.values()
        ]

    def bm_fn[**P](
            self,
            fn: Callable[P, Any],
            iterations: int,
            rounds: int,
            /,
            *args: P.args,
            **kwargs: P.kwargs
    ) -> list[TimeCounter]:
        if iterations < 1:
            raise ValueError
        if rounds < 1:
            raise ValueError

        run_times: list[TimeCounter] = []
        for _ in range(rounds):
            timer: Timer = BaseTimer()
            with ExitStack() as ctx:
                if gc.isenabled():
                    ctx.callback(gc.enable)
                    gc.disable()
    
                if iterations > 1:
                    # warmup fn
                    fn(*args, **kwargs)

                    iter_range = range(iterations)
                    timer.start()
                    for _ in iter_range:
                        fn(*args, **kwargs)
                    timer.stop()

                else:
                    timer.start()
                    fn(*args, **kwargs)
                    timer.stop()

            run_times.append(timer.total_time)

        return run_times

    def get_its(self, group: str, name: str) -> int:
        return self._group_map[group].runs[name].iterations

    def extra_runs[**P](
            self,
            group: str,
            name: str,
            rounds: int,
            fn: Callable[P, Any],
            *args: P.args,
            **kwargs: P.kwargs,
    ):
        times = self.bm_fn(
            fn,
            self.get_its(group, name),
            rounds,
            *args,
            **kwargs
        )
        self._group_map[group].runs[name].times.extend(times)


    def run[**P](
            self,
            name: str,
            group: str,
            iterations: int,
            rounds: int,
            fn: Callable[P, Any],
            *args: P.args,
            **kwargs: P.kwargs,
    ):
        run = Run(
            self.bm_fn(
                fn,
                iterations,
                rounds,
                *args,
                **kwargs
            ),
            iterations,
        )
        self.add_run(
            group,
            name,
            run,
        )