No, do not use `:latest` for the base image in production Dockerfiles.

**Why it is risky**
- `:latest` is a moving tag. The same Dockerfile can produce different images on different days.
- A rebuild can pull a new major version of the OS, language runtime, or libraries. This can break your app with no change in your code.
- You cannot reproduce or debug an old build, because you cannot tell which base image it used.
- Rollbacks are unreliable. A rebuild of an old commit does not give you the old image.
- A bad or compromised upstream push reaches your production builds without review.
- `:latest` does not always mean the newest or most stable version. The image maintainer decides what it points to.

**What to do instead**
1. Pin a specific version tag, for example `python:3.12.4-slim-bookworm`. Avoid broad tags such as `python:3`.
2. For strict reproducibility, also pin the digest (a content hash that never changes): `FROM python:3.12.4-slim-bookworm@sha256:<digest>`. Get the digest with `docker buildx imagetools inspect <image:tag>`.
3. Automate updates with Renovate or Dependabot. They open pull requests that bump the tag or digest. CI then tests each bump before it reaches production.
4. Rebuild on a schedule to pick up security patches. Pinning a digest stops automatic patches, so the update bot is what keeps you current.

**Exception**
`:latest` is acceptable for quick local experiments or throwaway test images. It is not acceptable for anything that ships.
