"""
    NOTE: use self.puzzle instead of puzzle

    TODO
    remove all the debugging st8ments, incl. print()
    to_str in cell class
"""


import sys
import copy
import heapq

class Sudoku(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle                # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle)    # self.ans is a list of lists
        self.history = []


    def solve(self):
        board, queue, cell = self.init_everything(puzzle) # cell -> most constrained variable

        just_backtracked = False

        while queue.size() > 0:

            if just_backtracked:
                self.init_legal_values(board)   # problem is that afte3r backtracking, u don't reinitr correclty. u do it ased on old val.
                

            next_val = cell.next_larger_legal_value()

            # backtracking
            if next_val == -1:
                cell.value = 0
                cell = self.history.pop()
                just_backtracked = True
                continue

            cell.value = next_val

            if just_backtracked:
                self.init_legal_values(board)   # problem is that afte3r backtracking, u don't reinitr correclty. u do it ased on old val.
                queue = self.queue_all_cells(board)
                just_backtracked = False
            else:
                if not self.forward_check(cell):
                    continue

            queue.heapify() #doesn't work.
            self.history.append(cell)
            cell = queue.pop()  # this is the cell representing the most constrained variable

        self.ans = self.board_to_2d_int_array(board)
        return self.ans



    def print_board(self, board):
        for r in board:
            for c in r:
                if c.value == 0:
                    print(" ", end=" ")
                else:
                    print(str(c.value), end=' ')

            print("\n", end='')
        print("\n")


    def init_everything(self, puzzle):
        board = self.generate_board(self.puzzle)
        self.init_constraint_neighbors(board)
        self.init_legal_values(board)
        queue = self.queue_all_cells(board)
        cell = queue.pop()
        return (board, queue, cell)


    def forward_check(self, cell):
        for neighbor in cell.neighbors:
            if neighbor.given:
                continue

            if neighbor.legal_count() == 1 and neighbor.legal_values[cell.value]:
                return False
        
        for neighbor in cell.neighbors:
            if neighbor.value == 0:
                neighbor.legal_values[cell.value] = False
        
        return True


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




    def queue_all_cells(self, board):
        queue = Heap()
        
        for i in range(9):
            for j in range(9):
                cell = board[i][j]

                if cell.value == 0:
                    queue.push_without_sift(cell)
        
        queue.heapify()
        return queue

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

    def next_larger_legal_value(self):
        for i in range(self.value + 1, 10):
            if self.legal_values[i]:
                return i
        
        return -1

    def open_all_legal_values(self):
        self.legal_values = [None] # make a one-indexed list.

        for i in range(9):
            self.legal_values.append(True)
    
    def to_str(self):
        return str(self.x) + " " + str(self.y)






















"""
    NOTE it's a min heap
"""
class Heap(object):
    def __init__(self):
        self.list = []
        self.order = 0

    def peek(self):
        return self.list[0][2]

    def push_without_sift(self, cell):
        self.list.append((cell.legal_count(), self.order, cell))
        self.order += 1

    def pop(self):
        return heapq.heappop(self.list)[2]

    def size(self):
        return len(self.list)
    
    def heapify(self):
        heapq.heapify(self.list)



















































































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
