#!/usr/bin/env bash
set -euo pipefail

# Lumina macOS .app and .dmg Packaging Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "=== Building Lumina macOS Application Bundle ==="
cd "${ROOT_DIR}"

# 1. Ensure ICNS Icon exists
ICNS_PATH="${ROOT_DIR}/assets/icons/lumina.icns"
if [[ ! -f "${ICNS_PATH}" ]]; then
    echo "→ Generating lumina.icns from logo.svg..."
    mkdir -p "${ROOT_DIR}/assets/icons" /tmp/lumina_icon.iconset
    qlmanage -t -s 1024 -o /tmp "${ROOT_DIR}/assets/images/readme/logo.svg" >/dev/null 2>&1
    mv /tmp/logo.svg.png /tmp/lumina_1024.png
    sips -z 16 16     /tmp/lumina_1024.png --out /tmp/lumina_icon.iconset/icon_16x16.png >/dev/null
    sips -z 32 32     /tmp/lumina_1024.png --out /tmp/lumina_icon.iconset/icon_16x16@2x.png >/dev/null
    sips -z 32 32     /tmp/lumina_1024.png --out /tmp/lumina_icon.iconset/icon_32x32.png >/dev/null
    sips -z 64 64     /tmp/lumina_1024.png --out /tmp/lumina_icon.iconset/icon_32x32@2x.png >/dev/null
    sips -z 128 128   /tmp/lumina_1024.png --out /tmp/lumina_icon.iconset/icon_128x128.png >/dev/null
    sips -z 256 256   /tmp/lumina_1024.png --out /tmp/lumina_icon.iconset/icon_128x128@2x.png >/dev/null
    sips -z 256 256   /tmp/lumina_1024.png --out /tmp/lumina_icon.iconset/icon_256x256.png >/dev/null
    sips -z 512 512   /tmp/lumina_1024.png --out /tmp/lumina_icon.iconset/icon_256x256@2x.png >/dev/null
    sips -z 512 512   /tmp/lumina_1024.png --out /tmp/lumina_icon.iconset/icon_512x512.png >/dev/null
    cp /tmp/lumina_1024.png /tmp/lumina_icon.iconset/icon_512x512@2x.png
    iconutil -c icns /tmp/lumina_icon.iconset -o "${ICNS_PATH}"
    rm -rf /tmp/lumina_icon.iconset /tmp/lumina_1024.png
    echo "✓ lumina.icns ready."
fi

# 2. Run PyInstaller
echo "→ Running PyInstaller..."
PYTHON_BIN="${PYTHON:-.venv/bin/python}"
"${PYTHON_BIN}" -m PyInstaller --noconfirm --clean "${SCRIPT_DIR}/Lumina.spec"

APP_PATH="${ROOT_DIR}/dist/Lumina.app"
if [[ ! -d "${APP_PATH}" ]]; then
    echo "Error: Lumina.app was not created!"
    exit 1
fi
echo "✓ Lumina.app created successfully at ${APP_PATH}"

# 3. Build DMG Disk Image
echo "→ Packaging Lumina.dmg..."
DMG_STAGING="${ROOT_DIR}/dist/dmg_staging"
rm -rf "${DMG_STAGING}"
mkdir -p "${DMG_STAGING}"

cp -R "${APP_PATH}" "${DMG_STAGING}/"
ln -s /Applications "${DMG_STAGING}/Applications"

VERSION="$("${PYTHON_BIN}" -c "import sys; sys.path.insert(0, 'src'); from lumina import __version__; print(__version__)")"
DMG_OUTPUT="${ROOT_DIR}/dist/Lumina-${VERSION}-macos.dmg"
DMG_EVERGREEN="${ROOT_DIR}/dist/Lumina-macos.dmg"
rm -f "${DMG_OUTPUT}" "${DMG_EVERGREEN}"

hdiutil create -volname "Lumina Studio" \
    -srcfolder "${DMG_STAGING}" \
    -ov -format UDZO \
    "${DMG_OUTPUT}"

cp "${DMG_OUTPUT}" "${DMG_EVERGREEN}"
rm -rf "${DMG_STAGING}"
echo "✓ DMG created successfully: ${DMG_OUTPUT}"
echo "✓ Evergreen DMG created: ${DMG_EVERGREEN}"
ls -lh "${DMG_OUTPUT}" "${DMG_EVERGREEN}"
