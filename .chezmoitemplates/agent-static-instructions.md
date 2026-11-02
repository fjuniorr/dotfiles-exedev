# Temporary static artifacts

`agent-static.service` serves `/tmp/agent-static` on port **8765**. Use it
for routine previews, reports, and downloads instead of starting per-task
servers. **Port 8000 is reserved for Django**; never stop or replace it to
serve artifacts.

- Normally publish under `/tmp/agent-static/<feature-branch-slug>/`.
  Derive the slug from the current working repository's feature branch:
  lowercase it, replace runs of non-alphanumeric characters (including `/`)
  with `-`, and trim leading/trailing hyphens.
- Reuse that folder for the same feature, with subfolders for multiple
  artifacts. On main/master, detached HEAD, or outside Git, choose a
  descriptive feature slug. Avoid overwriting another feature if slugs collide.
- Local tools use `http://localhost:8765/<slug>/<file>`. User links use
  `https://<vm-name>.exe.xyz:8765/<slug>/<file>` with this VM's public hostname.
  The root URL always lists the folders; a feature folder serves its
  `index.html` when present, otherwise a directory listing.
- Publish only intended static artifacts: no secrets, private source trees,
  symlinks, or CGI scripts. All previews share an origin; this is not a
  sandbox for untrusted HTML/JavaScript.
- Files may disappear on reboot or OS temporary-file cleanup. Do not add
  automatic deletion without an agreed retention policy.

Check the service with `systemctl status agent-static.service`; logs are
available with `journalctl -u agent-static.service`.
