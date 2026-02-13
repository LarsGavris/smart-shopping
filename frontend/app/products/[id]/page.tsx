type ProductPageProps = {
  params: {
    id: string;
  };
};

export default function ProductPage({ params }: ProductPageProps) {
  return (
    <section>
      <h1>Product {params.id}</h1>
      <p>Detailed price history and matched offers.</p>
    </section>
  );
}
