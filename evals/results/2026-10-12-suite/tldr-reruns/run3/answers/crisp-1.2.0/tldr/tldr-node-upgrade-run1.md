Upgrade to Node 20 by switching the version everywhere, then rebuild native modules, or the app will crash at startup.

- Update the version in `.nvmrc` and your CI configuration, then run the full test suite.
- Run `npm rebuild`, or delete `node_modules` and reinstall, because bcrypt, sharp, and node-sass compile against a specific Node ABI.
- Without the rebuild, the app crashes at startup with a `NODE_MODULE_VERSION` mismatch error, and Docker deployments also need the base image set to `node:20`.
