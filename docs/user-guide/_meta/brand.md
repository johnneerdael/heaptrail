# HeapTrail brand: where the assets come from

For anyone who updates the identity. This file is not published (`exclude_docs` in `mkdocs.yml`).

The identity is **HeapTrail Brand Kit 1.0** (25 October 2026), made for this project and shared with WireTrail. The kit ships its own guide (`HeapTrail-Brand-Guide.html`) and rules (`README.md`, `INTEGRATION.md`). This repository keeps only what the README, the release notes and the user guide use, not the whole kit.

## What is used, and where it came from

Every file below is byte-identical to the kit, and its SHA-256 matches the kit's `asset-manifest.json`. The prefix is `docs/`.

| In this repository | In the kit | SHA-256 (start) |
|---|---|---|
| `user-guide/assets/brand/heaptrail-mark-on-dark.svg` | `01-logos/marks/heaptrail-mark-on-dark.svg` | `e658107ee4f2` |
| `user-guide/assets/brand/favicon.svg` | `02-platform-icons/web/favicon.svg` | `bda7bfcc7902` |
| `user-guide/assets/brand/favicon.ico` | `02-platform-icons/web/favicon.ico` | `fa9e479f717f` |
| `user-guide/assets/brand/favicon-32x32.png` | `02-platform-icons/web/favicon-32x32.png` | `6cdfcc7ddbeb` |
| `user-guide/assets/brand/favicon-16x16.png` | `02-platform-icons/web/favicon-16x16.png` | `ff8d57bcc1c5` |
| `user-guide/assets/brand/apple-touch-icon.png` | `02-platform-icons/web/apple-touch-icon.png` | `487b2fa6373c` |
| `user-guide/assets/brand/heaptrail-social-dark-1200x630.png` | `03-banners/heaptrail-social-dark-1200x630.png` | `048cdbbacbde` |
| `assets/brand/heaptrail-readme-light-1600x480.png` | `03-banners/heaptrail-readme-light-1600x480.png` | `be6dabf2e5ec` |
| `assets/brand/heaptrail-readme-dark-1600x480.png` | `03-banners/heaptrail-readme-dark-1600x480.png` | `cbcbc22e67b5` |
| `assets/brand/heaptrail-github-dark-1280x640.png` | `03-banners/heaptrail-github-dark-1280x640.png` | `18628b30dee2` |
| `user-guide/assets/fonts/SpaceGrotesk.woff` | `07-fonts/SpaceGrotesk.woff` | `7b7f926bd3f5` |
| `user-guide/assets/fonts/Inter.woff` | `07-fonts/Inter.woff` | `dcfc3feb79a1` |
| `user-guide/assets/fonts/IBMPlexMono-Regular.woff` | `07-fonts/IBMPlexMono-Regular.woff` | `b4719702a5c6` |
| `user-guide/assets/fonts/*-OFL.txt` (three files) | `07-fonts/*-OFL.txt` | see the kit |

Two copies are changed on purpose:

- **The 16 glyphs** in `overrides/.icons/heaptrail/` come from `04-integration-artwork/ui-icons/`. The kit labels each with `role="img"`, `aria-label` and a `<title>`. They sit beside a visible heading here, so those are replaced with `aria-hidden="true"`, as the kit's `INTEGRATION.md` advises for decorative glyphs. The paths are untouched.
- **The colour tokens** in `user-guide/stylesheets/heaptrail.css` are the values of `06-implementation/brand-tokens.css`, written under Material's `data-md-color-scheme` selectors (`default` and `slate`) instead of the kit's `data-theme`. The code-highlighting colours are chosen from the same tokens.

## Where each thing is used

| Asset | Used by |
|---|---|
| `heaptrail-readme-{light,dark}-1600x480.png` | `README.md`, in a `<picture>` that follows the reader's colour scheme, and the top of each release's notes (see `release-notes.md`) |
| `heaptrail-github-dark-1280x640.png` | GitHub's social preview. GitHub has no API for it: upload the file in Settings, General, Social preview |
| `heaptrail-social-dark-1200x630.png` | `og:image` and `twitter:image` on every page, from `overrides/main.html` |
| `heaptrail-mark-on-dark.svg` | The header logo. The header is Night in both colour schemes, so the on-dark mark is always right |
| `favicon.svg`, `favicon.ico`, `apple-touch-icon.png` | The browser tab and the home-screen icon. `favicon-16x16.png` and `favicon-32x32.png` are kept for tools that look for them |
| The three `.woff` fonts | `@font-face` in `heaptrail.css`. `font: false` in `mkdocs.yml` keeps Material from loading Google Fonts |
| The 16 glyphs | `:heaptrail-trace:` and so on, through `pymdownx.emoji` in `mkdocs.yml`. The home page cards use nine of them |

Not used, on purpose: the PWA manifest and the maskable icons (a documentation site is not an installable app), the platform icon sets for Windows, macOS and Linux (HeapTrail is a command-line tool with no GUI), the template and monochrome artwork, and the background pattern. They stay in the kit.

## Rules from the kit that the guide follows

- Write HeapTrail in prose and branding. The executable is `heaptrail`. `scripts/docs-check.py` enforces this.
- Clear space of 16 units around a 100-unit mark. The horizontal logo is at least 160 px wide; below that, use the mark. Do not distort, rotate or add effects.
- Light surfaces use `#8C4C00` for links and filled controls, with white text. Dark surfaces use `#F5A623` for filled controls, with Night text, and `#FFC56B` for links.
- Status colours always come with a label, an icon or a code. The product colour is never a severity scale.
- Keep machine output stable: no logo, colour code or marketing in JSON, and respect `NO_COLOR`. Branding belongs in documentation, release material and package listings, not in the terminal output.

## Licence and trademark

The kit's README says that the Apache-2.0 licence of the HeapTrail code "is not a new declaration about this artwork", that the artwork was created for the kit, and that no trademark clearance is claimed. This repository adds no licence statement for the artwork either. The fonts keep their SIL Open Font Licence notices, which travel with them in `assets/fonts/`.

## Updating to a new kit

1. Unpack the new kit into an empty folder, outside the repository.
2. Compare the files in the table above with `shasum -a 256` and the kit's `asset-manifest.json`. Replace the ones that changed.
3. Copy the glyphs again and replace `role`, `aria-label` and `<title>` with `aria-hidden="true"`.
4. Compare `06-implementation/brand-tokens.css` with the token blocks in `heaptrail.css`.
5. Update the table above, then run the three checks in `style.md`.
