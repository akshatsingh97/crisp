Upgrade to Node 20 by switching the version everywhere, then rebuild native modules.

- Update `.nvmrc`, your CI configuration, and the Docker base image (`node:20`) so every environment uses Node 20, then run the full test suite.
- Pure JavaScript packages usually need no changes.
- Native modules such as bcrypt, sharp, or node-sass need `npm rebuild` (or delete `node_modules` and reinstall), otherwise the app crashes at startup with a `NODE_MODULE_VERSION` mismatch error.
