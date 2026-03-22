# github-import — Git Handoff

## Branch Plan

| Field | Value |
|-------|-------|
| **Expected branch** | `prj0000020-github-import` |
| **Observed branch** | `prj0000020-github-import` ✅ |
| **Project match** | ✅ confirmed |

## Staged Files

- `src/github_app.py`
- `src/importer/downloader.py`
- `src/importer/config.py`
- `tests/test_github_app.py`
- `tests/test_importer_flow.py`
- `docs/project/prj0000020/` (all 9 doc artifacts)

## Commit Message

```
feat(prj0000020)+docs: github_app event routing + clone_repo + 9 tests + full artifact suite
```

## Handoff Rule
Push to `prj0000020-github-import`. Open PR to `main` only after tests pass on CI.
