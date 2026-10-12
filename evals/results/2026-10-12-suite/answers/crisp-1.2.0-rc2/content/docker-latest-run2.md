No, do not use `:latest` for base images in production Dockerfiles.

**Why**
- `:latest` is a moving tag. The image behind it changes when the maintainer pushes a new build.
- Builds are not reproducible. The same Dockerfile can give different results on different days or machines.
- A major version bump can break your app with no change in your repo. Examples are a new OS release, a new language runtime, or a removed package.
- Rollbacks are hard. You cannot tell which base image a past build used.
- Security review is harder. You cannot easily audit which version is in production.
- `:latest` does not always mean newest or most stable. It is only the tag the maintainer chose as default.

**What to use instead**
1. Pin a specific version tag, for example `node:22.11-bookworm-slim` or `python:3.12.7-slim`. This is the minimum.
2. For strict reproducibility, pin the digest: `FROM node:22.11-bookworm-slim@sha256:<digest>`. A digest never changes. A tag can.
3. Keep the tag next to the digest as a comment or in the same line so people can read the version.

**Keep pinned images updated**
- Pinned images do not get security patches on their own. Use Renovate or Dependabot to open pull requests when a new tag or digest appears.
- Rebuild on a regular schedule so OS-level patches reach production.
- Scan images in CI with a tool such as Trivy or Grype.

**Exceptions**
- `:latest` is fine for local experiments and throwaway test containers.
- It is also acceptable in an internal image that your own team controls and versions with care. Even then, an explicit version tag is safer.
