import { useEffect, useState } from "react";
import { createAlert, getOffers, getProductHistory, type AlertInput } from "./api";
import "./styles.css";

type Offer = {
  id: number;
  product_id: number;
  product_name: string;
  market: string;
  region: string;
  current_price: number;
  valid_until: string;
  is_best_price?: boolean;
  is_new_today?: boolean;
};

type ProductHistory = {
  product_id: number;
  history: Record<string, Array<{ price: number; captured_at: string }>>;
  active_promotions: Offer[];
};

function PriceHistoryChart({ points }: { points: Array<{ price: number; captured_at: string }> }) {
  const max = Math.max(...points.map((p) => p.price));
  const min = Math.min(...points.map((p) => p.price));
  const range = max - min || 1;

  const d = points
    .map((p, i) => {
      const x = (i / Math.max(points.length - 1, 1)) * 280;
      const y = 90 - ((p.price - min) / range) * 70;
      return `${i === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");

  return (
    <svg width="300" height="100" className="chart" aria-label="price history">
      <path d={d} fill="none" stroke="#2b6cb0" strokeWidth="3" />
    </svg>
  );
}

export default function App() {
  const [query, setQuery] = useState("");
  const [market, setMarket] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [region, setRegion] = useState("");
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [history, setHistory] = useState<ProductHistory | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    getOffers({ query, market, max_price: maxPrice || undefined, region: region || undefined }).then(setOffers).catch(() => setOffers([]));
  }, [query, market, maxPrice, region]);

  useEffect(() => {
    if (!selectedProduct) return;
    getProductHistory(selectedProduct).then(setHistory).catch(() => setHistory(null));
  }, [selectedProduct]);

  const handleAlertSubmit = async (payload: AlertInput) => {
    await createAlert(payload);
    setMessage("Alert created successfully.");
  };

  return (
    <main className="page">
      <h1>Smart Shopping Offers</h1>
      <section className="filters">
        <input placeholder="Search product" value={query} onChange={(e) => setQuery(e.target.value)} />
        <input placeholder="Market" value={market} onChange={(e) => setMarket(e.target.value)} />
        <input placeholder="Region" value={region} onChange={(e) => setRegion(e.target.value)} />
        <input placeholder="Max price" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} />
      </section>

      <section className="offer-grid">
        {offers.map((offer) => (
          <article className="offer-card" key={offer.id} onClick={() => setSelectedProduct(offer.product_id)}>
            <h3>{offer.product_name}</h3>
            <p>{offer.market} · {offer.region}</p>
            <p className="price">${offer.current_price.toFixed(2)}</p>
            <p>Valid until: {offer.valid_until}</p>
            <div className="badges">
              {offer.is_new_today && <span className="badge new">New today</span>}
              {offer.is_best_price && <span className="badge best">Best price</span>}
            </div>
          </article>
        ))}
      </section>

      {history && (
        <section className="product-detail">
          <h2>Product #{history.product_id}</h2>
          {Object.entries(history.history).map(([marketName, points]) => (
            <div key={marketName}>
              <h4>{marketName} price history</h4>
              <PriceHistoryChart points={points} />
            </div>
          ))}
          <h3>Active promotions</h3>
          <ul>
            {history.active_promotions.map((p) => (
              <li key={p.id}>{p.market}: ${p.current_price.toFixed(2)} (until {p.valid_until})</li>
            ))}
          </ul>
        </section>
      )}

      <AlertForm onSubmit={handleAlertSubmit} />
      {message && <p className="success">{message}</p>}
    </main>
  );
}

function AlertForm({ onSubmit }: { onSubmit: (payload: AlertInput) => void }) {
  const [productId, setProductId] = useState("101");
  const [threshold, setThreshold] = useState("2.50");
  const [channel, setChannel] = useState<"email" | "push" | "webhook">("email");

  return (
    <section className="alert-form">
      <h2>Create Price Alert</h2>
      <input value={productId} onChange={(e) => setProductId(e.target.value)} placeholder="Product ID" />
      <input value={threshold} onChange={(e) => setThreshold(e.target.value)} placeholder="Price threshold" />
      <select value={channel} onChange={(e) => setChannel(e.target.value as "email" | "push" | "webhook") }>
        <option value="email">Email</option>
        <option value="push">Push</option>
        <option value="webhook">Webhook</option>
      </select>
      <button onClick={() => onSubmit({ product_id: Number(productId), threshold: Number(threshold), channel })}>Create Alert</button>
    </section>
  );
}
