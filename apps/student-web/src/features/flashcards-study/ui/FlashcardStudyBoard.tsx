import { useEffect, useState } from "react";
import {
  applyStudyRating,
  getDueCardIds,
  getNextDueAt,
  getPileSummaries,
  normalizeStudyProgress,
  type StudyProgress,
} from "@/features/flashcards-study/model/session";
import type { FlashcardStudyDeck } from "@/shared/types/flashcards";

const STORAGE_PREFIX = "westgard.flashcards.progress";

function storageKey(deckId: string): string {
  return `${STORAGE_PREFIX}.${deckId}`;
}

function readProgress(deckId: string): StudyProgress | null {
  if (typeof window === "undefined") {
    return null;
  }
  const raw = window.localStorage.getItem(storageKey(deckId));
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as StudyProgress;
  } catch {
    return null;
  }
}

function formatDueDate(value: string | null): string {
  if (!value) {
    return "Sin proxima revision.";
  }
  return new Date(value).toLocaleString("es-CL", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function FlashcardStudyBoard({ deck }: { deck: FlashcardStudyDeck }): JSX.Element {
  const [progress, setProgress] = useState<StudyProgress>(() =>
    normalizeStudyProgress(deck, readProgress(deck.deck_id), new Date().toISOString()),
  );
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    window.localStorage.setItem(storageKey(deck.deck_id), JSON.stringify(progress));
  }, [deck.deck_id, progress]);

  useEffect(() => {
    setProgress(normalizeStudyProgress(deck, readProgress(deck.deck_id), new Date().toISOString()));
    setRevealed(false);
  }, [deck]);

  const nowIso = new Date().toISOString();
  const dueCardIds = getDueCardIds(deck, progress, nowIso);
  const activeCard = deck.cards.find((card) => card.id === dueCardIds[0]) ?? null;
  const activeProgress = activeCard ? progress.cards[activeCard.id] : null;
  const pileSummaries = getPileSummaries(progress);
  const reviewedCount = Object.values(progress.cards).filter((card) => card.seen_count > 0).length;

  function handleRating(rating: "again" | "good") {
    if (!activeCard) {
      return;
    }
    setProgress((current) =>
      applyStudyRating(current, activeCard.id, rating, new Date().toISOString()),
    );
    setRevealed(false);
  }

  function handleReset() {
    const next = normalizeStudyProgress(deck, null, new Date().toISOString());
    window.localStorage.removeItem(storageKey(deck.deck_id));
    setProgress(next);
    setRevealed(false);
  }

  return (
    <div className="flashcards-layout">
      <section className="content-section flashcards-hero">
        <div className="section-header">
          <p className="flashcards-eyebrow">Estudio activo</p>
          <h2>{deck.metadata.title}</h2>
          <p>{deck.metadata.description}</p>
        </div>
        <div className="card-grid flashcards-meta-grid">
          <article className="info-card">
            <h3>Estado de sesion</h3>
            <p>{reviewedCount} tarjetas vistas en este navegador.</p>
            <p>{dueCardIds.length} tarjetas disponibles ahora.</p>
          </article>
          <article className="info-card">
            <h3>Regla del MVP</h3>
            <p>Usa dos decisiones: <strong>Repetir</strong> y <strong>La supe</strong>.</p>
            <p>
              Se inspira en Anki y Leitner: las tarjetas correctas avanzan una pila; los errores
              vuelven a la pila 1.
            </p>
          </article>
          <article className="info-card">
            <h3>Proximo repaso</h3>
            <p>{formatDueDate(getNextDueAt(progress))}</p>
            <button className="button-secondary" onClick={handleReset} type="button">
              Reiniciar progreso local
            </button>
          </article>
        </div>
      </section>

      <section className="content-section">
        <h2>Tres pilas</h2>
        <div className="card-grid flashcards-pile-grid">
          {pileSummaries.map((pile) => (
            <article className="info-card flashcards-pile-card" key={pile.pile}>
              <h3>{pile.title}</h3>
              <p>{pile.description}</p>
              <strong>{pile.count} tarjetas</strong>
            </article>
          ))}
        </div>
      </section>

      <section className="content-section">
        <div className="section-header">
          <h2>Sesion de tarjetas</h2>
          <p>
            Muestra el anverso, piensa la respuesta y luego decide si debes repetirla o si ya la
            supiste.
          </p>
        </div>

        {!activeCard && (
          <article className="message-state">
            <h3>No hay tarjetas pendientes ahora</h3>
            <p>
              Ya no quedan tarjetas con revision inmediata. Puedes volver mas tarde o reiniciar el
              progreso local para repetir la sesion.
            </p>
          </article>
        )}

        {activeCard && (
          <article className="flashcard-study-card">
            <header className="flashcard-study-header">
              <div>
                <p className="flashcards-eyebrow">
                  {activeCard.card_type_label} · {activeCard.id}
                </p>
                <h3>Tarjeta actual</h3>
              </div>
              <div className="tag-list flashcards-inline-tags">
                {activeCard.display_tags.map((tag) => (
                  <span className="tag" key={tag}>
                    {tag}
                  </span>
                ))}
              </div>
            </header>

            <section className="flashcard-study-face">
              <h4>Anverso</h4>
              <div dangerouslySetInnerHTML={{ __html: activeCard.front_html }} />
            </section>

            {revealed && (
              <section className="flashcard-study-face flashcard-study-answer">
                <h4>Reverso</h4>
                <div dangerouslySetInnerHTML={{ __html: activeCard.back_html }} />
              </section>
            )}

            <footer className="flashcard-study-actions">
              {!revealed && (
                <button className="button-primary" onClick={() => setRevealed(true)} type="button">
                  Mostrar respuesta
                </button>
              )}

              {revealed && (
                <>
                  <button className="button-secondary" onClick={() => handleRating("again")} type="button">
                    Repetir
                  </button>
                  <button className="button-primary" onClick={() => handleRating("good")} type="button">
                    La supe
                  </button>
                </>
              )}
            </footer>

            {activeProgress && (
              <p className="soft-text flashcard-study-meta">
                Pila actual: {activeProgress.pile} · Vista {activeProgress.seen_count} veces ·
                Aciertos {activeProgress.success_count}
              </p>
            )}
          </article>
        )}
      </section>
    </div>
  );
}
