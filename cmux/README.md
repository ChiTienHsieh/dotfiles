# cmux config profiles

This directory tracks cmux config profiles for `~/.config/cmux/cmux.json`.

- `cmux.default.jsonc`: the cmux-generated default template, kept for rollback and reference.
- `cmux.performance.jsonc`: the installed profile, tuned for smoother multi-agent use in cmux.

`install.sh` links `cmux.performance.jsonc` to `~/.config/cmux/cmux.json`.

To switch profiles manually:

```bash
ln -sf ~/dotfiles/cmux/cmux.performance.jsonc ~/.config/cmux/cmux.json
cmux reload-config
```

To revert to the default template:

```bash
ln -sf ~/dotfiles/cmux/cmux.default.jsonc ~/.config/cmux/cmux.json
cmux reload-config
```

The performance profile reduces automatic agent restore, hibernates idle background agents, hides high-churn sidebar details, and discards hidden browser webviews after a short delay.
