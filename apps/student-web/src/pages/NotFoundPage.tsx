import { Link } from "react-router-dom";
import { NotFoundState } from "@/shared/ui/AsyncStates";

export function NotFoundPage(): JSX.Element {
  return (
    <section className="content-section">
      <NotFoundState description="La ruta solicitada no existe en la aplicacion del estudiante." />
      <Link className="button-primary" to="/">
        Volver al inicio
      </Link>
    </section>
  );
}
