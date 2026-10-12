Upgrade from Node 16 to Node 20 by updating version files, then rebuild native modules if you have any.

- Update the version in `.nvmrc` and your CI configuration, then run the full test suite.
- Run `npm rebuild` or reinstall `node_modules`, otherwise native modules like bcrypt, sharp, or node-sass crash at startup with NODE_MODULE_VERSION mismatch.
- If you deploy with containers, update your Docker base image to `node:20`.
