## Install and run

Logtail needs Node.js 18 or later. To check your version, run `node --version`.

1. Install logtail globally.

   ```sh
   npm install -g logtail
   ```

2. Set your API token. Logtail reads it from the `LOGTAIL_TOKEN` environment variable, so set it before you run the tool.

   ```sh
   export LOGTAIL_TOKEN="your-api-token"
   ```

   This example uses bash or zsh syntax. Use the equivalent command in other shells.

3. Run logtail with the `--follow` option and a log file.

   ```sh
   logtail --follow app.log
   ```
