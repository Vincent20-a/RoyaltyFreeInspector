#!/usr/bin/env bash
# Crea RoyaltyFreeInspector-x86_64.AppImage
# Requisiti: Linux x86_64, Python 3.10-3.13 (con venv), curl o wget.
# Consiglio: compilare su una distro non troppo recente (es. Ubuntu 22.04)
# per massimizzare la compatibilita' con le altre distribuzioni.
set -euo pipefail
cd "$(dirname "$0")"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

rm -rf build dist AppDir
pyinstaller --noconfirm --clean --windowed \
    --name RoyaltyFreeInspector \
    --add-data "assets/icon.png:assets" \
    --collect-submodules rfi \
    main.py

# --- AppDir ---
mkdir -p AppDir/usr/lib AppDir/usr/share/icons/hicolor/256x256/apps
cp -r dist/RoyaltyFreeInspector AppDir/usr/lib/
cp packaging/AppRun AppDir/AppRun && chmod +x AppDir/AppRun
cp packaging/RoyaltyFreeInspector.desktop AppDir/
cp assets/icon.png AppDir/RoyaltyFreeInspector.png
cp assets/icon.png AppDir/usr/share/icons/hicolor/256x256/apps/RoyaltyFreeInspector.png

# --- appimagetool ---
TOOL=./appimagetool-x86_64.AppImage
if [ ! -x "$TOOL" ]; then
    URL=https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    if command -v curl >/dev/null; then curl -L -o "$TOOL" "$URL"; else wget -O "$TOOL" "$URL"; fi
    chmod +x "$TOOL"
fi

ARCH=x86_64 "$TOOL" --appimage-extract-and-run AppDir RoyaltyFreeInspector-x86_64.AppImage
chmod +x RoyaltyFreeInspector-x86_64.AppImage
echo
echo "Fatto! -> RoyaltyFreeInspector-x86_64.AppImage"
