## Install and run

logtail needs Node.js 18 or later. Check your version with `node --version`.

### Install

Install logtail globally:

```bash
npm install -g logtail
```

### Set your API token

logtail reads your API token from the `LOGTAIL_TOKEN` environment variable. Set the variable before you run logtail.

```bash
export LOGTAIL_TOKEN="your-api-token"
```

### Run

Follow a log file:

```bash
logtail --follow app.log
```

The `--follow` flag follows `app.log` as it changes.

I used `export` for bash and zsh. If your README covers Windows, add the matching command for that shell.
