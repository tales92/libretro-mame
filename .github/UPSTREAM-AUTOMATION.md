# MAME CURRENT — primary upstream synchronization and desktop CI

## Upstream source

The primary source is **`mamedev/mame`**, branch `master`.

The repository `libretro/mame` is not used as the update source. The fork uses the Libretro integration layer already present in this repository and builds it through `Makefile.libretro`.

## Automatic synchronization

Workflow: `.github/workflows/mame-upstream-sync-build.yml`

- Scheduled every 15 minutes on the default branch.
- Can also be started manually through `workflow_dispatch`.
- Reads `.github/upstream/mame-sync.json`.
- Checks the latest `mamedev/mame/master` commit.
- Verifies that the recorded upstream baseline is the actual Git merge base of the integration branch.
- If new MAME commits exist, creates a candidate by merging upstream into the integration branch.
- Stops on merge conflicts or unexpected history changes; it does not resolve conflicts automatically.

## Verified integration baseline

The initial MAME integration is complete.

- Historical common ancestor: `f34f02505e32c1993c6a782b6814232cbfc74e36` (MAME 0.289).
- Last verified `mamedev/mame` commit included in the integration branch: `8dc81b82f2166f80b4a5fb68a8e71669bae910fc`.
- The GitHub compare endpoint confirmed that exact commit as the merge base between the current upstream and `integration/mame-upstream-resolved-2026-11-11`.
- The exact baseline is stored in `.github/upstream/mame-sync.json`.

Only move the baseline forward as part of a candidate that successfully passes both desktop builds and is promoted to the stable integration branch.

## Build and publication policy

The workflow builds:

- Windows x64: `mame_libretro.dll`
- Linux x86_64: `mame_libretro.so`

Each build uses the candidate branch, verifies the output architecture, writes `BUILD-INFO.txt` and `SHA256SUMS.txt`, then uploads a GitHub Actions artifact with 30-day retention.

The stable branch `integration/mame-upstream-resolved-2026-11-11` is advanced only after **both** Windows x64 and Linux x86_64 builds succeed. If integration or either build fails, the previously validated branch remains unchanged. Build success confirms compilation and architecture, not a live RetroArch runtime test.

## Operational notes

- The temporary candidate branch is `automation/mamedev-mame-candidate`.
- The workflow serializes synchronization attempts to avoid competing updates.
- The MAME upstream commit included in each build is recorded in its artifact metadata and in the synchronization state file.
