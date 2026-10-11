## Install and run

**Requirements:** [Node.js](https://nodejs.org/) 18 or later.

**Install** globally with npm:

```sh
npm install -g logtail
```

**Authenticate** by setting your API token in the `LOGTAIL_TOKEN` environment variable:

```sh
export LOGTAIL_TOKEN="your-api-token"
```

**Run** logtail and follow a log file:

```sh
logtail --follow app.log
```
