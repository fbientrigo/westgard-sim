import { AppRouter } from "@/app/router";
import { AuthProvider } from "@/features/auth/AuthProvider";

export function App(): JSX.Element {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}
