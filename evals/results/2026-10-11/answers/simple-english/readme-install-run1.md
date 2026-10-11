Here is the section, ready to paste into your README.

````markdown
## Install and run

logtail needs Node.js 18 or later.

1. Make sure that your Node.js version is 18 or later. To see the version, run `node --version`.
2. Install logtail:

   ```
   npm install -g logtail
   ```

3. Set your API token. logtail reads the token from the `LOGTAIL_TOKEN` environment variable (a named value that programs read from your shell). Replace `your-token` with your API token:

   ```
   export LOGTAIL_TOKEN=your-token
   ```

4. Run logtail on a log file:

   ```
   logtail --follow app.log
   ```

The `--follow` flag keeps logtail open and shows new lines as they are added to `app.log`.
````

I assumed the `--follow` description and the `export` syntax for bash-style shells. If the flag does something different, or if you support Windows, change those lines.
