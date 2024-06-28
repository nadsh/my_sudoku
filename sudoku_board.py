import pygame
pygame.init()

import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import sudoku_generator

class SudokuCell(QtWidgets.QLineEdit):
    def __init__(self, value, row, col, parent=None):
        super(SudokuCell, self).__init__(parent)
        self.setFixedSize(40, 40)
        font = self.font()
        font.setPointSize(16)
        self.setFont(font)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.row = row
        self.col = col
        if value != 0:
            self.setText(str(value))
            self.setReadOnly(True)
        
            palette = self.palette()
            palette.setColor(QtGui.QPalette.Text, QtCore.Qt.darkGray)
            self.setPalette(palette)

    def paintEvent(self, event):
        super(SudokuCell, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen()
        pen.setWidth(2)
        pen.setColor(QtCore.Qt.black)
        painter.setPen(pen)

        rect = self.rect()
        if 'r2' in self.objectName() or 'r5' in self.objectName():  # Thick bottom border
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        if 'c2' in self.objectName() or 'c5' in self.objectName():  # Thick right border
            painter.drawLine(rect.topRight(), rect.bottomRight())

    def keyPressEvent(self, event):
        
        self.parent().parent().parent().check_solution()
        key = event.key()
        
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            self.move_focus(-1, 0)
        elif key == QtCore.Qt.Key_Right:
            self.move_focus(1, 0)
        elif key == QtCore.Qt.Key_Up:
            self.move_focus(0, -1)
        elif key == QtCore.Qt.Key_Down:
            self.move_focus(0, 1)
        else:
            if not self.isReadOnly():
                text_of_the_event = event.text()
                if text_of_the_event.isdigit() and '1' <= text_of_the_event <= '9':
                    if self.is_valid_input(text_of_the_event):
                        self.setText(text_of_the_event)
                    else:
                        self.play_error_sound()
                elif text_of_the_event == '\x08':  # Backspace key
                    self.setText('')
            event.ignore()

    def move_focus(self, dx, dy):
        next_row = self.row + dy
        next_col = self.col + dx
        if 0 <= next_row < 9 and 0 <= next_col < 9:
            next_widget = self.parent().layout().itemAtPosition(next_row, next_col).widget()
            if next_widget:
                next_widget.setFocus()
    
    def is_valid_input(self, number):
        # Check row
        for col in range(9):
            if col != self.col:
                cell = self.parent().layout().itemAtPosition(self.row, col).widget()
                if cell and cell.text() == number:
                    cell.flash_background_color()
                    return False
        
        # Check column
        for row in range(9):
            if row != self.row:
                cell = self.parent().layout().itemAtPosition(row, self.col).widget()
                if cell and cell.text() == number:
                    cell.flash_background_color()
                    return False
                
        block_start_row = (self.row // 3) * 3
        block_start_col = (self.col // 3) * 3
        for r in range(block_start_row, block_start_row + 3):
            for c in range(block_start_col, block_start_col + 3):
                if r != self.row and c != self.col:
                    cell = self.parent().layout().itemAtPosition(r, c).widget()
                    if cell and cell.text() == number:
                        cell.flash_background_color()
                        return False
        
        return True

    def flash_background_color(self):
        original_palette = self.palette()
        flash_palette = QtGui.QPalette(original_palette)
        flash_palette.setColor(QtGui.QPalette.Base, QtCore.Qt.red)
        self.setPalette(flash_palette)

        def restore_later():
            original_palette.setColor(QtGui.QPalette.Base, QtCore.Qt.white)
            self.setPalette(original_palette)

        # Schedule a reset of the background color after a short delay
        QtCore.QTimer.singleShot(200, restore_later)

    def play_error_sound(self):
        if self.parent().parent().parent().play_sound:
            pygame.mixer.music.load(r'C:\Windows\Media\Windows Error.wav')
            pygame.mixer.music.play()
            pygame.event.wait()

    def focusInEvent(self, event):
        self.setStyleSheet('background-color: lightblue;')
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setStyleSheet('background-color: white;')
        super().focusOutEvent(event)

class SudokuGrid(QtWidgets.QWidget):
    def __init__(self, grid, parent=None):
        super(SudokuGrid, self).__init__(parent)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        self.cells = []

        for row in range(9):
            for col in range(9):
                cell = SudokuCell(grid[row][col], row, col, self)
                cell.setObjectName(f'r{row}c{col}')
                layout.addWidget(cell, row, col)
                self.cells.append(cell)


    def is_sudoku_solved(self):
        # Check rows and columns
        for i in range(9):
            row_values = set()
            col_values = set()
            for j in range(9):
                row_value = self.cells[i * 9 + j].text()
                col_value = self.cells[j * 9 + i].text()
                if row_value == '' or row_value in row_values or col_value == '' or col_value in col_values:
                    return False
                row_values.add(row_value)
                col_values.add(col_value)
        
        # Check 3x3 blocks
        for block_row in range(0, 9, 3):
            for block_col in range(0, 9, 3):
                block_values = set()
                for i in range(3):
                    for j in range(3):
                        cell_value = self.cells[(block_row + i) * 9 + block_col + j].text()
                        if cell_value == '' or cell_value in block_values:
                            return False
                        block_values.add(cell_value)
        
        return True

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, grid, parent=None):
        super(MainWindow, self).__init__(parent)
        self.play_sound = True
        
        self.setWindowTitle('Sudoku')
        
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        self.mute_button = QtWidgets.QPushButton('Mute Sounds')
        self.mute_button.clicked.connect(self.toggle_sound)
        layout.addWidget(self.mute_button)

        self.status_label = QtWidgets.QLabel()
        self.status_label.setText('Sudoku is not solved yet.')
        layout.addWidget(self.status_label)

        self.sudoku_grid = SudokuGrid(grid, self)
        layout.addWidget(self.sudoku_grid)

    def toggle_sound(self):
        self.play_sound = not self.play_sound
        if self.play_sound:
            self.mute_button.setText('Mute Sounds')
        else:
            self.mute_button.setText('Unmute Sounds')

    def check_solution(self):
        if self.sudoku_grid.is_sudoku_solved():
            self.status_label.setText('Sudoku Solved! Congratulations!')
        else:
            self.status_label.setText('Sudoku is not solved yet.')

def main():
    sudoku_grid = sudoku_generator.get_new_sudoku_as_list()

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow(sudoku_grid)
    main_window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
