# AWS SSO on exe.dev VMs

When a task needs AWS access and the SSO session is expired or missing, start
the login yourself rather than asking me to run a command:

```sh
aws sso login --profile ficks --use-device-code --no-browser
```

For a different profile, use the profile required by the task. Show me the
verification URL and device code printed by AWS and ask me to approve the
login in my browser. Leave the login process running while awaiting approval;
do not open the URL or approve it yourself. Once login succeeds, retry the
blocked command. If the device code expires, start a new login and show me
the new URL and code.
