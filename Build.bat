pip install --upgrade pyinstaller
python -m PyInstaller --noconsole --name AudicaSongSpeeder source\main.py
python spec_fix.py
python -m PyInstaller AudicaSongSpeeder.spec
pause