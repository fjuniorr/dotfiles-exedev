# AWS SSO on exe.dev VMs

When AWS access fails because the SSO session is missing or expired (including
`just db-tunnel` and the `production_*` recipes), log in yourself instead of
asking me to:

```sh
aws sso login --profile ficks --use-device-code --no-browser
```

Keep it running, show me the URL and code it prints, and ask me to approve.
Never approve it yourself. Retry the blocked command once it succeeds.
