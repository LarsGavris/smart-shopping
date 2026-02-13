from __future__ import annotations

from datetime import date
from typing import Iterable

from backend.sources.connectors import SourceConnector
from backend.workers.jobs import JobQueue


class DailyIngestionScheduler:
    """Queue-driven entry point for daily supermarket ingestion."""

    def __init__(self, queue: JobQueue | None = None) -> None:
        self.queue = queue or JobQueue()

    def run_daily(self, connectors: Iterable[SourceConnector], target_date: date | None = None):
        self.queue.enqueue_daily_jobs(connectors=connectors, target_date=target_date)
        return self.queue.drain()
