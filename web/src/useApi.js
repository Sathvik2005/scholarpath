import { useCallback, useEffect, useState } from 'react';

// Loads data on mount; `reload` refetches. status: 'loading' | 'ready' | 'error'.
export function useApi(fetcher) {
  const [state, setState] = useState({ status: 'loading', data: null });

  const reload = useCallback(() => {
    fetcher()
      .then((data) => setState({ status: 'ready', data }))
      .catch(() => setState({ status: 'error', data: null }));
  }, [fetcher]);

  useEffect(reload, [reload]);
  return { ...state, reload };
}
