"""
    NOTE: backing up legal values takes too long. we prefer to re-initialize whenever required.
"""


import sys
import copy

class Sudoku(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle                # self.puzzle is a list of lists
        self.history = []


    def solve(self):
        board, cell = self.init_everything(puzzle) # cell -> most constrained variable

        just_backtracked = False

        while True:

            if just_backtracked:
                self.init_legal_values(board)
                

            next_val = cell.get_next_larger_legal_value()

            # backtracking
            if next_val == -1:
                cell.value = 0
                cell = self.history.pop()
                just_backtracked = True
                continue

            cell.value = next_val

            if just_backtracked:
                self.init_legal_values(board)
                just_backtracked = False
            else:
                if not self.forward_check_from(cell):
                    self.init_legal_values(board)
                    continue

            self.history.append(cell)

            cell = self.get_most_constrained_cell(board)

            if cell == None:
                break

        self.ans = self.board_to_2d_int_array(board)
        return self.ans



    def get_most_constrained_cell(self, board):
        
        min_val = 9
        min_cell = None

        for r in board:
            for c in r:
                if c.value == 0 and c.legal_count() < min_val:
                    min_val = c.legal_count()
                    min_cell = c
        
        return min_cell

    def forward_check_from(self, cell):
        affected_neighbors = []

        for neighbor in cell.neighbors:
            if neighbor.given:
                continue

            if neighbor.legal_count() == 1 and neighbor.legal_values[cell.value]:
                return False
        
        for neighbor in cell.neighbors:
            if neighbor.value == 0 and neighbor.legal_values[cell.value]:
                neighbor.legal_values[cell.value] = False
                affected_neighbors.append(neighbor)

        if len(affected_neighbors) == 0:
            return True
        
        for neighbor in affected_neighbors:
            if not self.propagate_arc_consistency_from(neighbor):
                return False
        
        return True


    def propagate_arc_consistency_from(self, cell):

        if cell.legal_count() > 1:
            return True

        affected_neighbors = []

        for n in cell.neighbors:

            if n.value != 0:
                continue

            for i in range(1, 10):
                if not n.legal_values[i]:
                    continue
                if cell.legal_values[i]:
                    n.legal_values[i] = False
                    affected_neighbors.append(n)
                    continue
        
        if len(affected_neighbors) == 0:
            return True
        
        for n in affected_neighbors:
            if not self.propagate_arc_consistency_from(n):
                return False
        
        return True
        


    def init_legal_values(self, board):
        for i in range(9):
            for j in range(9):
                cell = board[i][j]

                if cell.given:
                    continue
                
                cell.open_all_legal_values()
                
                for neighbor in cell.neighbors:
                    if neighbor.value == 0:
                        continue
                    
                    cell.legal_values[neighbor.value] = False












    def init_everything(self, puzzle):
        board = self.generate_board(self.puzzle)
        self.init_constraint_neighbors(board)
        self.init_legal_values(board)
        cell = self.get_most_constrained_cell(board)

        while (cell.legal_count() == 1):
            self.propagate_arc_consistency_from(cell)
            cell = self.get_most_constrained_cell(board)

        return (board, cell)

    def generate_board(self, puzzle):
        board = []

        for i in range(9):
            row = []
            board.append(row)

            for j in range(9):
                cell = Cell(i, j, puzzle[i][j])
                row.append(cell)
        
        return board

    def init_constraint_neighbors(self, board):
        for i in range(9):
            for j in range(9):
                cell = board[i][j]

                if cell.given:
                    continue

                for k in range(9):
                    self.try_neighbor(cell, board, i, k)
                    self.try_neighbor(cell, board, k, j)
                
                for k in range(3):
                    for m in range(3):
                        
                        x = (i//3)*3 + k
                        y = (j//3)*3 + m

                        if x == cell.x or y == cell.y:
                            continue

                        self.try_neighbor(
                            cell,
                            board,
                            x,
                            y
                        )

    def try_neighbor(self, cell, board, x, y):
        other = board[x][y]

        if not other.equals(cell):
            cell.add_neighbor(other)


    def board_to_2d_int_array(self, board):
        rv = []
        
        for i in range(9):
            row = []
            rv.append(row)
            for j in range(9):
                row.append(board[i][j].value)
        
        return rv



















class Cell(object):
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.given = (self.value != 0)
        self.neighbors = []

        if not self.given:
            self.open_all_legal_values()
    
    # this method should never be called on a given Cell.
    # there is no check for the above scenario because the programmer wants an exception to be thrown.
    def legal_count(self):
        count = 0

        for b in self.legal_values:
            if b:
                count += 1
        
        return count
    
    # note that "neighbor" here refers to a neighbor in the constraint graph.
    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
    
    def equals(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def get_next_larger_legal_value(self):
        for i in range(self.value + 1, 10):
            if self.legal_values[i]:
                return i
        
        return -1

    def open_all_legal_values(self):
        self.legal_values = [None] # make a one-indexed list.

        for i in range(9):
            self.legal_values.append(True)
    
































































































if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
