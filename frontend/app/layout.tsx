import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart Shopping",
  description: "Track offers and create shopping alerts"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header>
          <nav>
            <Link href="/offers">Offers</Link> | <Link href="/alerts">Alerts</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
