Switch .nvmrc and CI to Node 20, run your tests, and rebuild native modules.

- Native modules like bcrypt, sharp, and node-sass need `npm rebuild`, or delete `node_modules` and reinstall.
- If you skip the rebuild, the app crashes at startup with a NODE_MODULE_VERSION mismatch error.
- If you deploy with containers, change the Docker base image to `node:20`.
