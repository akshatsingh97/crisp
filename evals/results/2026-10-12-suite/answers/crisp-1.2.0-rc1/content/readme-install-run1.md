## Install and run

### Requirements

- Node.js 18 or later. Run `node --version` to check your version.
- A Logtail API token. The CLI reads it from the `LOGTAIL_TOKEN` environment variable.

### Install

1. Install the package globally:

   ```sh
   npm install -g logtail
   ```

2. Check that the install worked:

   ```sh
   logtail --help
   ```

   If the shell says `command not found`, add the npm global bin directory to your `PATH`.

### Run

Set the token before you run the CLI. If `LOGTAIL_TOKEN` is not set, the CLI cannot read your token.

1. Set your token:

   ```sh
   export LOGTAIL_TOKEN=your-token-here
   ```

   This command works in bash and zsh. The variable lasts only for the current shell session.

2. Follow a log file:

   ```sh
   logtail --follow app.log
   ```

The `--follow` flag keeps the command running and reads new lines as they arrive. Press `Ctrl+C` to stop.

Assumption: `--help` is a supported flag. Remove step 2 of the install section if logtail does not support it.
