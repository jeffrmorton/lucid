# Contributing to Lucid

Thanks for your interest in contributing to Lucid. This guide covers how to get started.

## Development Setup

### Prerequisites

- **Node.js 22+** and **pnpm 9+** (web dashboard, monorepo tooling)
- **Python 3.13+** and **uv** (server, SDK)
- **Rust (stable)** and **wasm-pack** (DSP core)
- **ESP-IDF 5.x** (firmware, only needed for firmware work)
- **KiCad 8** (hardware, only needed for PCB work)

### Getting Started

```bash
git clone https://github.com/jeffrmorton/lucid.git
cd lucid

# Install JavaScript/TypeScript dependencies
pnpm install

# Install Python dependencies
uv sync

# Build DSP core
cd dsp && cargo build && cd ..

# Run all tests
pnpm test              # Web + monorepo
uv run pytest          # Python server + SDK
cd dsp && cargo test   # Rust DSP
```

## Code Style

All code style is enforced by automated tooling. Run checks before submitting:

- **TypeScript/JavaScript**: `pnpm lint` (Biome)
- **Python linting**: `uv run ruff check . && uv run ruff format --check .`
- **Python type checking**: `uv run pyright`
- **Python security**: `uv run bandit -r server/lucid_server/ sdk/python/lucid/`
- **Python dead code**: `uv run vulture server/lucid_server/ sdk/python/lucid/`
- **Rust**: `cargo clippy -- -D warnings && cargo fmt --check`
- **Firmware**: Follow ESP-IDF conventions, Doxygen comments on all functions

## Pull Request Process

1. Fork the repository and create a feature branch from `main`.
2. Write tests for any new functionality. Target 100% coverage.
3. Ensure all CI checks pass: format, lint, pyright, test, bandit security scan, vulture dead code.
4. Write a clear PR description explaining what and why.
5. One approval required for merge.

## Adding Neurofeedback Protocols

Protocol definitions live in `protocols/` as YAML files. Each protocol specifies:

- Target EEG bands and electrode montage
- Reward/inhibit thresholds
- Session timing and structure
- Clinical evidence references

See existing protocols for the expected format.

## Hardware Contributions

- PCB designs are in KiCad 8 format under `hardware/`.
- Include design rationale in commit messages.
- Update `hardware/bom.yaml` if components change.
- All patient-connected circuits must maintain galvanic isolation.

## Safety

Lucid interfaces with the human body. All contributions must respect the safety guidelines in `docs/SAFETY.md`. Galvanic isolation is non-negotiable.

## License

By contributing, you agree that your contributions will be licensed under the MIT License (code) and CERN-OHL-S v2 (hardware).
