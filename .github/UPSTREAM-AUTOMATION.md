# MAME CURRENT — upstream monitoring and desktop CI

## Scope

This automation tracks the upstream repository `mamedev/mame` and prepares CI artifacts for:

- Windows x64: `mame_libretro.dll`
- Linux x86_64: `mame_libretro.so`

It reuses the fork's `Makefile.libretro`; it does not build the standalone MAME executable.

## Periodic upstream check

Workflow: `.github/workflows/upstream-watch.yml`

- Runs at minute 17 of every hour in `America/Sao_Paulo`.
- Can also be started manually through `workflow_dispatch`.
- Reads `.github/upstream/mame-sync.json`.
- Queries current `mamedev/mame/master` through the GitHub API.
- Uses GitHub's compare endpoint to validate ancestry and count commits after the configured baseline.
- Opens or updates one tracking issue when changes are detected.
- Closes that issue only when the initial integration is marked complete and the recorded baseline is fully synchronized.

The watcher **does not merge upstream code**. Initial integration must be completed and validated first, so the periodic job cannot blindly merge thousands of changes into an unverified Libretro layer.

## Baseline state

The historical reference is `f34f02505e32c1993c6a782b6814232cbfc74e36`, whose commit message identifies MAME 0.289.

At the time this automation was prepared, the initial upstream integration had not been completed. Therefore:

- `initial_sync_complete` remains `false`.
- `last_integrated_upstream_sha` remains `null`.
- The watcher reports the raw number of commits since the historical reference.
- That count is **not** the number of changes still missing from the Libretro fork. The Libretro repository has downstream history and may contain selected upstream changes under different commit identities.

After initial reconciliation, update `mame-sync.json` only with the exact `mamedev/mame` commit whose code was verified as integrated. Then set `initial_sync_complete` to `true`. Never advance this marker merely because a build passed.

## Windows and Linux build jobs

Workflows:

- `.github/workflows/ci-libretro-mingw.yml`
- `.github/workflows/ci-libretro-linux.yml`

They run automatically for relevant code/build-system changes under `src/`, `scripts/`, `3rdparty/` and related build files. Both can also be started manually.

Each build job:

1. Requires the expected Libretro shared library.
2. Checks its architecture (`PE32+ x86-64` on Windows or `ELF 64-bit x86-64` on Linux).
3. Packages the core with `BUILD-INFO.txt` and `SHA256SUMS.txt`.
4. Uploads a GitHub Actions artifact named with the exact fork commit.
5. Retains the artifact for 30 days.

A successful compile and architecture check do not prove that the core has been tested in an actual RetroArch session. The build metadata states this distinction.

## Other platform workflows

Android, iOS and macOS workflows are retained, but changed to manual dispatch only. Automatic CI is focused on the two requested desktop targets.

## Scheduled workflow activation

GitHub scheduled workflows run only from the repository's default branch. The upstream watcher becomes active on its hourly schedule after this automation pull request is merged into `master`. Until then, its code is present for review but the schedule is not active.

## Next integration phase

After the initial MAME-to-Libretro reconciliation, a separate integration workflow can:

1. Create/update a candidate branch from the last verified upstream baseline.
2. Integrate upstream changes while preserving downstream Libretro commits.
3. Stop and report conflicts instead of force-resolving them.
4. Launch Windows x64 and Linux x86_64 builds.
5. Move the last-integrated marker only after the integration outcome is verified.
6. Keep previous successful artifacts available when a candidate fails.
