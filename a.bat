del output.txt
cls
powershell -Command "Measure-Command {python sudoku_A2_xx.py input.txt output.txt | Out-Default}"
fc output.txt expected.txt

