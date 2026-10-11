## Install and run

### Requirements

logtail needs Node.js 18 or later. To check your version, run `node --version`.

### Install

1. Install logtail globally:

   ```sh
   npm install -g logtail
   ```

### Set your API token

logtail reads your API token from the `LOGTAIL_TOKEN` environment variable. You must set the variable before you run logtail.

1. Set the token in your shell:

   ```sh
   export LOGTAIL_TOKEN=your_api_token
   ```

Keep the token out of version control. Do not commit it to a file in your repository.

### Run

1. Follow a log file:

   ```sh
   logtail --follow app.log
   ```

logtail follows `app.log` and keeps reading as the file changes.

The last sentence assumes `--follow` works like `tail -f`. You did not say what it does, so check it against the real behavior.
