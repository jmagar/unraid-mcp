import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

// This package's real @nestjs/*, class-transformer, and class-validator
// dependencies are peerDependencies resolved from the host unraid-api
// monorepo at build/deploy time (see CLAUDE.md) — they aren't installed
// under this package's own node_modules. Source files only use them for
// decorators (@Injectable, @ObjectType, @IsString, etc.) that don't affect
// the pure logic under test here, so tests resolve those imports to tiny
// local no-op stubs instead of requiring the full framework to be vendored.
const stub = (name: string) => fileURLToPath(new URL(`./test-stubs/${name}/index.js`, import.meta.url));

export default defineConfig({
  resolve: {
    alias: {
      "@nestjs/common": stub("@nestjs/common"),
      "@nestjs/config": stub("@nestjs/config"),
      "@nestjs/graphql": stub("@nestjs/graphql"),
      "class-transformer": stub("class-transformer"),
      "class-validator": stub("class-validator"),
    },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
    globals: false,
  },
});
