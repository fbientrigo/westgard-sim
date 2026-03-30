type MessageStateProps = {
  title: string;
  description: string;
};

function MessageState({ title, description }: MessageStateProps): JSX.Element {
  return (
    <section className="message-state" role="status">
      <h2>{title}</h2>
      <p>{description}</p>
    </section>
  );
}

export function LoadingState({ description }: { description: string }): JSX.Element {
  return <MessageState title="Cargando" description={description} />;
}

export function ErrorState({
  description,
  onRetry,
}: {
  description: string;
  onRetry?: () => void;
}): JSX.Element {
  return (
    <section className="message-state message-state-error" role="alert">
      <h2>Error de carga</h2>
      <p>{description}</p>
      {onRetry && (
        <button className="button-secondary" onClick={onRetry} type="button">
          Reintentar
        </button>
      )}
    </section>
  );
}

export function EmptyState({ description }: { description: string }): JSX.Element {
  return <MessageState title="Sin datos" description={description} />;
}

export function NotFoundState({ description }: { description: string }): JSX.Element {
  return <MessageState title="No encontrado" description={description} />;
}
