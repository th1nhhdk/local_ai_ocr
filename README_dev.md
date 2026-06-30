<img src='src/res/icon.png' width='128' height='128'>

# Local AI OCR (v3.0.0)

## Tech Stack
- **Python:** Embeddable Python `3.13.14`
- **transformers:** `4.46.3`
- **Frontend:** PySide6 `6.11.1`
- **src/res/node/mathjax:** `4.0.0`
- **src/res/node/@mathjax/mathjax-newcm-font:** `4.0.0`

## Environment setup
- Execute `env_setup.cmd`.

## Packaging
- Execute `make_release.cmd` to create release zip.

## Debloating `src/res/node/mathjax` and `src/res/node/@mathjax/mathjax-newcm-font`
```
./core.js
./loader.js
./startup.js
./mml-chtml-nofont.js
./mml-chtml.js
./mml-svg-nofont.js
./mml-svg.js
./tex-chtml-nofont.js
./tex-chtml.js
./tex-mml-chtml-nofont.js
./tex-mml-chtml.js
./tex-mml-svg-nofont.js
./tex-svg-nofont.js
./tex-svg.js
./input/asciimath.js
./input/mml.js
./input/tex.js
./input/tex-base.js
./input/mml/
./output/
./ui/
./chtml/
./examples/
```