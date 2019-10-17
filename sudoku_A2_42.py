"""
"""

import sys
import copy

class Sudoku(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle                            # self.puzzle is a list of lists
        self.history = []                               # keeps track of order of cells assigned (for backtracking)




    def solve(self):
        board, cell = self.init_everything(puzzle)

        just_backtracked = False

        while True:
            next_val = cell.choose_next_value()

            if next_val == -1:                          # backtrack when no more legal values
                cell.value = 0
                self.propagate_arc_consistency_from(cell)
                cell.refresh_value_order()
                cell = self.history.pop()
                just_backtracked = True
                continue

            cell.value = next_val
            self.propagate_arc_consistency_from(cell)   # arc-consistency

            if just_backtracked:
                self.init_legal_values(board)
                just_backtracked = False
            else:
                if not self.forward_check_from(cell):   # if forward checking fails
                    self.init_legal_values(board)
                    continue                            # restart the loop - will try next value for this Cell

            # at this point the cell has been assigned a legal value and arc-consistency has been enforced.

            self.history.append(cell)
            cell = self.get_most_constrained_cell(board)

            if cell == None:                            # no cells left to fill
                break

        self.ans = self.board_to_2d_int_array(board)
        return self.ans



    """
======= CSP-related methods ========================================================================
    """
    # returns None if all cells are already filled.
    def get_most_constrained_cell(self, board):
        min_val = 9
        min_cell = None

        for r in board:
            for c in r:
                if c.value == 0 and c.count_legal_values() < min_val:
                    min_val = c.count_legal_values()
                    min_cell = c
        
        return min_cell



    # performs forward-checking from a given cell. updates the legal values of all "neighbor" cells
    # to reflect the newly-assigned value of the current cell.
    # will return False if the forward-checking results in some cell having no legal values.
    # NOTE: "neighbors" refers to neighbors in the constraint graph.
    def forward_check_from(self, cell):
        affected_neighbors = []

        # if neighbor already has a value, we don't need to worry about what other values are legal for it
        for neighbor in cell.neighbors:
            if neighbor.value != 0:
                continue

            # forward checking fails because the neighbor's only legal value is the same as this cell's current value
            if neighbor.count_legal_values() == 1 and neighbor.legal_values[cell.value]:
                return False
        
        # neighbors of this cell cannot legally have the same value as this cell
        for neighbor in cell.neighbors:
            if neighbor.value == 0 and neighbor.legal_values[cell.value]:
                neighbor.legal_values[cell.value] = False
                affected_neighbors.append(neighbor)

        return True



    # propagates arc-consistency. given a cell c, ensures that the following holds true for every
    # neighbor n:
    # for every value in domain of n, there is some value in domain of c s.t. the constraint holds.
    # if this is not the case then domain of n will be reduced.
    def propagate_arc_consistency_from(self, cell):

        # we ensure domains are kept up to date. as such, if the current cell has more than 1 value
        # in its domain, then the domains of its neighbors need not be reduced.
        if not cell.given:
            if cell.count_legal_values() > 1:
                return True
            elif cell.count_legal_values() == 0:
                return False

        affected_neighbors = []

        for neighbor in cell.neighbors:
            # neighbor already has a value. no need to modify its domain.
            if neighbor.value != 0:
                continue

            # loop through all legal values in domain of neighbor
            for i in range(1, 10):
                if not neighbor.legal_values[i]:
                    continue
                if cell.value == i or (cell.value == 0 and cell.legal_values[i]):
                    neighbor.legal_values[i] = False
                    affected_neighbors.append(neighbor)
                    continue
        
        for neighbor in affected_neighbors:
            if not self.propagate_arc_consistency_from(neighbor):
                return False
        
        return True
        

    # initializes the list of legal values for all cells in the board, then establishes arc-
    # consistency.
    def init_legal_values_ac(self, board):
        for i in range(9):
            for j in range(9):
                cell = board[i][j]

                if cell.given:
                    continue
                
                cell.open_all_legal_values()
        
        for i in range(9):
            for j in range(9):
                self.propagate_arc_consistency_from(board[i][j])
    

    # initializes the list of legal values for all cells in the board. this method is called after
    # backtracking, since doing so may re-open some values as being legal.
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







    """
======= Admin methods ==============================================================================
    """
    # performs startup initialization.
    def init_everything(self, puzzle):
        board = self.generate_board(self.puzzle)
        self.init_constraint_neighbors(board)
        self.init_legal_values_ac(board)
        cell = self.get_most_constrained_cell(board)

        return (board, cell)

    # generates a board of Cells from the given puzzle
    def generate_board(self, puzzle):
        board = []

        for i in range(9):
            row = []
            board.append(row)

            for j in range(9):
                cell = Cell(i, j, puzzle[i][j])
                row.append(cell)
        
        return board

    # populates each Cell's neighbors list with all its neighbors in the constraint graph
    def init_constraint_neighbors(self, board):
        for i in range(9):
            for j in range(9):
                cell = board[i][j]

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






"""
======= Cell =======================================================================================
"""


# representation of a Cell. each cell keeps track of its neighbors in the constraint graph, as well as
# all legal values for that Cell. note that if a Cell is marked as "given", then it is provided as
# part of the problem input, and thus will not be changed.
class Cell(object):
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.given = (self.value != 0)
        self.neighbors = []

        if not self.given:
            self.open_all_legal_values()
            self.refresh_value_order()

    # this method should never be called on a Cell that was given in the problem input.
    # there is no check for the above scenario because the programmer wants an exception to be thrown.
    def count_legal_values(self):
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

    def refresh_value_order(self):
        self.val_order = None

    # chooses a new value for this cell. values are chosen with least-constraining first.
    def choose_next_value(self):

        if self.val_order != None:
            if len(self.val_order) == 0:
                return -1
            else:
                return self.val_order.pop()[1]

        self.val_order = []

        for i in range(1, 10):
            if not self.legal_values[i]:
                continue

            current_constraint_count = 0
            
            for neighbor in self.neighbors:
                if neighbor.given:
                    continue

                if neighbor.legal_values[i]:
                    current_constraint_count += 1
            
            self.val_order.append((current_constraint_count, i))

        self.val_order = sorted(self.val_order, reverse=True)
        return self.choose_next_value()


    def open_all_legal_values(self):
        self.legal_values = [None] # make a one-indexed list.

        for i in range(9):
            self.legal_values.append(True)
    































































































"""
======= Don't change ===============================================================================
"""

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
