## Install and run

**Requirements:** Node.js 18 or later.

**Install** globally with npm:

```bash
npm install -g logtail
```

**Authenticate** by setting your API token in the `LOGTAIL_TOKEN` environment variable:

```bash
export LOGTAIL_TOKEN=your-api-token
```

**Run** logtail on a log file. `--follow` keeps it streaming new lines as they're written:

```bash
logtail --follow app.log
```
