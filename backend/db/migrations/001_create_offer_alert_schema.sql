BEGIN;

CREATE TABLE supermarkets (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    source_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (name, region),
    UNIQUE (source_id)
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    brand TEXT,
    normalized_key TEXT NOT NULL UNIQUE,
    aliases TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE offers (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    supermarket_id BIGINT NOT NULL REFERENCES supermarkets(id) ON DELETE CASCADE,
    normalized_key TEXT NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    unit_price NUMERIC(12, 4),
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT offers_validity_window_chk CHECK (valid_to IS NULL OR valid_to >= valid_from),
    CONSTRAINT offers_price_chk CHECK (price >= 0),
    CONSTRAINT offers_unit_price_chk CHECK (unit_price IS NULL OR unit_price >= 0),
    CONSTRAINT offers_dedup_uk UNIQUE (normalized_key, supermarket_id, valid_from, valid_to, price)
);

CREATE TABLE raw_offer_items (
    id BIGSERIAL PRIMARY KEY,
    offer_id BIGINT REFERENCES offers(id) ON DELETE SET NULL,
    raw_text TEXT NOT NULL,
    parser_confidence NUMERIC(4, 3) NOT NULL,
    extraction_payload JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT raw_offer_items_confidence_chk CHECK (parser_confidence >= 0 AND parser_confidence <= 1)
);

CREATE TABLE alert_rules (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_query TEXT,
    product_id BIGINT REFERENCES products(id) ON DELETE CASCADE,
    target_price NUMERIC(12, 2) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT alert_rules_target_price_chk CHECK (target_price >= 0),
    CONSTRAINT alert_rules_product_selector_chk CHECK (
        (product_id IS NOT NULL AND COALESCE(BTRIM(product_query), '') = '')
        OR (product_id IS NULL AND COALESCE(BTRIM(product_query), '') <> '')
    )
);

CREATE TABLE alert_events (
    id BIGSERIAL PRIMARY KEY,
    alert_rule_id BIGINT NOT NULL REFERENCES alert_rules(id) ON DELETE CASCADE,
    offer_id BIGINT NOT NULL REFERENCES offers(id) ON DELETE CASCADE,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    channel TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_offers_product_validity ON offers (product_id, valid_from, valid_to);
CREATE INDEX ix_offers_supermarket ON offers (supermarket_id);
CREATE INDEX ix_alert_rules_user_active ON alert_rules (user_id, active);
CREATE INDEX ix_alert_events_rule_sent_at ON alert_events (alert_rule_id, sent_at DESC);

CREATE INDEX ix_products_text_search ON products USING GIN (
    to_tsvector('simple', canonical_name || ' ' || COALESCE(array_to_string(aliases, ' '), ''))
);

COMMIT;
