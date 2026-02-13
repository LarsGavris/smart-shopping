from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from queue import Queue
from typing import Iterable

from backend.extract.pipeline import OfferExtractionPipeline, ParsedOffer
from backend.sources.connectors import DateRange, SourceConnector


@dataclass
class IngestionJob:
    connector: SourceConnector
    date_range: DateRange
    retry_count: int = 0


@dataclass
class JobResult:
    market: str
    region: str
    offers: list[ParsedOffer] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class IngestionWorker:
    def __init__(self, max_retries: int = 3) -> None:
        self.max_retries = max_retries
        self.pipeline = OfferExtractionPipeline()

    def process(self, job: IngestionJob) -> JobResult:
        result = JobResult(market=job.connector.market, region=job.connector.region)
        try:
            payloads = job.connector.fetch_raw_offers(job.date_range)
            for payload in payloads:
                result.offers.extend(self.pipeline.run(payload))
        except Exception as exc:  # noqa: BLE001
            result.errors.append(str(exc))
            raise
        return result


class JobQueue:
    def __init__(self, worker: IngestionWorker | None = None) -> None:
        self.worker = worker or IngestionWorker()
        self.queue: Queue[IngestionJob] = Queue()
        self.results: list[JobResult] = []

    def enqueue_daily_jobs(self, connectors: Iterable[SourceConnector], target_date: date | None = None) -> None:
        run_date = target_date or date.today()
        date_range = DateRange(start=run_date, end=run_date + timedelta(days=6))
        for connector in connectors:
            self.queue.put(IngestionJob(connector=connector, date_range=date_range))

    def drain(self) -> list[JobResult]:
        while not self.queue.empty():
            job = self.queue.get()
            try:
                self.results.append(self.worker.process(job))
            except Exception:  # noqa: BLE001
                if job.retry_count < self.worker.max_retries:
                    self.queue.put(
                        IngestionJob(
                            connector=job.connector,
                            date_range=job.date_range,
                            retry_count=job.retry_count + 1,
                        )
                    )
            finally:
                self.queue.task_done()
        return self.results
