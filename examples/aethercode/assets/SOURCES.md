# Asset sources

All assets below are embedded in `../aethercode-pipeline.drawio` as data URIs (`shape=image` / `shape=label` styles); the drawio file does not reference any online image. These local copies let `../../verification/build_drawio.py` regenerate the identical file.

## Logos (Wikimedia Commons, retrieved 2026-09-28)

| File | Source | License on Commons | Use in figure |
| --- | --- | --- | --- |
| `ioi-logo.png` (original, 1258×691) | https://commons.wikimedia.org/wiki/File:IOI_logo.png (credit: ioinformatics.org) | Public domain | not embedded; kept as provenance |
| `ioi-logo-small.png` (360×198) | downscaled from `ioi-logo.png`, no other change | same | OI series card |
| `icpc-logo.png` (original, 472×376) | https://commons.wikimedia.org/wiki/File:ICPC_logo.png (author: ACM ICPC; credit: ICPC Foundation site) | Public domain; Commons marks it as trademarked | not embedded; kept as provenance |
| `icpc-foundation-mark.png` (354×197) | cropped from `icpc-logo.png`: rays and "icpc.foundation" wordmark kept, outer rounded border and tagline removed, white made transparent; colours and letterforms unchanged | same | ICPC series card |

The logos are trademarks of their owners and identify the two contest series named in the paper. Commons has no other ICPC mark, so the ICPC Foundation mark is used.

## Icons

Tabler Icons 3.48.0, outline set, MIT License (`tabler/LICENSE`, copyright Paweł Kuna), from `https://cdn.jsdelivr.net/npm/@tabler/icons@3.48.0/icons/outline/<name>.svg`.

Used: award, binary-tree, calendar-event, calendar-stats, chart-bar, circle-check, circle-x, file-check, file-code, file-text, files, gavel, photo-off, settings-automation, shield-check, stack-2, target-arrow, user-check, users-group.

Modification at embed time only: stroke colour set to the section colour and stroke width 2 changed to 1.8. The files in `tabler/` are unmodified originals.

## Checksums (SHA-256)

```
c561c1fd95d4ac58455a7c48f9f2445dd671c4b1f686e47f530fe2174d303711  ioi-logo.png
a8e9e9e6e4481976d25ecfda8456b9375d14a6f0de11d18be7e508461f3327cb  ioi-logo-small.png
04d4b567ded7ba143807f4f53b5e193850afd2e92662583a07bd57e77f0ae745  icpc-logo.png
b1e7fbb0ae7bbb90b5a035a7c4535de1ec952f989d9a998753ce9401a8085195  icpc-foundation-mark.png
b740a1d46122672da62833e97f7e7c8a13fa85cbc7445b584b297cc00dde93db  tabler/LICENSE
```
