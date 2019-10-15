cls
git checkout arc-consistency-propagation
powershell -Command "Measure-Command {python sudoku_A2_xx.py input.txt output.txt | Out-Default}"
git checkout master
powershell -Command "Measure-Command {python sudoku_A2_42.py input.txt output.txt | Out-Default}"

