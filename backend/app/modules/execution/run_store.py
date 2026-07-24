"""ExecutionRunStore — in-memory run buffer (TASK-054 / TASK-055).



No database, queue, or scheduler.
Does not know Complaint, Workflow, or Notification.
"""



from __future__ import annotations



import uuid



from app.modules.execution.runtime_models import ExecutionRun





class ExecutionRunStore:
    """Process-local list of prepared / transitioned execution runs."""



    def __init__(self) -> None:
        self._items: list[ExecutionRun] = []



    def add(self, run: ExecutionRun) -> None:
        if not isinstance(run, ExecutionRun):
            raise TypeError(
                f"run must be ExecutionRun, got {type(run).__name__}"
            )
        self._items.append(run)



    def replace(self, run: ExecutionRun) -> None:
        """Replace an existing run by run_id with a new immutable snapshot."""
        if not isinstance(run, ExecutionRun):
            raise TypeError(
                f"run must be ExecutionRun, got {type(run).__name__}"
            )
        for index, item in enumerate(self._items):
            if item.run_id == run.run_id:
                self._items[index] = run
                return
        raise KeyError(f"ExecutionRun not found: {run.run_id}")



    def put(self, run: ExecutionRun) -> None:
        """Upsert an immutable run snapshot by run_id."""
        if not isinstance(run, ExecutionRun):
            raise TypeError(
                f"run must be ExecutionRun, got {type(run).__name__}"
            )
        for index, item in enumerate(self._items):
            if item.run_id == run.run_id:
                self._items[index] = run
                return
        self._items.append(run)



    def get(self, run_id: uuid.UUID) -> ExecutionRun | None:
        for item in self._items:
            if item.run_id == run_id:
                return item
        return None



    def by_plan_id(self, plan_id: uuid.UUID) -> list[ExecutionRun]:
        return [r for r in self._items if r.plan_id == plan_id]



    def all(self) -> list[ExecutionRun]:
        return list(self._items)



    def clear(self) -> None:
        self._items.clear()



    def __len__(self) -> int:
        return len(self._items)


