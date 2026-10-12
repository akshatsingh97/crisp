No. Avoid `:latest` for base images in production.

- **Unreproducible builds:** `:latest` points to a different image over time. The same Dockerfile can build different images on different days, so a rollback or rebuild may not give you what you ran before.
- **Surprise breakage:** A new major version of the OS, language runtime, or libc can land without warning and break your build or runtime.
- **Hard to audit:** You can't tell which base a running image was built from. That makes CVE tracking and incident response harder.
- **Unclear meaning:** `latest` is just the default tag. It isn't guaranteed to be the newest or the most stable.

**What to do instead**
1. Pin to a specific version, such as `python:3.12.7-slim-bookworm` or `node:22.11-alpine3.20`.
2. For stricter reproducibility, pin by digest: `python:3.12.7-slim@sha256:<digest>`. Keep the version tag next to it so people can read it.
3. Let Dependabot or Renovate open PRs to bump the pinned tag or digest. You then get updates and security patches through review and CI, not by surprise.
4. Rebuild on a schedule, so you pick up OS patches within the pinned version.

`:latest` is fine for local experiments or throwaway dev containers.
