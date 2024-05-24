# main.py
import sys
from PyQt5.QtWidgets import QApplication
from app.task_manager import TaskManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())
