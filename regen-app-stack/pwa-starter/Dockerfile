# RegenHub PWA Builder
# Build WASM without installing Rust toolchain locally
#
# Usage:
#   docker build -t regen-pwa-builder .
#   docker run --rm -v $(pwd):/app -p 8080:8080 regen-pwa-builder
#
# Or to just build:
#   docker run --rm -v $(pwd):/app -w /app regen-pwa-builder trunk build

FROM rust:1.77-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev \
    pkg-config \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install wasm32 target and trunk
RUN rustup target add wasm32-unknown-unknown && \
    cargo install trunk

# Install wasm-bindgen-cli for additional tooling
RUN cargo install wasm-bindgen-cli

WORKDIR /app

# Expose dev server port
EXPOSE 8080

# Default: run trunk serve for development
CMD ["trunk", "serve", "--host", "0.0.0.0"]
