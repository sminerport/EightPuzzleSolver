import sys
import random
import time
from simpleai.search import astar, SearchProblem
from PyQt5 import QtWidgets, QtGui, QtCore

GOAL_STATE = [['1', '2', '3'],
              ['4', '5', '6'],
              ['7', '8', '*']]

GOAL_POSITIONS = {
    '1': (0, 0), '2': (0, 1), '3': (0, 2),
    '4': (1, 0), '5': (1, 1), '6': (1, 2),
    '7': (2, 0), '8': (2, 1), '*': (2, 2)
}

class EightPuzzle(SearchProblem):
    def __init__(self, initial_state):
        self.initial_state = initial_state
        super().__init__(initial_state=self.state_to_tuple(initial_state))

    def actions(self, state):
        empty_row, empty_col = self.find_position(state, '*')
        actions = []

        moves = {'Up': (empty_row - 1, empty_col),
                 'Down': (empty_row + 1, empty_col),
                 'Left': (empty_row, empty_col - 1),
                 'Right': (empty_row, empty_col + 1)}

        for action, (row, col) in moves.items():
            if 0 <= row <= 2 and 0 <= col <= 2:
                actions.append(action)

        return actions

    def result(self, state, action):
        state = [list(row) for row in state]
        empty_row, empty_col = self.find_position(state, '*')

        if action == 'Up':
            target_row, target_col = empty_row - 1, empty_col
        elif action == 'Down':
            target_row, target_col = empty_row + 1, empty_col
        elif action == 'Left':
            target_row, target_col = empty_row, empty_col - 1
        elif action == 'Right':
            target_row, target_col = empty_row, empty_col + 1

        state[empty_row][empty_col], state[target_row][target_col] = state[target_row][target_col], state[empty_row][empty_col]
        return tuple(tuple(row) for row in state)

    def is_goal(self, state):
        return state == self.state_to_tuple(GOAL_STATE)

    def heuristic(self, state):
        distance = 0
        for row in range(3):
            for col in range(3):
                value = state[row][col]
                if value != '*':
                    goal_row, goal_col = GOAL_POSITIONS[value]
                    distance += abs(row - goal_row) + abs(col - goal_col)
        return distance

    @staticmethod
    def state_to_tuple(state):
        return tuple(tuple(row) for row in state)

    @staticmethod
    def find_position(state, element):
        for row_idx, row in enumerate(state):
            for col_idx, value in enumerate(row):
                if value == element:
                    return row_idx, col_idx
        return None

    @staticmethod
    def is_solvable(state):
        flattened = [num for row in state for num in row if num != '*']
        inversions = 0
        for i in range(len(flattened)):
            for j in range(i + 1, len(flattened)):
                if flattened[i] > flattened[j]:
                    inversions += 1
        return inversions % 2 == 0

    @staticmethod
    def generate_random_state():
        numbers = ['1','2','3','4','5','6','7','8','*']
        while True:
            random.shuffle(numbers)
            state = [numbers[:3], numbers[3:6], numbers[6:]]
            if EightPuzzle.is_solvable(state):
                return state

class PuzzleGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.puzzle = EightPuzzle(EightPuzzle.generate_random_state())
        self.update_ui()
        self.timer = QtCore.QTimer(self)  # Timer for updating time display
        self.timer.timeout.connect(self.update_timer)
        self.start_time = 0
        self.elapsed_time = 0

    def init_ui(self):
        button_size = 140  # Size of each tile button
        button_spacing = 10  # Spacing between buttons
        margin = 20  # Additional margin for the layout

        # Create the grid layout for the puzzle buttons
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setSpacing(button_spacing)
        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        for row in range(3):
            for col in range(3):
                button = QtWidgets.QPushButton('')
                button.setFixedSize(button_size, button_size)
                button.setFont(QtGui.QFont('Arial', 48))
                button.clicked.connect(self.make_move)
                self.grid_layout.addWidget(button, row, col)
                self.buttons[row][col] = button

        # Create Solve and Shuffle buttons
        self.solve_button = QtWidgets.QPushButton('Solve')
        self.solve_button.setFont(QtGui.QFont('Arial', 20))
        self.solve_button.setFixedSize(200, 50)
        self.solve_button.clicked.connect(self.solve_puzzle)

        self.shuffle_button = QtWidgets.QPushButton('Shuffle')
        self.shuffle_button.setFont(QtGui.QFont('Arial', 20))
        self.shuffle_button.setFixedSize(200, 50)
        self.shuffle_button.clicked.connect(self.shuffle_puzzle)

        # Status label to display solving time
        self.status_label = QtWidgets.QLabel('')
        self.status_label.setFont(QtGui.QFont('Arial', 16))
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)

        # Layout for Solve and Shuffle buttons
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.solve_button)
        self.hbox.addWidget(self.shuffle_button)

        # Main vertical layout
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.grid_layout)
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.status_label)

        self.setLayout(self.vbox)
        self.setWindowTitle('Eight Puzzle Solver')

        # Calculate total window size
        total_width = 3 * button_size + 2 * button_spacing + margin
        total_height = 3 * button_size + 2 * button_spacing + 100 + margin  # 100 for buttons and label

        # Set fixed window size
        self.setFixedSize(total_width, total_height)
        self.show()

    def update_ui(self):
        for row in range(3):
            for col in range(3):
                value = self.puzzle.initial_state[row][col]
                button = self.buttons[row][col]
                if value == '*':
                    button.setText('')
                    button.setStyleSheet('background-color: lightgray')
                else:
                    button.setText(value)
                    button.setStyleSheet('background-color: white')

    def make_move(self):
        sender = self.sender()
        row, col = self.get_button_position(sender)
        empty_row, empty_col = self.puzzle.find_position(self.puzzle.initial_state, '*')

        if (abs(row - empty_row) == 1 and col == empty_col) or (abs(col - empty_col) == 1 and row == empty_row):
            new_state = [list(r) for r in self.puzzle.initial_state]
            new_state[empty_row][empty_col], new_state[row][col] = new_state[row][col], new_state[empty_row][empty_col]
            self.puzzle.initial_state = new_state
            self.update_ui()

            if self.puzzle.is_goal(self.puzzle.state_to_tuple(self.puzzle.initial_state)):
                self.status_label.setText('Congratulations! Puzzle solved.')

    def get_button_position(self, button):
        for row in range(3):
            for col in range(3):
                if self.buttons[row][col] == button:
                    return row, col
        return None

    def solve_puzzle(self):
        self.status_label.setText('Using A* algorithm to find the best route...')
        QtWidgets.QApplication.processEvents()  # Force UI update

        problem = EightPuzzle(self.puzzle.initial_state)
        result = astar(problem)

        if result:
            self.status_label.setText('Solving the puzzle...')
            QtWidgets.QApplication.processEvents()  # Update the UI

            self.start_time = time.time()
            self.timer.start(10)  # Update the timer every 10 milliseconds

            self.move_index = 0
            self.result_path = result.path()[1:]
            self.piece_timer = QtCore.QTimer(self)
            self.piece_timer.timeout.connect(self.move_pieces)
            self.piece_timer.start(1000)  # Move pieces every second

        else:
            self.status_label.setText('This puzzle cannot be solved.')

    def update_timer(self):
        self.elapsed_time = time.time() - self.start_time
        self.status_label.setText(f'Solving... Time elapsed: {self.elapsed_time:.2f} seconds')

    def move_pieces(self):
        if self.move_index < len(self.result_path):
            _, state = self.result_path[self.move_index]
            self.highlight_move(state)
            self.puzzle.initial_state = [list(row) for row in state]
            self.update_ui()
            self.move_index += 1
        else:
            self.piece_timer.stop()
            self.timer.stop()
            self.status_label.setText(f'Puzzle solved in {self.elapsed_time:.2f} seconds!')

    def shuffle_puzzle(self):
        self.puzzle.initial_state = EightPuzzle.generate_random_state()
        self.update_ui()
        self.status_label.setText('')
        self.timer.stop()
        if hasattr(self, 'piece_timer'):
            self.piece_timer.stop()

    def highlight_move(self, new_state):
        for row in range(3):
            for col in range(3):
                old_value = self.puzzle.initial_state[row][col]
                new_value = new_state[row][col]
                button = self.buttons[row][col]
                if old_value != new_value:
                    button.setStyleSheet('background-color: yellow')  # Highlight moving piece
                else:
                    if new_value == '*':
                        button.setStyleSheet('background-color: lightgray')
                    else:
                        button.setStyleSheet('background-color: white')

def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = PuzzleGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
