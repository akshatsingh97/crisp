````markdown
## Install and run

logtail needs Node.js 18 or later.

1. Check your Node.js version.

   ```bash
   node --version
   ```

   The output must show v18 or higher.

2. Install logtail.

   ```bash
   npm install -g logtail
   ```

3. Set your API token in the `LOGTAIL_TOKEN` environment variable.

   ```bash
   export LOGTAIL_TOKEN=<your-token>
   ```

4. Run logtail on your log file.

   ```bash
   logtail --follow app.log
   ```

logtail reads the API token from `LOGTAIL_TOKEN` only. Set the variable in the same shell session where you run the command.
````

The `export` syntax in step 3 works in bash and zsh. Other shells, such as Windows PowerShell, use different syntax.
