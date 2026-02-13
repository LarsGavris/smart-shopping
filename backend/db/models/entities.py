from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Supermarket(TimestampMixin, Base):
    __tablename__ = "supermarkets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    region: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[str | None] = mapped_column(Text)

    offers: Mapped[list[Offer]] = relationship(back_populates="supermarket")


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    canonical_name: Mapped[str] = mapped_column(Text, nullable=False)
    brand: Mapped[str | None] = mapped_column(Text)
    normalized_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    offers: Mapped[list[Offer]] = relationship(back_populates="product")
    alert_rules: Mapped[list[AlertRule]] = relationship(back_populates="product")


class Offer(TimestampMixin, Base):
    __tablename__ = "offers"
    __table_args__ = (
        UniqueConstraint(
            "normalized_key",
            "supermarket_id",
            "valid_from",
            "valid_to",
            "price",
            name="offers_dedup_uk",
        ),
        CheckConstraint("valid_to IS NULL OR valid_to >= valid_from", name="offers_validity_window_chk"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    supermarket_id: Mapped[int] = mapped_column(
        ForeignKey("supermarkets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    normalized_key: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text)

    product: Mapped[Product] = relationship(back_populates="offers")
    supermarket: Mapped[Supermarket] = relationship(back_populates="offers")
    raw_offer_items: Mapped[list[RawOfferItem]] = relationship(back_populates="offer")
    alert_events: Mapped[list[AlertEvent]] = relationship(back_populates="offer")


class RawOfferItem(Base):
    __tablename__ = "raw_offer_items"
    __table_args__ = (
        CheckConstraint("parser_confidence >= 0 AND parser_confidence <= 1", name="raw_offer_items_confidence_chk"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    offer_id: Mapped[int | None] = mapped_column(ForeignKey("offers.id", ondelete="SET NULL"))
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parser_confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    extraction_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    offer: Mapped[Offer | None] = relationship(back_populates="raw_offer_items")


class AlertRule(TimestampMixin, Base):
    __tablename__ = "alert_rules"
    __table_args__ = (
        CheckConstraint("target_price >= 0", name="alert_rules_target_price_chk"),
        CheckConstraint(
            "((product_id IS NOT NULL AND COALESCE(BTRIM(product_query), '') = '')"
            " OR (product_id IS NULL AND COALESCE(BTRIM(product_query), '') <> ''))",
            name="alert_rules_product_selector_chk",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    product_query: Mapped[str | None] = mapped_column(Text)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    target_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    product: Mapped[Product | None] = relationship(back_populates="alert_rules")
    events: Mapped[list[AlertEvent]] = relationship(back_populates="alert_rule")


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    alert_rule_id: Mapped[int] = mapped_column(
        ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    offer_id: Mapped[int] = mapped_column(ForeignKey("offers.id", ondelete="CASCADE"), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    alert_rule: Mapped[AlertRule] = relationship(back_populates="events")
    offer: Mapped[Offer] = relationship(back_populates="alert_events")
