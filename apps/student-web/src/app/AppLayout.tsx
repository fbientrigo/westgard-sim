import { Link, Outlet } from "react-router-dom";

export function AppLayout(): JSX.Element {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-inner">
          <Link className="brand-link" to="/">
            Westgard Student Lab
          </Link>
          <p className="brand-subtitle">
            Simulacion de control interno para entrenamiento en reglas de Westgard.
          </p>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
