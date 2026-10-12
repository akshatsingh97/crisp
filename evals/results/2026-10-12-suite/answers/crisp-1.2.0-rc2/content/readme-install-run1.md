```markdown
## Install and run

### Requirements

- Node.js 18 or later.
- A logtail API token.

### Install

1. Check your Node.js version.

   ```bash
   node --version
   ```

   The output must show v18 or later.

2. Install logtail globally.

   ```bash
   npm install -g logtail
   ```

### Set your token

logtail reads your API token from the `LOGTAIL_TOKEN` environment variable. Set the variable before you run the command.

```bash
export LOGTAIL_TOKEN="your-token-here"
```

This command sets the variable for the current shell session only. To keep it, add the line to your shell profile.

### Run

Run logtail with the `--follow` option and the path to a log file.

```bash
logtail --follow app.log
```

logtail follows `app.log` and shows new lines as they are written.

### Troubleshooting

- If `logtail` is not found, check that the npm global bin folder is in your `PATH`.
- If logtail reports an authentication error, check that `LOGTAIL_TOKEN` is set in the same shell.
```

Assumptions: the `export` command is for bash and zsh. The README does not say where to get a token. The `PATH`, authentication, and "shows new lines" notes are my additions, so check them against the real behavior of logtail.
