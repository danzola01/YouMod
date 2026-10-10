# Personal YouMod build

## Current state

- Code fork: https://github.com/danzola01/YouMod
- Personal/default branch: `sidestore`; upstream branch: `Tonwalter888/YouMod/main`.
- Initial upstream commit: `fb6a9f6f3bbfcbe8aa8b92debda6405f2b7be2d7`.
- Base IPA: `com.google.ios.youtube-21.40.5-Decrypted.ipa` in the project root.
- Inspection: `base-ipa.json` records integrity, version, minimum OS, hash and
  encryption metadata. All seven detected Mach-O executables have `cryptid: 0`.
  No dylibs, provisioning profiles, or obvious YouMod/YouPiP resources were found.
  Metadata checks do not establish the binary's provenance or device behavior.
- Target reported by user: iPhone 17, iOS 27.0. Base IPA requires iOS 17.0.
- Upload destination: user selected an unpublished draft release in the fork.
  Base release tag: `base-youtube-21.40.5`. Uploaded and remote asset digest
  verified against the local SHA-256.
- First build succeeded: https://github.com/danzola01/YouMod/actions/runs/38014046024
  (source/workflow commit `0411203b7a3c0d4d943a239d44d419602d3cff36`).
- Output draft tag: `youmod-ipa1`; owner-only release page:
  https://github.com/danzola01/YouMod/releases/tag/untagged-627361f5fe57922d5159
- Final IPA: `output/YouMod_21.40.5_v2.0.0.ipa` (129,310,334 bytes).
  SHA-256: `7410bafa51cda6c7b1f62e1f8f70bd6128ebdba7913876548825cbdf7525f2ba`.
  `built-ipa.json` records successful integrity/hash/encryption checks and the
  injected load commands for YouMod, YouPiP, YouGroupSettings, YTVideoOverlay and
  UncappedAVPlayer. Only the injected Safari app extension remains.
- Anonymous asset API requests returned 404 for both the base and final IPA;
  authenticated owner access works. Both releases were verified as drafts.
- User confirmed SideStore is installed and refresh works on the target phone.
  YouMod installation and on-device feature checks remain pending.

## Build choices

`config/sidestore-inputs.json` contains the personal build inputs. Use the fork's
source on `sidestore`, enable YouPiP, and disable the optional companion tweaks
for the initial build. YouMod includes SponsorBlock, downloads, ad blocking, and
background playback. The workflow also injects its mandatory dependencies and
the upstream Safari extension. Preserve these unless a build/device issue
requires a targeted change.

App name is `YouMod` and bundle ID is `com.danzola.youmod`, allowing a separate
installation alongside the App Store YouTube app. Keep this bundle ID and the
SideStore signing account stable when installing updates.

## Inspect a base IPA

Run before uploading a replacement:

```bash
python3 scripts/inspect_ipa.py path/to/base.ipa --require-decrypted --output output/base-ipa.json
```

Inspect the version, bundle ID, minimum OS, encryption records and dylibs. The
inspector reads archive content without executing or extracting the app. Reuse
the saved base IPA for tweak updates while that YouTube version remains supported.
Changing the YouTube version requires another decrypted base IPA and build.

## Build and retrieve

The base IPA lives in draft release `base-youtube-21.40.5`. The workflow checks
that the release is unpublished and uses its own `GITHUB_TOKEN` to download it
with authenticated `gh release download`. No public download link or extra
storage credentials are required. The upstream draft-cleanup workflow is disabled
in this fork to preserve the base; manage old output drafts individually.

Dispatch the personal workflow using the saved inputs:

```bash
bash scripts/build_ipa.sh
gh run list --repo danzola01/YouMod --workflow ipa.yml --branch sidestore
```

The hosted macOS runner builds and injects the tweaks; no local Mac is required.
For a new base version, inspect it, create another unpublished `base-youtube-*`
release, and update `ipa_release` and `ipa_sha256` in the saved inputs. External
URL downloads remain supported by setting `ipa_release` empty; keep credentials
and signed URLs out of tracked files.

Confirm the workflow succeeds and the output release remains a draft. Download
with authenticated GitHub access, then inspect the resulting IPA for YouMod and
YouPiP dylibs, the expected app identity, and encryption metadata. Record the run
URL, source commit, draft tag and output hash here. Never publish a release
containing the proprietary IPA.

Retrieve the first successful build locally:

```bash
gh release download youmod-ipa1 --repo danzola01/YouMod --pattern '*.ipa' --dir output
python3 scripts/inspect_ipa.py output/YouMod_21.40.5_v2.0.0.ipa --require-decrypted
```

The first-build validation also confirmed that the main executable's Mach-O load
commands reference the injected YouMod and YouPiP libraries, beyond checking
that the files exist.

## Install and configure

If SideStore is not already working, follow the current
[installation prerequisites](https://docs.sidestore.io/docs/installation/prerequisites)
and [installation guide](https://docs.sidestore.io/docs/installation/install).
The guide uses iloader on the computer and LocalDevVPN on the phone. Apple
Account sign-in, trusting the computer/app, and Developer Mode belong on the
user's devices; keep passwords and pairing files private.

On the iPhone, open Safari and sign into GitHub as `danzola01`. Open the output
draft release linked above, expand Assets, and download
`YouMod_21.40.5_v2.0.0.ipa`. Keep the release as a draft. Alternatively, transfer
the verified local IPA to Files by a private method of the user's choice.

Connect the VPN used by your existing SideStore setup, open SideStore → My Apps
→ `+`, and choose the IPA from Files. If asked, remove the Safari app extension
to save an App ID; YouMod and YouPiP are injected in the main app and remain.
Keep the same extension choice on later updates. Launch YouMod after signing
and installation finish.

In YouTube settings, open YouMod and confirm:

- SponsorBlock is enabled and the Sponsor category uses automatic skipping.
- Downloading → Download manager is enabled. Choose video/audio from its download
  UI and verify that the saved file is accessible offline. On-device downloading
  is the current upstream default; use the app's alternatives if needed.
- Others → Background playback is enabled (current upstream default).
- Feed → Hide Shorts shelf is enabled; keep Shorts in subscriptions off.
- Tab bar customization disables the Shorts tab. This hides UI entry points;
  Shorts links can still open.
- YouPiP's settings allow picture-in-picture. Test by leaving a playing video.

## Device acceptance checks

All remain pending until the user tests the installed build:

| Requirement | Check | Result |
| --- | --- | --- |
| Video/feed ads | Play several videos and browse Home | Pending |
| SponsorBlock | Play a video with a known Sponsor segment; confirm auto-skip | Pending |
| Downloads | Save video and audio, then play saved files in airplane mode | Pending |
| PiP | Leave the app while a normal video plays | Pending |
| Background/locked playback | Switch apps, then lock screen; audio continues | Pending |
| Shorts hiding | Confirm shelf and tab are hidden after restarting | Pending |
| Signing refresh | Refresh the installed app successfully in SideStore | Pending |

## Updates

SideStore signing refresh renews the existing installation; it does not rebuild
the IPA. Free-account signing normally lasts seven days. Follow the current
[SideStore FAQ](https://docs.sidestore.io/docs/faq) for refresh and replacement
installation behavior.

For a tweak update, inspect upstream changes, fetch `upstream`, and merge
`upstream/main` into `sidestore`. Preserve the personal workflow changes, inspect
new defaults/dependencies, and push that branch. Rebuild with the same saved base
IPA and chosen inputs, retrieve the new draft asset, and install it through
SideStore over the existing app. Retest features affected by the changes.

Upstream references: [YouMod](https://github.com/Tonwalter888/YouMod),
[IPA workflow](https://github.com/Tonwalter888/YouMod/blob/main/.github/workflows/ipa.yml),
[YouPiP](https://github.com/PoomSmart/YouPiP). The tweak is open source; the
underlying YouTube app is proprietary.
