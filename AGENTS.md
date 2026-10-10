# SideStore personal YouMod build

This checkout is the `sidestore` branch of `danzola01/YouMod`; `upstream`
points to `Tonwalter888/YouMod`. Keep upstream build tooling and make small
changes on this branch. Build source must come from this fork and branch.

For IPA inspection, build dispatch, installation, or updates, read
`docs/SIDESTORE.md`. Record build/run/release identifiers there as work proceeds.
Device checks are complete only after the user reports the results.

Keep proprietary IPAs and signing material out of Git. Store credentials and
signed download URLs in secrets, never in tracked configuration or documentation.
Keep releases containing IPAs unpublished. Before dispatching, verify the base
IPA hash and encryption metadata and explicitly select companion tweaks.
