---
type: "Reference"
title: "Operations"
openwiki_generated: true
---

---
type: "Reference"
title: "Operations"
description: "Operational guidance for building, running, configuring, deploying, and testing the unraid-rmcp repository."

# Operations

How to deploy, configure, test, and develop unrust.

## Pages in this section

- **[Configuration](configuration.md)** - Environment variables, config files, and data directories
- **[Deployment](deployment.md)** - Local installation, Docker, and production deployment
- **[Testing](testing.md)** - Test suite organization and running tests
- **[Development workflow](development.md)** - Adding actions, code style, release process, and OpenWiki automation

## Quick reference

**Run locally:**
```bash
cargo run -- serve mcp
```

**Run tests:**
```bash
cargo test
# or
just test
```

**Format code:**
```bash
cargo fmt
# or
just fmt
```

**Check lints:**
```bash
cargo clippy --all-targets --features test-support
# or
just clippy
```

**Build release:**
```bash
cargo build --release
# Binary at target/release/runraid
```

**Install via one-liner:**
```bash
curl -fsSL https://raw.githubusercontent.com/jmagar/runraid/main/install.sh | bash
```

See individual pages for detailed guidance.
