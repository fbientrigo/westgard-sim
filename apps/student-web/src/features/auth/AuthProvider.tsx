import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { Session, User } from "@supabase/supabase-js";
import { getSupabaseClient, isSupabaseConfigured } from "@/shared/supabase/client";

type AuthContextValue = {
  enabled: boolean;
  loading: boolean;
  session: Session | null;
  user: User | null;
  signInWithEmail: (email: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const disabledAuthContext: AuthContextValue = {
  enabled: false,
  loading: false,
  session: null,
  user: null,
  signInWithEmail: async () => undefined,
  signOut: async () => undefined,
};

const AuthContext = createContext<AuthContextValue>(disabledAuthContext);

function authRedirectUrl(): string | undefined {
  if (typeof window === "undefined") {
    return undefined;
  }
  return `${window.location.origin}${window.location.pathname}`;
}

async function upsertProfile(session: Session | null): Promise<void> {
  const client = getSupabaseClient();
  if (!client || !session?.user) {
    return;
  }

  const { error } = await client.from("westgard_profiles").upsert(
    {
      email: session.user.email ?? null,
      id: session.user.id,
      updated_at: new Date().toISOString(),
    },
    { onConflict: "id" },
  );

  if (error) {
    console.warn("No se pudo sincronizar el perfil de Supabase.", error.message);
  }
}

export function AuthProvider({ children }: { children: ReactNode }): JSX.Element {
  const enabled = isSupabaseConfigured();
  const [loading, setLoading] = useState(enabled);
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    const client = getSupabaseClient();
    if (!client) {
      setLoading(false);
      setSession(null);
      return undefined;
    }

    let active = true;
    void client.auth.getSession().then(({ data }) => {
      if (!active) {
        return;
      }
      setSession(data.session);
      setLoading(false);
      void upsertProfile(data.session);
    });

    const {
      data: { subscription },
    } = client.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      setLoading(false);
      void upsertProfile(nextSession);
    });

    return () => {
      active = false;
      subscription.unsubscribe();
    };
  }, []);

  const signInWithEmail = useCallback(async (email: string) => {
    const client = getSupabaseClient();
    if (!client) {
      return;
    }

    const { error } = await client.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: authRedirectUrl(),
      },
    });

    if (error) {
      throw error;
    }
  }, []);

  const signOut = useCallback(async () => {
    const client = getSupabaseClient();
    if (!client) {
      return;
    }

    const { error } = await client.auth.signOut();
    if (error) {
      throw error;
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      enabled,
      loading,
      session,
      signInWithEmail,
      signOut,
      user: session?.user ?? null,
    }),
    [enabled, loading, session, signInWithEmail, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  return useContext(AuthContext);
}
