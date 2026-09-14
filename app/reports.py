from datetime import datetime, timezone
from pathlib import Path

REPORT_LOG_PATH = Path(__file__).parent / "completion_reports.log"

def write_completion_report(task_id: int, title: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(REPORT_LOG_PATH, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] completion report: task {task_id} ('{title}') marked done.\n")