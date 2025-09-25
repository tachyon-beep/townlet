import time

from townlet.console.handlers import ConsoleCommand
from townlet_ui.commands import ConsoleCommandExecutor


class DummyRouter:
    def __init__(self) -> None:
        self.dispatched: list[ConsoleCommand] = []

    def dispatch(self, command: ConsoleCommand) -> None:
        self.dispatched.append(command)
        time.sleep(0.01)


def test_console_command_executor_dispatches_async() -> None:
    router = DummyRouter()
    executor = ConsoleCommandExecutor(router)

    command = ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={})
    executor.submit(command)
    executor.shutdown()
    assert router.dispatched == [command]


def test_console_command_executor_swallow_errors() -> None:
    class FailingRouter(DummyRouter):
        def dispatch(self, command: ConsoleCommand) -> None:
            raise RuntimeError("boom")

    executor = ConsoleCommandExecutor(FailingRouter())
    executor.submit(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={}))
    executor.shutdown()
