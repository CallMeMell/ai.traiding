@echo off
REM Lege einen Ordner für überflüssige Dateien an
mkdir unused_files

REM Verschiebe nicht benötigte Dateien (Liste ggf. anpassen!)
move pw.txt unused_files\
move build_features_and_train.bat unused_files\
move run_backtest.bat unused_files\
move run_testnet.bat unused_files\
move download_all_data.bat unused_files\
move QUICK_START.md unused_files\
pause
