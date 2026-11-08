# RoyaltyFree Inspector

Applicazione desktop (Windows, macOS, Linux) per analizzare provenienza e licenza dei contenuti.

## Struttura
- `main.py` – avvio
- `rfi/models.py` – modelli (`ContentItem`, `LicenseInfo`, `Status`)
- `rfi/licenses.py` – riconoscimento licenze da testo/URL
- `rfi/evaluation.py` – regole degli stati Verificato / Da verificare / Non autorizzato
- `rfi/sources/` – fonti online (una classe per catalogo, vedi `base.py`)
- `rfi/local_scan.py` – analisi cartelle (XMP, `.license`, LICENSE di cartella)
- `rfi/url_check.py` – verifica di un URL
- `rfi/report.py` – esportazione CSV
- `rfi/ui/` – interfaccia PySide6

## Avvio
    python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python main.py

## Aggiungere una fonte
Crea una sottoclasse di `Source` in `rfi/sources/`, implementa `search()` e registrala in `rfi/sources/__init__.py`.

## Pacchetti
- Windows: `build_windows.bat` (exe) / `build_installer.bat` (installer)
- Linux: `./build_appimage.sh` (AppImage)
