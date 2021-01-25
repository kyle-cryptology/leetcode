from typing import List


def highlight(data, color: str = 'yellow') -> str:
    """
    :param data: the content to be highlighted
    :param color: the color to be highlighted
    """
    colors = {'red': 31, 'green': 32, 'yellow': 33, 'blue': 34, 'grey': 90}
    code = colors[color] if color in colors else 33
    return '\x1b[1;%dm%s\x1b[0m' % (code, str(data))

# === Paste below content to LeetCode. ===


class Solution:
    def solveSudoku(self, board: List[List[str]]) -> None:
        """
        Do not return anything, modify board in-place instead.
        """
        self.board = board
        self.candidates = [[list(range(1, 10)) for _ in range(9)]
                           for _ in range(9)]
        self.guessing = False
        self.index = 0  # The current index to put a node.
        self.queue = []  # All ensured or guessed nodes.
        self.done = [[0 for _ in range(9)] for _ in range(9)]
        # Done value: 0 for unput; 1 for pending in queue; 2 for added.
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] != '.':
                    self.add(i, j, int(board[i][j]))
        self.crosses = []
        self.execute()
        if self.index != 81:
            self.guessing = True
            self.dfs()

    def add(self, row: int, column: int, value: int):
        if self.done[row][column] == 0:
            self.done[row][column] = 1
            self.queue.append((row, column, value))
            if self.guessing:
                node = {'row': row, 'column': column, 'value': value,
                        'candidates': [], 'remove': []}
                cross = self.crosses[-1]
                cross['index'][str(row * 10 + column)] = len(cross['nodes'])
                cross['nodes'].append(node)

    def execute(self) -> bool:
        """
            Return results for putting those points in the queue.
        """
        while True:
            while (len(self.queue) != self.index):
                # Put and eliminate candidates.
                node = self.queue[self.index]
                succ = self._put(node[0], node[1], node[2])
                if not succ:
                    return False
                self.index += 1
            if self.index != 81:
                # To scan solutions.
                self.scan()
                if len(self.queue) == self.index:  # No new node found.
                    return True
            else:
                return True

    def _put(self, row: int, column: int, value: int) -> bool:
        if self.guessing and (not self.detect(row, column, value)):
            return False
        self.board[row][column] = str(value)  # Set the board.
        self.done[row][column] = 2
        node = {}
        if self.guessing:
            cross = self.crosses[-1]
            index = cross['index'][str(row * 10 + column)]
            node = cross['nodes'][index]
            cross['nodes'][index]['candidates']\
                = [c for c in self.candidates[row][column]]
        self.candidates[row][column] = []  # Clear the candidates.
        # Remove neighbor's candidates.
        neighbors = self.get_neighbors(row, column)
        for n in neighbors:
            x = n[0]
            y = n[1]
            _cans = self.candidates[x][y]
            if value in _cans:
                if self.guessing:
                    node['remove'].append((x, y))
                _cans.pop(_cans.index(value))
                # self.monitor(row, column)
                length = len(_cans)
                if length == 1:
                    self.add(x, y, _cans[0])
                elif length == 0:
                    return False
        return True

    def get_neighbors(self, row: int, column: int) -> list:
        neighbors = []
        for i in range(9):  # Remove candidates.
            if i != column and (self.done[row][i] == 0):
                neighbors.append((row, i))  # horizantal
            if i != row and (self.done[i][column] == 0):
                neighbors.append((i, column))  # vertical
        y = int(int(row / 3) * 3)  # square
        x = int(int(column / 3) * 3)
        for i in range(3):
            for j in range(3):
                if (i+y) != row and (j+x) != column\
                        and (self.done[i+y][j+x] == 0):
                    neighbors.append((i+y, j+x))
        return neighbors

    def scan(self) -> None:
        for i in range(9):
            for j in range(9):
                if self.done[i][j] == 0:
                    _cans = self.candidates[i][j]
                    neighbors = self.get_grouped_neighbors(i, j)
                    for c in _cans:  # For each candidate in a node.
                        # for n in neighbors:  # For each group of neighbors.
                        for k in range(3):
                            n = neighbors[k]
                            only = True
                            for x, y in n:  # For each neighbor.
                                if c in self.candidates[x][y]:
                                    only = False
                                    break
                            if only:
                                self.add(i, j, c)
                                return

    def get_grouped_neighbors(self, row: int, column: int) -> list:
        horizantal = []
        vertical = []
        square = []
        for i in range(9):  # Remove candidates.
            if i != column and (self.done[row][i] == 0):
                horizantal.append((row, i))  # horizantal
            if i != row and (self.done[i][column] == 0):
                vertical.append((i, column))  # vertical
        x = int(int(row / 3) * 3)  # square
        y = int(int(column / 3) * 3)
        for i in range(3):
            for j in range(3):
                if not ((i+x) == row and (j+y) == column)\
                        and (self.done[i+x][j+y] == 0):
                    square.append((i+x, j+y))
        return [horizantal, vertical, square]

    def dfs(self) -> bool:
        cross = self.choose()
        self.crosses.append(cross)
        row = cross['row']
        column = cross['column']
        while len(cross['alternative']) > 0:
            value = cross['alternative'].pop()
            self.add(row, column, value)
            exec_succ = self.execute()
            dfs_succ = False
            if exec_succ:
                if self.index == 81:
                    return True
                else:
                    dfs_succ = self.dfs()
            if dfs_succ:
                return True
            #  The execution failed and dfs failed.
            self.reverse()
        self.crosses.pop()
        return False

    def reverse(self) -> None:
        cross = self.crosses[-1]
        while len(cross['nodes']) > 0:
            node = cross['nodes'].pop()
            row = node['row']
            column = node['column']
            self.queue.pop()
            if self.done[row][column] == 2:
                value = node['value']
                for x, y in node['remove']:
                    self.candidates[x][y].append(value)
                self.board[row][column] = '.'
                self.candidates[row][column] = node['candidates']
                self.index -= 1
            self.done[row][column] = 0

    def choose(self) -> dict:
        row = column = -1
        _min = 10
        count = 30
        for i in range(9):
            for j in range(9):
                if self.done[i][j] == 0:
                    numbers = len(self.candidates[i][j])
                    if numbers < _min:
                        row = i
                        column = j
                        _min = numbers
        cross = {'row': row, 'column': column, 'index': {},
                 'alternative': [c for c in self.candidates[row][column]],
                 'nodes': []}
        return cross

    def detect(self, row: int, column: int, value: int) -> bool:
        for i in range(9):
            if i != column and self.board[row][i] != '.':
                if value == int(self.board[row][i]):
                    return False
            if i != row and self.board[i][column] != '.':
                if value == int(self.board[i][column]):
                    return False
        x = int(row / 3) * 3  # square
        y = int(column / 3) * 3
        for i in range(3):
            for j in range(3):
                if x+i != row and y+j != column \
                        and self.board[x+i][y+j] != '.':
                    if value == int(self.board[x+i][y+j]):
                        return False
        return True

    # === Paste above content to LeetCode. ===

    def print_queue(self, last_five: bool = False) -> None:
        print('%s:' % highlight('Queue'))
        x = len(self.queue) - 5 if last_five else 0
        for i in range(x, len(self.queue)):
            node = self.queue[i]
            print('  %s. x: %d, y: %d, value: %s, from: %s'
                  % (highlight('%3d' % i), node[0],
                     node[1], node[2], self.source[node[0]][node[1]]))
        print()

    def display_candidates(self, row: int, column: int) -> None:
        reds = [[True * 9] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                value = str(len(self.candidates[i][j]))
                # highligh
                matrix = ((int(row / 3) == int(i / 3)) and
                          (int(column / 3) == int(j / 3)))
                if i == row or j == column or matrix:
                    if i == row and j == column:
                        value = highlight(value, 'red')
                    else:
                        value = highlight(value, 'green')
                print('%s ' % value, end='')
            print('\t', end='')
            for j in range(9):
                value = self.board[i][j]
                if i == row and j == column:
                    value = highlight(value, 'red')
                print('%s ' % value, end='')
            print()
        value = 0 if self.board[row][column] == '.'\
            else int(self.board[row][column])
        print()

    def display(self) -> None:
        for i in range(9):
            for j in range(9):
                print(' %s' % self.board[i][j], end='')
            print()
        print()

    def compare(self, board: list) -> None:
        for i in range(9):
            for j in range(9):
                node = self.board[i][j]
                if board[i][j] == '.' and self.board[i][j] != '.':
                    node = highlight(node, 'red')
                print(' %s' % node, end='')
            print()
        print()

    def verify(self) -> bool:
        for i in range(9):
            array = []
            for j in range(9):
                if not str(j+1) in self.board[i]:
                    return False
                array.append(self.board[j][i])
            for j in range(9):
                if not str(j+1) in array:
                    return False
        for x in range(3):  # square
            for y in range(3):
                array = []
                for i in range(3):
                    for j in range(3):
                        array.append(self.board[3*x+i][3*y+j])
                for j in range(9):
                    if not str(j+1) in array:
                        return False
        return True


v = [["1", ".", ".", ".", "7", ".", ".", "3", "."],
     ["8", "3", ".", "6", ".", ".", ".", ".", "."],
     [".", ".", "2", "9", ".", ".", "6", ".", "8"],
     ["6", ".", ".", ".", ".", "4", "9", ".", "7"],
     [".", "9", ".", ".", ".", ".", ".", "5", "."],
     ["3", ".", "7", "5", ".", ".", ".", ".", "4"],
     ["2", ".", "3", ".", ".", "9", "1", ".", "."],
     [".", ".", ".", ".", ".", "2", ".", "4", "3"],
     [".", "4", ".", ".", "8", ".", ".", ".", "9"]]

w = [[".", ".", ".", "2", ".", ".", ".", "6", "3"],
     ["3", ".", ".", ".", ".", "5", "4", ".", "1"],
     [".", ".", "1", ".", ".", "3", "9", "8", "."],
     [".", ".", ".", ".", ".", ".", ".", "9", "."],
     [".", ".", ".", "5", "3", "8", ".", ".", "."],
     [".", "3", ".", ".", ".", ".", ".", ".", "."],
     [".", "2", "6", "3", ".", ".", "5", ".", "."],
     ["5", ".", "3", "7", ".", ".", ".", ".", "8"],
     ["4", "7", ".", ".", ".", "1", ".", ".", "."]]

x = [["5", "3", ".", ".", "7", ".", ".", ".", "."],
     ["6", ".", ".", "1", "9", "5", ".", ".", "."],
     [".", "9", "8", ".", ".", ".", ".", "6", "."],
     ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
     ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
     ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
     [".", "6", ".", ".", ".", ".", "2", "8", "."],
     [".", ".", ".", "4", "1", "9", ".", ".", "5"],
     [".", ".", ".", ".", "8", ".", ".", "7", "9"]]

y = [[".", ".", "9", "7", "4", "8", ".", ".", "."],
     ["7", ".", ".", ".", ".", ".", ".", ".", "."],
     [".", "2", ".", "1", ".", "9", ".", ".", "."],
     [".", ".", "7", ".", ".", ".", "2", "4", "."],
     [".", "6", "4", ".", "1", ".", "5", "9", "."],
     [".", "9", "8", ".", ".", ".", "3", ".", "."],
     [".", ".", ".", "8", ".", "3", ".", "2", "."],
     [".", ".", ".", ".", ".", ".", ".", ".", "6"],
     [".", ".", ".", "2", "7", "5", "9", ".", "."]]

z = [["5", "1", "7", "6", ".", ".", ".", "3", "4"],
     ["2", "8", "9", ".", ".", "4", ".", ".", "."],
     ["3", "4", "6", "2", ".", "5", ".", "9", "."],
     ["6", ".", "2", ".", ".", ".", ".", "1", "."],
     [".", "3", "8", ".", ".", "6", ".", "4", "7"],
     [".", ".", ".", ".", ".", ".", ".", ".", "."],
     [".", "9", ".", ".", ".", ".", ".", "7", "8"],
     ["7", ".", "3", "4", ".", ".", "5", "6", "."],
     [".", ".", ".", ".", ".", ".", ".", ".", "."]]

problems = [v, w, x, y, z]
# problems = [w]
s = Solution()
for p in problems:
    s.solveSudoku(p)
    print('Verified: %s.' % highlight(('pass' if s.verify() else 'fail')))
    print()
