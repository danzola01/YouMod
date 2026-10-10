# Personal YouMod build

## Current state

- Code fork: https://github.com/danzola01/YouMod
- Personal branch: `sidestore`; upstream branch: `Tonwalter888/YouMod/main`.
- Initial upstream commit: `fb6a9f6f3bbfcbe8aa8b92debda6405f2b7be2d7`.
- Base IPA: `com.google.ios.youtube-21.40.5-Decrypted.ipa` in the project root.
- Inspection: `base-ipa.json` records integrity, version, minimum OS, hash and
  encryption metadata. All seven detected Mach-O executables have `cryptid: 0`.
  No dylibs, provisioning profiles, or obvious YouMod/YouPiP resources were found.
  Metadata checks do not establish the binary's provenance or device behavior.
- Target reported by user: iPhone 17, iOS 27.0. Base IPA requires iOS 17.0.
- Upload destination: awaiting user selection. No IPA uploaded or build run yet.
- SideStore setup and on-device feature checks: unconfirmed.

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

Use `.github/workflows/ipa.yml` on the `sidestore` branch after supplying the
approved download source. Keep download credentials and signed URLs out of this
document and the committed inputs file. The hosted macOS runner builds and
injects the tweaks; no local Mac is required.

Confirm the workflow succeeds and the output release remains a draft. Download
with authenticated GitHub access, then inspect the resulting IPA for YouMod and
YouPiP dylibs, the expected app identity, and encryption metadata. Record the run
URL, source commit, draft tag and output hash here. Never publish a release
containing the proprietary IPA.

## Install and configure

If SideStore is not already working, follow the current
[installation prerequisites](https://docs.sidestore.io/docs/installation/prerequisites)
and [installation guide](https://docs.sidestore.io/docs/installation/install).
The guide uses iloader on the computer and LocalDevVPN on the phone. Apple
Account sign-in, trusting the computer/app, and Developer Mode belong on the
user's devices; keep passwords and pairing files private.

Transfer the final IPA to Files on the iPhone. Connect LocalDevVPN, open
SideStore → My Apps → `+`, and choose the IPA. If SideStore offers to remove app
extensions, removing them saves App IDs; the Safari/Share/widget features then
will not be installed. Keep the same extension choice on later updates.

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
