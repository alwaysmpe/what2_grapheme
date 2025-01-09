import pytest
from pytest import StashKey, CollectReport
from _pytest.nodes import Node
from collections.abc import Generator
phase_report_key = StashKey[dict[str, CollectReport]]()


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Generator[None, pytest.CollectReport, pytest.CollectReport]:
    # execute all other hooks to obtain the report object
    rep = yield

    when = rep.when
    assert when is not None
    # store test results for each phase of a call, which can
    # be "setup", "call", "teardown"
    item.stash.setdefault(phase_report_key, {})[when] = rep

    return rep


def did_fail(request: pytest.FixtureRequest) -> bool:
    node: object = getattr(request, "node", None)
    assert isinstance(node, Node)
    report = node.stash[phase_report_key]
    if report["setup"].failed:
        return False
        # print("setting up a test failed or skipped", request.node.nodeid)
    if "call" not in report:
        return False
    return report["call"].failed
