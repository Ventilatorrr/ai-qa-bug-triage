from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption("--e2e", action="store_true", help="Enable browser test collection.")
    parser.addoption(
        "--e2e-port", type=int, choices=(8148, 8151), default=8151,
        help="8148 for agent runs; 8151 for the user's manual workflow.",
    )


def pytest_ignore_collect(collection_path, config):
    if (
        collection_path == Path(__file__).parent / "tests" / "e2e"
        and not config.getoption("--e2e")
    ):
        return True


def pytest_configure(config):
    if config.getoption("--e2e") and (
        hasattr(config, "workerinput") or config.getoption("numprocesses", default=None)
    ):
        raise pytest.UsageError("E2E tests must run serially against their test server.")
