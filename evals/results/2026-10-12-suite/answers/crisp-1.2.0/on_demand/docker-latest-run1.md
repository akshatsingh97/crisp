No, avoid `:latest` for base images in production.

**Why it causes problems**
- **Unreproducible builds.** The same Dockerfile can produce different images on different days, so a rebuild can break something that worked yesterday.
- **Surprise major upgrades.** `latest` can jump a major version of the OS, language runtime, or libc, which can break your app.
- **Hard rollbacks and debugging.** You can't tell which base image a running container was built from.
- **Security audits.** You can't prove which base layer was deployed.
- **Cache confusion.** Local and CI caches can hold a stale `latest` that differs from the registry's.

**What to use instead**
1. **Pin a specific version.** For example, `node:22.11-bookworm-slim` instead of `node:latest`. This is the minimum.
2. **Pin by digest for strict reproducibility.** For example, `node:22.11-bookworm-slim@sha256:<digest>`. The tag stays for readability, and the digest guarantees the exact image.
3. **Automate updates.** Use Renovate or Dependabot to open PRs that bump the tag or digest. Then you get security patches through review and CI, not by surprise.
4. **Prefer slim or minimal variants** (`-slim`, distroless, Alpine where compatible) to reduce attack surface.

**When `latest` is acceptable**
Local experiments, throwaway dev containers, or CI jobs that deliberately test against the newest upstream.

A good production default is a version tag plus a digest, with a bot keeping it current.
