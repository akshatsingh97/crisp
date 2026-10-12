```markdown
## Install and run

logtail needs Node.js 18 or later. To check your version, run `node --version`.

1. Install logtail globally:

   ```sh
   npm install -g logtail
   ```

2. Set your API token. You must set it before you run logtail.

   ```sh
   export LOGTAIL_TOKEN=<your-token>
   ```

3. Run logtail on a log file:

   ```sh
   logtail --follow app.log
   ```

logtail reads the API token from the `LOGTAIL_TOKEN` environment variable. The `--follow` flag is the option for `app.log` in the command above.
```

I do not know what `--follow` does, so I did not describe it. The `export` command works in Bash and Zsh. Add a line for Windows if you support it. If you want a "Get a token" step, send me the steps.
