## Install and run

Logtail needs Node.js 18 or later. To check your version, run `node --version`.

1. Install logtail:

   ```
   npm install -g logtail
   ```

2. Set your API token in the `LOGTAIL_TOKEN` environment variable:

   ```
   export LOGTAIL_TOKEN=your-token-here
   ```

   Logtail reads the token from this variable. Set it in every shell where you run logtail.

3. Follow a log file:

   ```
   logtail --follow app.log
   ```

   Logtail keeps the file open and shows new lines as they arrive.
