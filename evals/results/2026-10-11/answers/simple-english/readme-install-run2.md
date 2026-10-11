Here is the section, ready to paste into your README.

````markdown
## Install and run

logtail needs Node.js 18 or later. To see your version, run `node --version`.

1. Install logtail:

   ```
   npm install -g logtail
   ```

2. Set the LOGTAIL_TOKEN environment variable (a named value that programs read from your shell) to your API token. logtail reads your token from this variable. In bash, run:

   ```
   export LOGTAIL_TOKEN=your-token
   ```

3. Run logtail with the `--follow` flag and the name of your log file:

   ```
   logtail --follow app.log
   ```
````

I did not describe what `--follow` does, because I do not know how your tool behaves. If you tell me, I can add one sentence about it.
