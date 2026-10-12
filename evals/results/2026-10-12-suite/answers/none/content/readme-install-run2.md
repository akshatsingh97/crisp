## Install and run

**Requirements:** Node.js 18 or later.

1. Install logtail:

   ```
   npm install -g logtail
   ```

2. Set your API token. logtail reads it from the `LOGTAIL_TOKEN` environment variable:

   ```
   export LOGTAIL_TOKEN=your-token-here
   ```

3. Run logtail on a log file:

   ```
   logtail --follow app.log
   ```

   The `--follow` flag keeps logtail open and shows new lines as they are added to `app.log`.

If `LOGTAIL_TOKEN` is not set, logtail cannot read your token. Set it in the same terminal session before you run the command.
