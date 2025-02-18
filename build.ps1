$pyInstallerCommand = "pyinstaller main.py --onefile --add-data `".\common_old.onnx;ddddocr`""

Invoke-Expression $pyInstallerCommand

