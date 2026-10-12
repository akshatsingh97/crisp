No, do not use `:latest` in production Dockerfiles.

**Why it is risky**
- `:latest` is a moving tag. It points to a different image each time the maintainer publishes.
- Two builds of the same Dockerfile can give different results. This breaks reproducibility.
- A new major version can arrive without notice. It can break your build or your app at runtime.
- Rollbacks are hard. You cannot tell which base image an old build used.
- `:latest` does not mean "most secure" or "most stable". It only means "the last push without a specific tag".

**What to use instead**
1. Pin a specific version tag, for example `python:3.12.4-slim-bookworm`. Avoid broad tags such as `python:3`.
2. For the strongest guarantee, pin the digest: `FROM python:3.12.4-slim-bookworm@sha256:<digest>`. A digest is immutable, so the image cannot change.
3. Keep the version tag next to the digest. It tells readers what the digest is.

**Keep pinned images patched**
- Pinning stops automatic security fixes. Add a bot such as Renovate or Dependabot to open PRs when a new tag or digest appears.
- Rebuild regularly and scan images with a tool such as Trivy or Grype.

**Exception**
`:latest` is acceptable for local experiments or throwaway test images. Do not use it in anything that you deploy.
