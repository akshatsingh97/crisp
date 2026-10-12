Upgrading Node 16 to 20 is usually easy, but native modules must be rebuilt after the switch.

- Update the version in `.nvmrc`, your CI configuration, and the Docker base image (`node:20`), then run your full test suite.
- Pure JavaScript packages usually need no changes.
- Run `npm rebuild` (or delete `node_modules` and reinstall) for native modules such as bcrypt, sharp, or node-sass, or the app will crash at startup with a `NODE_MODULE_VERSION` mismatch.
