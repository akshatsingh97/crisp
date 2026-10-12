```markdown
## Install and run

### Requirements

- Node.js 18 or later

### Install

1. Check your Node.js version.

   ```bash
   node --version
   ```

   The output must show `v18.0.0` or higher.

2. Install logtail globally.

   ```bash
   npm install -g logtail
   ```

### Set your API token

logtail reads your API token from the `LOGTAIL_TOKEN` environment variable. If the variable is not set, logtail cannot authenticate.

1. Set the variable in your shell.

   ```bash
   export LOGTAIL_TOKEN=your-api-token
   ```

   Replace `your-api-token` with your own token.

### Run

1. Start logtail with the `--follow` option and the path to your log file.

   ```bash
   logtail --follow app.log
   ```

   Replace `app.log` with the path to your own log file.
```
