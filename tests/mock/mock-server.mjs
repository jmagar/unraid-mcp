// Schema-faithful mock GraphQL server for offline integration tests.
//
// Serves docs/unraid/UNRAID-SCHEMA.graphql via @graphql-tools/mock
// (addMocksToSchema), so the real Python httpx client exercises a
// schema-accurate endpoint end-to-end without a live Unraid server.
//
//   MOCK_PORT=9002 node mock-server.mjs
//
// Scope: queries + mutations only. The `live` domain uses graphql-transport-ws
// subscriptions over WebSocket, which this HTTP server does NOT mock.

import { readFileSync } from "node:fs";
import { createServer } from "node:http";
import { fileURLToPath } from "node:url";

import { addMocksToSchema } from "@graphql-tools/mock";
import { makeExecutableSchema } from "@graphql-tools/schema";
import { createYoga } from "graphql-yoga";

const SDL_PATH = fileURLToPath(
  new URL("../../docs/unraid/UNRAID-SCHEMA.graphql", import.meta.url),
);
const typeDefs = readFileSync(SDL_PATH, "utf8");
const PORT = Number(process.env.MOCK_PORT ?? 9002);

// Every custom scalar in the SDL needs a mock, or value serialization throws.
// Standard scalars (Int/Float/String/Boolean/ID) use addMocksToSchema defaults.
const mocks = {
  DateTime: () => "2026-01-01T00:00:00.000Z",
  BigInt: () => 1024,
  JSON: () => ({ mock: true }),
  Port: () => 8080,
  URL: () => "https://mock.local",
  PrefixedID: () => "mock:0000000000000000000000000000000000000000000000000000000000000000",
};

const schema = addMocksToSchema({
  schema: makeExecutableSchema({ typeDefs }),
  mocks,
});

const yoga = createYoga({
  schema,
  logging: false,
  graphqlEndpoint: "/graphql",
  // Keep the landing page off so a bare GET to / doesn't 200 with HTML and
  // confuse readiness probes.
  landingPage: false,
});

createServer(yoga).listen(PORT, "127.0.0.1", () => {
  console.log(`[mock] graphql ready on http://127.0.0.1:${PORT}/graphql`);
});
