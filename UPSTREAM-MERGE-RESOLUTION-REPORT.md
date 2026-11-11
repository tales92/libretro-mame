# MAME upstream integration — resolution report

Date: 2026-11-11

## Source revisions

- Historical common ancestor (MAME 0.289): `f34f02505e32c1993c6a782b6814232cbfc74e36`
- Libretro fork before integration: `e944659076e866b3fa407619487c7be7a9275a26`
- MAME upstream integrated: `8dc81b82f2166f80b4a5fb68a8e71669bae910fc`
- Resulting merge commit: `a7271d8a635259317d31b81cb98ee85c58a70278`
- Resulting tree: `e3d165403b052d9a0ddbe586a0b648e83e733fa1`

## Scope analysis

A recursive Git-tree comparison was performed against the common ancestor. It found 111 paths changed by the Libretro fork: 39 additions, 45 modifications and 27 deletions.

Of those paths, 29 were also changed by upstream:
- 27 files were modified on both sides.
- 2 files were deleted by the fork while upstream had updated them:
  - `3rdparty/lzma/C/7zip_gcc_c.mak`
  - `3rdparty/lzma/C/var_clang_arm64.mak`

The upstream versions of those two LZMA makefiles were retained. The fork's other 25 deletions were applied.

## Three manually reconciled overlapping hunks

1. `scripts/genie.lua`: retained upstream's JCDB configuration handling and incorporated the fork's `libretro` and `libretrodbg` configurations into the normal configuration list.
2. `scripts/src/main.lua`: retained the upstream SDL3 transition while preserving the fork's rule that the Retro/Libretro OSD must not link the SDL desktop dependency. SDL3 is linked in the non-Retro branch.
3. `src/osd/modules/lib/osdobj_common.cpp`: combined upstream's macOS joystick registrations with the fork's SDL joystick conditional and Libretro-specific input registrations.

The remaining 24 files modified on both sides had disjoint change hunks in the line-by-line three-way comparison and were combined from the shared base.

## Preserved Libretro-specific build fix

The fork's `#undef USE_HW_AES` workaround in `3rdparty/lzma/C/AesOpt.c` was retained in the ARM-specific section. The upstream AES/VAES implementation was otherwise incorporated. This workaround does not change the x86-64 AES selection path used by the requested Windows x64 and Linux x86_64 builds.

## Result

The resolved tree was created on top of the upstream tree, with the fork's additions, unique modifications, and resolved shared-file edits applied. The merge commit has both expected parents:
- Libretro fork commit `e944659076e866b3fa407619487c7be7a9275a26`
- Upstream MAME commit `8dc81b82f2166f80b4a5fb68a8e71669bae910fc`

The work is isolated on branch `integration/mame-upstream-resolved-2026-11-11`. The fork's `master` branch was not changed.

## Verification and remaining validation

Content checks confirmed that the resulting commit contains the Libretro makefile and OSD sources, the Libretro GENie configurations, the SDL3/Retro conditional, the macOS and Libretro input registrations, the ARM workaround, and the two restored upstream LZMA makefiles.

The separate GitHub Actions `git merge-tree` audit (run `43079522079`) remained queued when this report was prepared, so its official artifact was not available. This report records the independent tree and line-level comparison used to construct the candidate; it does not claim that the queued workflow completed.

No Windows or Linux compilation was started, and no RetroArch runtime test has been performed. Those checks remain deliberately separate from this conflict-resolution step.


## CI event note (after creating the resolved branch)

The fork's previous CI definitions had unconditional `push` triggers. Publishing the resolved merge candidate and the report therefore created two push-triggered sets of CI runs. At the last status check (2026-11-11 19:02:53 UTC), all listed runs were queued; no completion result was available:

- Windows x64: runs `43083394763` and `43083496611`
- Linux x86_64: runs `43083394771` and `43083496501`
- Android ARM64: runs `43083394783` and `43083496811`
- iOS: runs `43083394780` and `43083496536`
- macOS: runs `43083394778` and `43083496467`

The resolved branch's CI definitions were then updated: Windows and Linux now trigger only for relevant source/build-file paths or manual dispatch; Android, iOS and macOS are manual-dispatch only. This workflow-only update did not create another CI run. The current configuration is intended to avoid future platform-wide runs from documentation-only or workflow-only changes.
