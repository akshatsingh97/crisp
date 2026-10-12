No, not for production. Pin the base image instead.

- **Builds aren't reproducible.** `:latest` points at a different image over time, so the same Dockerfile can produce different results next week. You can't reliably roll back or debug "it worked yesterday."
- **Upgrades land unannounced.** A major version bump of the OS, language runtime, or libc can arrive on your next build and break things.
- **`:latest` doesn't mean newest or safest.** It's just the default tag the maintainer chose. It can lag behind or point to an unexpected variant.
- **Caching is unpredictable.** Hosts and CI may reuse a stale local `:latest`, so different machines end up with different bases.

**What to do instead, strongest first:**
1. **Pin by digest:** `FROM node:22.11.0-alpine3.20@sha256:<digest>`. This is fully immutable.
2. **Pin an exact version tag:** `FROM node:22.11.0-alpine3.20`. This is readable, but tags can technically be re-pushed.
3. **Pin a minor series** (e.g. `node:22-alpine`) only if you accept patch updates without notice.

**Keeping pinned images patched:** let Renovate or Dependabot open PRs that bump the tag or digest. Your CI then tests each bump before it reaches production, so you get updates without surprises. Scan images with Trivy or Grype as well.

`:latest` is fine for throwaway local experiments and quick demos. It shouldn't be in anything that ships.
