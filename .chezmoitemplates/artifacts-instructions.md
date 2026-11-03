# Agent artifacts

For standalone deliverables the user should be able to view, interact with,
or download—reports, visualizations, diagrams, UI mockups, and small demos—
write ordinary files and share a direct browser URL. Use this file-based
workflow instead of Claude Artifacts, chat-embedded HTML/iframe previews,
or similar artifact/canvas tools. The purpose is to make generated output
usable beyond a chat message, with files the user can revisit, edit, and
keep independently of the conversation or agent.

- **Existing engineering plan first.** Check the project's plan conventions
  and find the corresponding plan. For Ficks, read `AGENTS.md` and
  `docs/working-with-claude.md`; plans normally live in the sibling `../plans`
  repo, under `plans/YYYY-MM-DD-<slug>/`. Save related artifacts in that
  existing folder alongside `README.md` (or in an appendix subfolder), link
  them from the plan, and use the plans repo's existing viewer (`just serve`
  in the `plans` tmux session). This is the actual plan folder, not a
  same-named folder under `/tmp`. Follow the plan repo's privacy, metadata,
  and commit/publish conventions; do not create a plan just to host an artifact.
- **No corresponding plan:** publish under
  `/tmp/artifacts/<feature-branch-slug>/`.
  Derive the slug from the current working repository's feature branch:
  lowercase it, replace runs of non-alphanumeric characters (including `/`)
  with `-`, and trim leading/trailing hyphens.
- Reuse that folder for the same feature, with subfolders for multiple
  artifacts. On main/master, detached HEAD, or outside Git, choose a
  descriptive feature slug. Avoid overwriting another feature if slugs collide.

The temporary fallback is served by `artifacts.service` on port **8765**;
do not start per-task servers. **Port 8000 is reserved for Django**; never
stop or replace it to serve artifacts.

- For temporary files, local tools use `http://localhost:8765/<slug>/<file>`. User links use
  `https://<vm-name>.exe.xyz:8765/<slug>/<file>` with this VM's public hostname.
  The root URL always lists the folders; a feature folder serves its
  `index.html` when present, otherwise a directory listing.
- Publish only intended static artifacts: no secrets, private source trees,
  symlinks, or CGI scripts. Previews on each server share an origin; this is not a
  sandbox for untrusted HTML/JavaScript.
- Files under `/tmp` may disappear on reboot or OS temporary-file cleanup. Do not add
  automatic deletion without an agreed retention policy.

Check the service with `systemctl status artifacts.service`; logs are
available with `journalctl -u artifacts.service`.
