// Talks to the local unraid-api GraphQL endpoint from inside a classic webGUI
// page. Auth is the webGUI's own session cookie (rides along via
// `credentials: "include"`, same-origin) plus the CSRF token DefaultPageLayout.php
// already puts on `window.csrf_token` for every page — see api/src/unraid-api/auth/
// auth.service.ts's validateCookiesWithCsrfToken for why this header is required
// on every non-GET (i.e. every POST, including pure queries) request.
declare global {
  interface Window {
    csrf_token?: string;
  }
}

export class GraphQLError extends Error {
  constructor(
    message: string,
    public readonly errors: unknown[]
  ) {
    super(message);
  }
}

export async function gql<T>(query: string, variables?: Record<string, unknown>): Promise<T> {
  const res = await fetch("/graphql", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "x-csrf-token": window.csrf_token ?? "",
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!res.ok) {
    throw new Error(`GraphQL request failed: HTTP ${res.status}`);
  }

  const body = await res.json();
  if (body.errors?.length) {
    throw new GraphQLError(body.errors[0]?.message ?? "GraphQL error", body.errors);
  }
  return body.data as T;
}
