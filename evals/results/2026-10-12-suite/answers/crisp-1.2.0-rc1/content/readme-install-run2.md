Here is the section, ready to paste into your README.

````markdown
## Install and run

logtail requires Node.js 18 or later.

### Install

1. Check your Node.js version.

   ```sh
   node --version
   ```

   The version must be 18.0.0 or later. If it is older, upgrade Node.js first.

2. Install logtail globally.

   ```sh
   npm install -g logtail
   ```

### Set your API token

logtail reads your API token from the `LOGTAIL_TOKEN` environment variable. Set it before you run the command.

```sh
export LOGTAIL_TOKEN=your-token-here
```

This setting lasts for the current shell session only. To keep it, add the line to your shell profile.

### Run

Pass a log file and the `--follow` flag.

```sh
logtail --follow app.log
```
````

I did not add any output examples, token sources, or other flags, because you did not give them. I also assumed a POSIX shell for the `export` line. Windows users need a different command, such as `set LOGTAIL_TOKEN=...` in Command Prompt.
