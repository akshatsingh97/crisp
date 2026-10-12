No. Pin the base image to a specific version, and ideally to a digest, in production Dockerfiles.

**Why `:latest` is risky**
- **Builds are not repeatable.** The same Dockerfile can give different images next week.
- **Surprise breakage.** A major upgrade of the base (OS, language runtime, libc) can arrive with no code change on your side.
- **Hard to debug and roll back.** You can't tell which base a running image was built from.
- **Weaker security review.** You can't audit or scan a known, fixed base.
- **Cache confusion.** Local and CI caches may hold different `latest` images.

**What to do instead**
1. **Pin a version tag.** For example, `python:3.12.4-slim-bookworm` and not `python:latest`.
2. **Pin the digest for strict reproducibility.** For example, `python:3.12.4-slim-bookworm@sha256:<digest>`. The tag stays readable and the digest fixes the exact bytes.
3. **Update on purpose.** Use Dependabot or Renovate to open PRs when a new base version or digest appears. Then CI tests it before it ships.
4. **Prefer small bases.** `-slim`, `distroless`, or `alpine` (check libc compatibility) reduce attack surface.

**One caveat**
A pinned digest does not get security patches by itself. Rebuild on a schedule, or let your bot bump the pin, so you still receive fixes.

`:latest` is fine for quick local experiments, but not for production.
