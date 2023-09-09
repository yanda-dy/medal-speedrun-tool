from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLCDNumber, QTableWidget, QTableWidgetItem, QTabWidget
from datetime import datetime
from utils import boot_status, map_start
from models import Score


class Stopwatch(QMainWindow):
    def __init__(self):
        super().__init__()
        self.status = "boot"
        self.start_time = None
        self.medal_count = 0
        self.play_count = 0

        self.setWindowTitle("Medal Speedrun Tool")
        screen = self.screen().availableGeometry()
        self.setFixedSize(screen.width() * 0.5, screen.height() * 0.4)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.start_button = QPushButton("Launch osu! and StreamCompanion to start", self)
        self.start_button.clicked.connect(self.start_stopwatch)

        self.digital_clock = DigitalClock(stopwatch=self)
        self.digital_clock.setFixedHeight(self.height() * 0.25)

        self.tab_widget = QTabWidget(self)
        self.tab1 = QTableWidget(self)
        self.tab1.setColumnCount(2)
        self.tab1.setHorizontalHeaderLabels(["Medal name", "Time achieved"])
        self.tab1.setColumnWidth(0, self.width() * 0.75)
        self.tab1.setColumnWidth(1, self.width() * 0.15)
        self.tab2 = QTableWidget(self)
        self.tab2.setColumnCount(3)
        self.tab2.setHorizontalHeaderLabels(["Map", "Statistics", "Time"])
        self.tab2.setColumnWidth(0, self.width() * 0.4)
        self.tab2.setColumnWidth(1, self.width() * 0.35)
        self.tab2.setColumnWidth(2, self.width() * 0.15)
        self.tab_widget.addTab(self.tab1, "Medals")
        self.tab_widget.addTab(self.tab2, "Plays")

        self.layout.addWidget(self.digital_clock)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.tab_widget)

    @Slot()
    def start_stopwatch(self):
        if self.status == "init":
            self.start_button.setText("Stopwatch will start automatically...")
            self.status = "wait"
        elif self.status == "wait":
            self.status = "init"
            self.start_button.setText("Start")
        elif self.status == "running":
            self.start_time = None
            self.status = "reset"
            self.start_button.setText("Reset")
        elif self.status == "reset":
            self.status = "init"
            self.tab1.setRowCount(0)
            self.tab2.setRowCount(0)
            self.medal_count = 0
            self.play_count = 0
            self.start_button.setText("Start")
    
    def add_medal(self, medal_name: str, time_achieved: datetime):
        if not self.start_time: return
        self.medal_count += 1
        medal_name_item = QTableWidgetItem(medal_name)
        time_achieved_item = QTableWidgetItem(str(time_achieved - self.start_time))
        medal_name_item.setFlags(Qt.ItemIsEnabled)
        time_achieved_item.setFlags(Qt.ItemIsEnabled)
        
        self.tab1.setRowCount(self.medal_count)
        self.tab1.setItem(self.medal_count - 1, 0, medal_name_item)
        self.tab1.setItem(self.medal_count - 1, 1, time_achieved_item)

    def add_play(self, score: Score):
        if not self.start_time: return
        self.play_count += 1
        grades = {
            0: "XH",
            1: "SH",
            2: "X",
            3: "S",
            4: "A",
            5: "B",
            6: "C",
            7: "D"
        }
        if not score.passed: grade_str = "F"
        else: grade_str = grades[score.statistics.grade]
        map_item = QTableWidgetItem(f"{score.beatmap.map_name} [{score.beatmap.diff_name}] ({score.beatmap.mstars}*, {score.settings.mods_int})")
        statistics_item = QTableWidgetItem(f"{grade_str} {score.statistics.score} ({score.statistics.accuracy:.2f}%) {score.statistics.max_combo}/{score.beatmap.max_combo}x {score.statistics.count_300}/{score.statistics.count_100}/{score.statistics.count_50}/{score.statistics.count_miss}")
        submit_time_item = QTableWidgetItem(str(score.submit_time - self.start_time))
        map_item.setFlags(Qt.ItemIsEnabled)
        statistics_item.setFlags(Qt.ItemIsEnabled)
        submit_time_item.setFlags(Qt.ItemIsEnabled)
        
        self.tab2.setRowCount(self.play_count)
        self.tab2.setItem(self.play_count - 1, 0, map_item)
        self.tab2.setItem(self.play_count - 1, 1, statistics_item)
        self.tab2.setItem(self.play_count - 1, 2, submit_time_item)


class DigitalClock(QLCDNumber):
    def __init__(self, parent=None, stopwatch=None):
        super().__init__(parent)
        self.stopwatch = stopwatch
        self.setSegmentStyle(QLCDNumber.Filled)
        self.setDigitCount(10)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_time)
        self.timer.start(10)

        self.show_time()

    @Slot()
    def show_time(self):
        if not self.stopwatch or self.stopwatch.status == "init":
            self.display("0:00:00.00")
        elif self.stopwatch.status == "boot":
            self.display("0:00:00.00")
            if boot_status():
                self.stopwatch.status = "init"
                self.stopwatch.start_button.setText("Start")
        elif self.stopwatch.status == "wait":
            if map_start():
                self.stopwatch.status = "running"
                self.stopwatch.start_time = datetime.now()
                self.stopwatch.start_button.setText("Stop")
        elif self.stopwatch.status == "running":
            elapsed_time = datetime.now() - self.stopwatch.start_time
            text = str(elapsed_time)[:-4]
            self.display(text)
