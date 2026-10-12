No, do not use `:latest` for the base image in production Dockerfiles. Pin a specific version instead.

**Why it is risky**
- `:latest` is a moving tag. The same Dockerfile can produce a different image next week.
- A major version bump can break your build or runtime with no change in your code.
- Builds are not reproducible. You cannot easily rebuild the exact image that ran last month.
- Rollbacks are harder. You cannot tell which base image a failing deploy used.
- Cached layers can hide the change. One machine builds the old `latest` and another builds the new one.
- `latest` does not mean newest stable for every image. The maintainer decides what it points to.

**Better options, from least to most strict**
1. Pin a version tag, for example `FROM node:22.11-bookworm-slim`. This is the minimum for production.
2. Pin the digest, for example `FROM node:22.11-bookworm-slim@sha256:<digest>`. This fixes the exact image bytes, even if someone retags.
3. Mirror the base image in your own registry. This protects you from upstream tag changes or removal.

**Keep the pin up to date**
- A pinned image does not receive security patches by itself. You must bump it on purpose.
- Use Dependabot or Renovate to open pull requests when a new tag or digest appears.
- Rebuild on a schedule and run an image scanner such as Trivy or Grype in CI.

**Exception**
`:latest` is acceptable for throwaway local experiments or short-lived CI jobs. It is not acceptable in anything that ships.
