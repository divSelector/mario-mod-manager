import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QVBoxLayout, QHBoxLayout, QFormLayout)
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess

class Worker(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.output_signal.emit(output.strip())
        
        stderr = process.stderr.read()
        if stderr:
            self.output_signal.emit(stderr.strip())

class MarioModManagerGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Mario Mod Manager')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Form layout for query options
        form_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.type_input = QLineEdit()
        self.author_input = QLineEdit()
        self.rating_over_input = QLineEdit()
        self.rating_under_input = QLineEdit()
        self.exits_over_input = QLineEdit()
        self.exits_under_input = QLineEdit()
        self.downloads_over_input = QLineEdit()
        self.downloads_under_input = QLineEdit()
        self.date_after_input = QLineEdit()
        self.date_before_input = QLineEdit()
        self.featured_input = QLineEdit()
        self.demo_input = QLineEdit()

        form_layout.addRow('Title', self.title_input)
        form_layout.addRow('Type', self.type_input)
        form_layout.addRow('Author', self.author_input)
        form_layout.addRow('Rating Over', self.rating_over_input)
        form_layout.addRow('Rating Under', self.rating_under_input)
        form_layout.addRow('Exits Over', self.exits_over_input)
        form_layout.addRow('Exits Under', self.exits_under_input)
        form_layout.addRow('Downloads Over', self.downloads_over_input)
        form_layout.addRow('Downloads Under', self.downloads_under_input)
        form_layout.addRow('Date After', self.date_after_input)
        form_layout.addRow('Date Before', self.date_before_input)
        form_layout.addRow('Featured', self.featured_input)
        form_layout.addRow('Demo', self.demo_input)

        layout.addLayout(form_layout)

        # Buttons for actions
        self.scrape_button = QPushButton('Scrape', self)
        self.scrape_button.clicked.connect(self.scrape)
        layout.addWidget(self.scrape_button)

        self.random_button = QPushButton('Random Game', self)
        self.random_button.clicked.connect(self.random_game)
        layout.addWidget(self.random_button)

        self.id_label = QLabel('Game ID:', self)
        self.id_input = QLineEdit(self)
        self.id_button = QPushButton('Select by ID', self)
        self.id_button.clicked.connect(self.select_by_id)

        id_layout = QHBoxLayout()
        id_layout.addWidget(self.id_label)
        id_layout.addWidget(self.id_input)
        id_layout.addWidget(self.id_button)
        layout.addLayout(id_layout)

        self.list_button = QPushButton('List Games', self)
        self.list_button.clicked.connect(self.list_games)
        layout.addWidget(self.list_button)

        # Output text area
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

    def run_command(self, command):
        self.thread = Worker(command)
        self.thread.output_signal.connect(self.update_output)
        self.thread.start()

    def update_output(self, text):
        self.output_area.append(text)

    def scrape(self):
        self.run_command(['python', 'smwcentral.py', '--scrape'])

    def random_game(self):
        self.run_command(['python', 'smwcentral.py', '--random'])

    def select_by_id(self):
        game_id = self.id_input.text()
        self.run_command(['python', 'smwcentral.py', '--id', game_id])

    def list_games(self):
        command = ['python', 'smwcentral.py', '--list']
        options = [
            ("--title", self.title_input.text()),
            ("--type", self.type_input.text()),
            ("--author", self.author_input.text()),
            ("--rating-over", self.rating_over_input.text()),
            ("--rating-under", self.rating_under_input.text()),
            ("--exits-over", self.exits_over_input.text()),
            ("--exits-under", self.exits_under_input.text()),
            ("--downloads-over", self.downloads_over_input.text()),
            ("--downloads-under", self.downloads_under_input.text()),
            ("--date-after", self.date_after_input.text()),
            ("--date-before", self.date_before_input.text()),
            ("--featured", self.featured_input.text()),
            ("--demo", self.demo_input.text())
        ]
        for option, value in options:
            if value:
                command.extend([option, value])
        self.run_command(command)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MarioModManagerGUI()
    ex.show()
    sys.exit(app.exec_())


