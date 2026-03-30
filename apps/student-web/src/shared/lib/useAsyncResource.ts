import { useEffect, useRef, useState } from "react";

type AsyncState<TData> = {
  data: TData | null;
  error: string | null;
  isLoading: boolean;
};

type AsyncResource<TData> = AsyncState<TData> & {
  reload: () => void;
};

export function useAsyncResource<TData>(
  loadData: () => Promise<TData>,
  dependencies: ReadonlyArray<unknown>,
): AsyncResource<TData> {
  const [nonce, setNonce] = useState(0);
  const [state, setState] = useState<AsyncState<TData>>({
    data: null,
    error: null,
    isLoading: true,
  });
  const loadRef = useRef(loadData);
  loadRef.current = loadData;

  useEffect(() => {
    let isCancelled = false;
    setState((previous) => ({ ...previous, isLoading: true, error: null }));

    loadRef
      .current()
      .then((data) => {
        if (isCancelled) {
          return;
        }
        setState({ data, error: null, isLoading: false });
      })
      .catch((error: unknown) => {
        if (isCancelled) {
          return;
        }
        const message =
          error instanceof Error ? error.message : "Ocurrio un error inesperado.";
        setState({ data: null, error: message, isLoading: false });
      });

    return () => {
      isCancelled = true;
    };
  }, [...dependencies, nonce]);

  return {
    ...state,
    reload: () => setNonce((value) => value + 1),
  };
}
