## Install and run

logtail needs Node.js 18 or later.

1. Check your Node.js version.

   ```sh
   node --version
   ```

   The output must show `v18` or a later version.

2. Install logtail globally.

   ```sh
   npm install -g logtail
   ```

3. Set your API token in the `LOGTAIL_TOKEN` environment variable.

   ```sh
   export LOGTAIL_TOKEN=<your-api-token>
   ```

   Do not commit the token to source control. On Windows, use `set` (Command Prompt) or `$env:LOGTAIL_TOKEN` (PowerShell) instead of `export`.

4. Run logtail with `--follow` on your log file.

   ```sh
   logtail --follow app.log
   ```

logtail reads the token from `LOGTAIL_TOKEN` each time it starts. Set the variable in every new shell session, or add it to your shell profile.

If `logtail` is not found after install, check that the npm global bin directory is in your `PATH`. Run `npm config get prefix` to find it.
