Upgrading from Node 16 to Node 20 mostly needs a version bump, but native modules must be rebuilt first.

- Update the version in `.nvmrc` and your CI configuration, then run the full test suite.
- Run `npm rebuild` (or delete `node_modules` and reinstall) after switching, or native modules such as bcrypt, sharp, and node-sass will crash at startup with a `NODE_MODULE_VERSION` mismatch error.
- If you deploy with containers, update the Docker base image to `node:20`.
