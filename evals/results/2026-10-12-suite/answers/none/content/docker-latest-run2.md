No, not for production. `:latest` is a moving target, so the same Dockerfile can build different images on different days.

- **Builds aren't reproducible.** A rebuild next week may pull a new major version of the OS, language runtime, or libc. You can't reliably roll back or debug "it worked yesterday."
- **Upgrades are silent.** A breaking change (Python 3.12 to 3.13, Debian bookworm to trixie) lands in an unrelated commit and surfaces as a CI or prod failure.
- **Auditing is harder.** You can't say which base image a given deployment was built from, which matters for CVE response.
- **Caching is misleading.** `latest` on your build host can be stale, while a clean CI runner pulls a newer one, so the two disagree.

**What to do instead:**

1. **Pin a specific version tag**, such as `python:3.12.7-slim-bookworm`. Avoid the bare `python:3`.
2. **Pin by digest for stronger guarantees.** For example, `FROM python:3.12.7-slim-bookworm@sha256:<digest>`. The tag stays for readability and the digest guarantees the exact bytes.
3. **Let a bot bump the pins.** Renovate or Dependabot can open PRs when new base images appear, so you still get security patches, but through review and CI.
4. **Rebuild on a schedule.** Patches reach you deliberately, not accidentally.

**When `:latest` is fine:** local experiments, throwaway dev containers, and quick demos. Even then, a pinned tag is a good habit.
