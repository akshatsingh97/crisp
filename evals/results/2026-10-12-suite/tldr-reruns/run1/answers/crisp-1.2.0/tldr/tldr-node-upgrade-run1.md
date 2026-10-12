Node 16 to 20 is usually a small upgrade, but native modules must be rebuilt after the switch.

- Update the version in `.nvmrc`, CI configuration, and your Docker base image (`node:20`), then run the full test suite.
- Native modules such as bcrypt, sharp, and node-sass must be rebuilt with `npm rebuild`, or by deleting `node_modules` and reinstalling.
- If you skip the rebuild, the app will crash at startup with a `NODE_MODULE_VERSION` mismatch error.
