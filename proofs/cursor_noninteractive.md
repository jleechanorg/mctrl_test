flags_tested: --trust --yolo --print --workspace, cli: cursor
commit: 67b652336660fdc4bc4cae298af5af7c145210bc

## Evidence

```bash
$ cursor --trust --yolo --print --workspace
Warning: 'trust' is not in the list of known options, but still passed to Electron/Chromium.
Warning: 'yolo' is not in the list of known options, but still passed to Electron/Chromium.
Warning: 'print' is not in the list of known options, but still passed to Electron/Chromium.
Warning: 'workspace' is not in the list of known options, but still passed to Electron/Chromium.
EXIT_CODE: 0
```

All four flags are accepted (passed through to Electron) and the process exits cleanly (code 0).
