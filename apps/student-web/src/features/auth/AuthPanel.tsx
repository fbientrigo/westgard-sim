import { useState, type FormEvent } from "react";
import { useAuth } from "@/features/auth/AuthProvider";

export function AuthPanel(): JSX.Element {
  const { enabled, loading, user, signInWithEmail, signOut } = useAuth();
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSignIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    setError(null);
    setSubmitting(true);
    try {
      await signInWithEmail(email);
      setMessage("Revisa tu correo para abrir la sesion.");
      setEmail("");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "No se pudo enviar el enlace.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSignOut() {
    setMessage(null);
    setError(null);
    setSubmitting(true);
    try {
      await signOut();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "No se pudo cerrar la sesion.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!enabled) {
    return <p className="auth-status">Modo local: progreso guardado en este navegador.</p>;
  }

  if (loading) {
    return <p className="auth-status">Cargando sesion...</p>;
  }

  if (user) {
    return (
      <div className="auth-panel">
        <p className="auth-status">Sesion: {user.email ?? "usuario autenticado"}</p>
        <button className="button-secondary" disabled={submitting} onClick={handleSignOut} type="button">
          Cerrar sesion
        </button>
        {error && <p className="auth-error">{error}</p>}
      </div>
    );
  }

  return (
    <form className="auth-panel" onSubmit={handleSignIn}>
      <label className="auth-label">
        Guardar progreso en Supabase
        <input
          className="auth-input"
          onChange={(event) => setEmail(event.target.value)}
          placeholder="correo@ejemplo.cl"
          required
          type="email"
          value={email}
        />
      </label>
      <button className="button-secondary" disabled={submitting} type="submit">
        Enviar enlace
      </button>
      {message && <p className="auth-status">{message}</p>}
      {error && <p className="auth-error">{error}</p>}
    </form>
  );
}
