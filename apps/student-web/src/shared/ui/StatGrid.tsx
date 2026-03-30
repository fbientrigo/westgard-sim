type StatItem = {
  label: string;
  value: string | number;
};

export function StatGrid({ items }: { items: StatItem[] }): JSX.Element {
  return (
    <dl className="stat-grid">
      {items.map((item) => (
        <div className="stat-card" key={item.label}>
          <dt>{item.label}</dt>
          <dd>{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}
