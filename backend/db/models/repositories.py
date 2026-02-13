from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy import and_, func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload

from .entities import Offer, Product


@dataclass(frozen=True)
class OfferUpsertInput:
    product_id: int
    supermarket_id: int
    normalized_key: str
    price: Decimal
    unit_price: Decimal | None
    valid_from: datetime
    valid_to: datetime | None
    captured_at: datetime
    source_url: str | None


class OfferRepository:
    """Persistence layer for offer ingestion and analytical reads."""

    def __init__(self, session: Session):
        self.session = session

    def upsert_offer(self, payload: OfferUpsertInput) -> Offer:
        """Deduplicate by normalized_key + supermarket + validity_window + price."""
        stmt = (
            insert(Offer)
            .values(
                product_id=payload.product_id,
                supermarket_id=payload.supermarket_id,
                normalized_key=payload.normalized_key,
                price=payload.price,
                unit_price=payload.unit_price,
                valid_from=payload.valid_from,
                valid_to=payload.valid_to,
                captured_at=payload.captured_at,
                source_url=payload.source_url,
            )
            .on_conflict_do_update(
                constraint="offers_dedup_uk",
                set_={
                    "captured_at": payload.captured_at,
                    "unit_price": payload.unit_price,
                    "source_url": payload.source_url,
                    "updated_at": func.now(),
                },
            )
            .returning(Offer)
        )
        return self.session.execute(stmt).scalar_one()

    def get_best_current_offers(
        self,
        now: datetime,
        *,
        product_id: int | None = None,
        normalized_key: str | None = None,
        limit: int = 20,
    ) -> list[Offer]:
        active_window = and_(Offer.valid_from <= now, or_(Offer.valid_to.is_(None), Offer.valid_to >= now))

        ranking = func.row_number().over(
            partition_by=Offer.normalized_key,
            order_by=(Offer.price.asc(), Offer.captured_at.desc()),
        ).label("rank")

        base_query = select(Offer.id, ranking).where(active_window)
        if product_id is not None:
            base_query = base_query.where(Offer.product_id == product_id)
        if normalized_key is not None:
            base_query = base_query.where(Offer.normalized_key == normalized_key)

        ranked_subquery = base_query.subquery()
        query = (
            select(Offer)
            .join(ranked_subquery, ranked_subquery.c.id == Offer.id)
            .where(ranked_subquery.c.rank == 1)
            .order_by(Offer.price.asc(), Offer.captured_at.desc())
            .limit(limit)
            .options(joinedload(Offer.product), joinedload(Offer.supermarket))
        )
        return list(self.session.scalars(query).all())

    def get_price_trend(
        self,
        *,
        normalized_key: str,
        from_dt: datetime,
        to_dt: datetime,
        bucket: str = "day",
    ) -> list[dict[str, object]]:
        bucket_start = func.date_trunc(bucket, Offer.captured_at).label("bucket_start")
        query = (
            select(
                bucket_start,
                func.min(Offer.price).label("min_price"),
                func.max(Offer.price).label("max_price"),
                func.avg(Offer.price).label("avg_price"),
                func.count(Offer.id).label("samples"),
            )
            .where(
                Offer.normalized_key == normalized_key,
                Offer.captured_at >= from_dt,
                Offer.captured_at <= to_dt,
            )
            .group_by(bucket_start)
            .order_by(bucket_start.asc())
        )

        records = self.session.execute(query).all()
        return [
            {
                "bucket_start": row.bucket_start,
                "min_price": row.min_price,
                "max_price": row.max_price,
                "avg_price": row.avg_price,
                "samples": row.samples,
            }
            for row in records
        ]


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def search_by_text(self, query: str, *, limit: int = 20) -> list[Product]:
        ts_query = func.plainto_tsquery("simple", query)
        vector = func.to_tsvector(
            "simple",
            Product.canonical_name + " " + func.coalesce(func.array_to_string(Product.aliases, " "), ""),
        )
        stmt = (
            select(Product)
            .where(vector.op("@@")(ts_query))
            .order_by(func.ts_rank_cd(vector, ts_query).desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())
