No, do not use `:latest` for the base image in production Dockerfiles.

The `:latest` tag is a moving pointer. The image publisher can change it at any time, so the same Dockerfile can produce different images on different days.

Reasons:
- Builds are not reproducible. A rebuild can pull a new major version of the OS, language runtime, or libraries.
- Failures are hard to trace. A deploy can break with no change in your code.
- Rollbacks are unsafe. Rebuilding an old commit does not give you the old image.
- Audits are harder. You cannot say which base image a given release used.

Steps:
1. Pin a specific version tag, for example `FROM node:22.11-bookworm-slim`.
2. For stronger safety, pin the digest (the unique hash of the image), for example `FROM node:22.11-bookworm-slim@sha256:<digest>`.
3. Use an automated updater such as Dependabot or Renovate. It will open pull requests when a new base image is available.
4. Run your tests on each update before you merge it.

A pinned image will not receive security patches by itself. You must update the pin on a regular schedule. This is the correct trade-off, because you control when the change happens.
