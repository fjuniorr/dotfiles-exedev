# AWS SSO on exe.dev VMs

When AWS access fails because the SSO session is missing or expired (including
`just db-tunnel` and the `production_*` recipes), log in yourself instead of
asking me to:

```sh
aws sso login --profile ficks --use-device-code --no-browser
```

Keep it running, read the device code it prints, and ask me to approve with
this short link, where `sso_start_url` comes from `~/.aws/config`:

```
<sso_start_url>/#/device?user_code=<DEVICE-CODE>
```

Never show me the long `signin.aws/platform/authorize?request_uri=...` URL the
CLI prints: retyping its opaque token corrupts it. Don't ask me to run a
command to print it, and don't serve it from a port on the VM.

Never approve it yourself. Retry the blocked command once it succeeds. If the
code expires, start a new login and send the new link.
