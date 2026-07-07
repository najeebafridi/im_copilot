interface PagePlaceholderProps {
  title: string;
  description: string;
}

export function PagePlaceholder({ title, description }: PagePlaceholderProps) {
  return (
    <section className="space-y-3">
      <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
      <p className="max-w-2xl text-sm leading-6 text-slate-600">{description}</p>
    </section>
  );
}
