# Changelog

## [1.4.0](https://github.com/AtaCanYmc/lumina/compare/lumina-tools-v1.3.0...lumina-tools-v1.4.0) (2026-11-15)


### Features

* **docs:** add homebrew tap install command and hero package switcher ([fcabc42](https://github.com/AtaCanYmc/lumina/commit/fcabc42361fca9a4db77fedd04042cb7fc2c90e1))


### Documentation

* fix package name to lumina-tools and document pipx installation ([37754fb](https://github.com/AtaCanYmc/lumina/commit/37754fb37e07495b5dd8f9968f1f388b6b6f61b4))

## [1.3.0](https://github.com/AtaCanYmc/lumina/compare/lumina-tools-v1.2.0...lumina-tools-v1.3.0) (2026-11-15)


### Features

* **pages:** add responsive antislop github pages landing and distribution site ([a7dd865](https://github.com/AtaCanYmc/lumina/commit/a7dd86517c6dbb1b7e018e43e19349b9ebea2e50))
* **pages:** localize landing page to English and optimize mobile header ([e9fe00e](https://github.com/AtaCanYmc/lumina/commit/e9fe00ec6e1a14c331aef0eeaf4768c440e1dfa7))
* **release:** configure dynamic versioning with release-please extra-files and evergreen DMG ([261a0a7](https://github.com/AtaCanYmc/lumina/commit/261a0a7fcca803ef795d2993c2f81de1b2ec8f87))


### Bug Fixes

* **ci:** make Python package publishing retries idempotent ([d09c997](https://github.com/AtaCanYmc/lumina/commit/d09c997caafdefb4cdc549b1f7d628927bccd128))
* **ci:** robust python interpreter resolution in build_dmg.sh for github actions ([1dbca33](https://github.com/AtaCanYmc/lumina/commit/1dbca33ada8e29566e269649254cef064d701e45))
* **styles:** prevent vertical image distortion in 3D inspector feature card ([bbbe4c4](https://github.com/AtaCanYmc/lumina/commit/bbbe4c4e6d6bcc03b63bd7ba34f12e690ebad3ea))


### Documentation

* polish documentation and add governance automations via well-document ([a038410](https://github.com/AtaCanYmc/lumina/commit/a0384108740d619f0ce7321833f66371d8e5aefa))

## [1.2.0](https://github.com/AtaCanYmc/lumina/compare/lumina-tools-v1.1.0...lumina-tools-v1.2.0) (2026-11-15)


### Features

* **cli:** enhance terminal ui and add interactive wizard ([765728b](https://github.com/AtaCanYmc/lumina/commit/765728bc9561a1659f03d80ede9e34375f988de2))
* **gui:** implement PySide6 desktop studio with drag-and-drop and dual-mode tabs ([c832dd9](https://github.com/AtaCanYmc/lumina/commit/c832dd965c91297758a0062e8bebdc7557b0e7d9))
* **packaging:** add standalone macos .app and .dmg packaging workflow ([7fab108](https://github.com/AtaCanYmc/lumina/commit/7fab1086e96ad5134f66a4a18324c651ba1f1795))
* **viewer:** implement real-time 3d viewport and backlight transmission simulation ([59b456e](https://github.com/AtaCanYmc/lumina/commit/59b456ea1fbf36c4d145dbb98627fecf26bbdf43))


### Bug Fixes

* **build:** auto-bootstrap pip in venv if missing ([30ddf44](https://github.com/AtaCanYmc/lumina/commit/30ddf444bb88dfd24d5dfe8ced92d021a1e99627))
* **build:** resolve pip command not found in Makefile using python module invocation ([d16bf99](https://github.com/AtaCanYmc/lumina/commit/d16bf9906d69c88952c1d517af9df7daea907663))
* **deps:** remove conflicting stl package shadowing numpy-stl ([3d26142](https://github.com/AtaCanYmc/lumina/commit/3d26142ba2e0671f398e42b85a1aa2d1e2db9eba))


### Documentation

* add vector logo banner to README header ([7a480c9](https://github.com/AtaCanYmc/lumina/commit/7a480c943942feb41f8448bc9f6c95feab4d5cb9))
* **readme:** add desktop studio and 3d viewport screenshots ([2b08bbe](https://github.com/AtaCanYmc/lumina/commit/2b08bbeb51d633c9a0c3401642a10f84a4da44c1))
* replace banner with minimalist square vector logo mark ([64c9eb9](https://github.com/AtaCanYmc/lumina/commit/64c9eb97858b5dca57899594def6ddc550019f22))
* update API, architecture, and quick start references for 3d viewer ([5ee7be3](https://github.com/AtaCanYmc/lumina/commit/5ee7be37744428a6fbb4f0f4930d73ed8952c7cf))

## [1.1.0](https://github.com/AtaCanYmc/lumina/compare/lumina-tools-v1.0.0...lumina-tools-v1.1.0) (2026-11-15)


### Features

* Add `spiral` CLI command to generate spiral Betty art from images. ([8821708](https://github.com/AtaCanYmc/lumina/commit/8821708508f5014e71fa78605b54152b7d463e33))
* Add `to_spiral` image transformation and simplify `jpg_to_stl` by removing frame parameters. ([944e0a0](https://github.com/AtaCanYmc/lumina/commit/944e0a0e85c3c71e9540a018c0d79acfd0387000))
* Add an `invert` parameter to `filename_to_stl` to control image inversion. ([5a8865b](https://github.com/AtaCanYmc/lumina/commit/5a8865b8f62a6adb7d4cc52928be622292c3b420))
* Add contributing guidelines and update README with quick start examples and a feature table. ([e637b67](https://github.com/AtaCanYmc/lumina/commit/e637b67b8d6670f3b893c26cf9f64f8f4aac38e3))
* Add GitHub Actions workflows for CI testing and PyPI package publishing. ([c499e0f](https://github.com/AtaCanYmc/lumina/commit/c499e0f178f8270a9139431c4b7ca7239845cbbb))
* Add normalize option for image processing and enhance grayscale handling ([d83af7e](https://github.com/AtaCanYmc/lumina/commit/d83af7e169411b1e44cb853d7f29d0af06096e76))
* add scripts to bump version and check distribution version ([1bfc831](https://github.com/AtaCanYmc/lumina/commit/1bfc83137862266e753d90d3ee7c5215a3062fde))
* **brew:** add homebrew formula and installation instructions ([c09d80d](https://github.com/AtaCanYmc/lumina/commit/c09d80d1d8e7476c112ed0cbab947a0c95238ee2))
* Enhance the CLI with detailed options for flat lithophane generation and introduce comprehensive API and CLI documentation. ([a79d608](https://github.com/AtaCanYmc/lumina/commit/a79d60871ea6b76a585f707266fa40c017c9c6ee))
* Implement bitmap generation and export to C-array/hex for embedded displays via new CLI command and library functions. ([4b0bf51](https://github.com/AtaCanYmc/lumina/commit/4b0bf51b6b02e64052814b8f7c048f93bf094e04))
* Implement RGBA canvas for image generation, add new output examples, and update gitignore to track new assets. ([a71336d](https://github.com/AtaCanYmc/lumina/commit/a71336d8c548f08178d26ce0d0dd6f6bb3c68a6b))
* Implement shape strategy for STL generation, enhance frame handling with CV2, and add new tests. ([2bde33e](https://github.com/AtaCanYmc/lumina/commit/2bde33e9e398644115d4af97930a4898818546a4))
* Implement spiral art generation with `generate_spiral_betty_png` API, core logic adjustments, and dedicated tests. ([b80da73](https://github.com/AtaCanYmc/lumina/commit/b80da73e02917cf28154130e2450f422c2586f3f))


### Bug Fixes

* Adjust heart mask generation to scale coordinates and render the heart upright. ([8e68c63](https://github.com/AtaCanYmc/lumina/commit/8e68c63133cd3cdc562f017bb2e0de601bf41f11))
* **ci:** resolve ruff linter errors and configure lint rules ([0ca0732](https://github.com/AtaCanYmc/lumina/commit/0ca07329776bbc734977f94579df9d91a154ba0e))
* Ensure shaped lithophane frames maintain correct height by explicitly setting Z-levels during frame generation. ([95393a5](https://github.com/AtaCanYmc/lumina/commit/95393a55d75a3a7234ced6746b798ea9720902d2))
* **release:** ensure consistent multi-line output for changelog in GitHub Actions ([b5896d7](https://github.com/AtaCanYmc/lumina/commit/b5896d79f451ca76203cfe6a10edd5923fb10ccc))
* **security:** sanitize inputs, harden CLI error handling, and remediate GHA injection ([ea4dc18](https://github.com/AtaCanYmc/lumina/commit/ea4dc18e73da802ded82ae6d836e8bcd05953bca))
* Update import paths for core services and enhance Z value handling in STL generation ([4580cac](https://github.com/AtaCanYmc/lumina/commit/4580cac634ede1816fa08556b013d86ae27e13a2))
* Update Python version formatting in CI configuration files ([40d6d75](https://github.com/AtaCanYmc/lumina/commit/40d6d75e90dd908224c3dd59d6b5af2586b50de6))
* update readme ([16d2376](https://github.com/AtaCanYmc/lumina/commit/16d237626f90224f37af58555bfb2903826a6d70))


### Documentation

* Add documentation for `lumina.generate_bitmap` function. ([7d4c5e2](https://github.com/AtaCanYmc/lumina/commit/7d4c5e2b9a7427e38f31c9ac0ae6d56aa929139d))
* add repository governance, security policy, and github templates ([3ca3ca4](https://github.com/AtaCanYmc/lumina/commit/3ca3ca4032e9ffa509d44c2836c0bf08226ac307))
* add spiral-&gt;lithophane example; add LICENSE; cli entrypoint ([b407e6c](https://github.com/AtaCanYmc/lumina/commit/b407e6c0e72fdc679666cde89a981ada74f77ce0))
* eliminate AI slop, ground technical references, and refine governance ([ec52adb](https://github.com/AtaCanYmc/lumina/commit/ec52adbd933caab4640ac295cb30af75b98c9509))
* remove Bitmap examples from README ([881d363](https://github.com/AtaCanYmc/lumina/commit/881d363d465fa1d3601c95e2b086f74ac912d4b0))
* remove bitmap references from CLI and API docs ([2648643](https://github.com/AtaCanYmc/lumina/commit/264864301bdd321332d50c3799cf176d2e011be8))
* remove bitmap_service reference from CONTRIBUTING ([2b03369](https://github.com/AtaCanYmc/lumina/commit/2b0336917a94d68289abc192e9d8c3d4421b11ba))
* **roadmap:** add project roadmap for desktop application and feature milestones ([84f49e5](https://github.com/AtaCanYmc/lumina/commit/84f49e5f2da858ed967004a721654c14587769c9))
