# app/task_manager.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem, \
    QLineEdit, QTextEdit, QMessageBox, QLabel, QComboBox, QDateTimeEdit, QInputDialog, QHBoxLayout, QFormLayout
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QTimer
from plyer import notification
import datetime


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task Manager")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('media/icons/app_icon.png'))
        self.categories = ["Работа", "Личное", "Покупки", "Другое"]
        self.task_list = QTreeWidget()
        self.task_list.setHeaderLabels(["Задача", "Описание", "Категория", "Крайни срок", "Приоритет"])

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Введите название задачи")
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Введите описание задачи")
        self.category_input = QComboBox()
        self.category_input.addItems(self.categories)
        self.priority_input = QComboBox()
        self.priority_input.addItems(["Низкий", "Средний", "Высокий"])
        self.deadline_input = QDateTimeEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDateTime(datetime.datetime.now())
        self.add_button = QPushButton("Добавить задачу")
        self.add_button.setObjectName("add_button")
        self.remove_button = QPushButton("Удалить задачу")
        self.remove_button.setObjectName("remove_button")
        self.add_subtask_button = QPushButton("Добавить подзадачу")
        self.add_subtask_button.setObjectName("add_subtask_button")
        self.filter_input = QComboBox()
        self.filter_input.addItems(["Все"] + self.categories)
        self.filter_input.currentIndexChanged.connect(self.filter_tasks)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск задач...")
        self.search_input.textChanged.connect(self.search_tasks)

        # Кнопка для показа/скрытия дополнительных элементов
        self.toggle_button = QPushButton("Дополнительные параметры")
        self.toggle_button.setCheckable(True)
        self.toggle_button.toggled.connect(self.toggle_elements)

        # Основные элементы
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Название задачи:"))
        main_layout.addWidget(self.task_input)
        main_layout.addWidget(QLabel("Описание:"))
        main_layout.addWidget(self.description_input)
        main_layout.addWidget(self.add_button)

        # Дополнительные элементы
        self.additional_elements = QWidget()
        additional_layout = QFormLayout()
        additional_layout.addRow(QLabel("Категория:"), self.category_input)
        additional_layout.addRow(QLabel("Приоритет:"), self.priority_input)
        additional_layout.addRow(QLabel("Дедлайн:"), self.deadline_input)
        additional_layout.addWidget(self.remove_button)
        additional_layout.addWidget(self.add_subtask_button)
        additional_layout.addRow(QLabel("Фильтр по категории:"), self.filter_input)
        additional_layout.addRow(QLabel("Поиск:"), self.search_input)
        self.additional_elements.setLayout(additional_layout)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Задачи:"))
        layout.addWidget(self.task_list)
        layout.addWidget(self.toggle_button)
        layout.addLayout(main_layout)
        layout.addWidget(self.additional_elements)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.add_button.clicked.connect(self.add_task)
        self.remove_button.clicked.connect(self.remove_task)
        self.add_subtask_button.clicked.connect(self.add_subtask)

        # Check deadlines every minute
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_deadlines)
        self.timer.start(60000)  # 60 seconds

        # Load styles
        self.load_styles()

        # Hide additional elements by default
        self.additional_elements.setVisible(False)

    def load_styles(self):
        with open('styles/style.qss', 'r') as f:
            self.setStyleSheet(f.read())

    def toggle_elements(self, checked):
        self.additional_elements.setVisible(checked)

    def add_task(self):
        task = self.task_input.text()
        description = self.description_input.toPlainText()
        category = self.category_input.currentText()
        priority = self.priority_input.currentText()
        deadline = self.deadline_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        if task:
            task_item = QTreeWidgetItem([task, description, category, deadline, priority])
            if priority == "Высокий":
                task_item.setBackground(0, QColor("#FF0000"))
                task_item.setBackground(1, QColor("#FFCCCC"))
            elif priority == "Средний":
                task_item.setBackground(0, QColor("#FFFF00"))
                task_item.setBackground(1, QColor("#FFFFCC"))
            else:
                task_item.setBackground(0, QColor("#00FF00"))
                task_item.setBackground(1, QColor("#CCFFCC"))
            self.task_list.addTopLevelItem(task_item)
            self.task_input.clear()
            self.description_input.clear()
        else:
            QMessageBox.warning(self, "Внимание", "Название задачи не может быть пустым!")

    def add_subtask(self):
        selected_task = self.task_list.currentItem()
        if selected_task:
            subtask, ok = QInputDialog.getText(self, "Добавить подзадачу", "Введите название подзадачи:")
            if ok and subtask:
                description = self.description_input.toPlainText()
                subtask_item = QTreeWidgetItem([subtask, description, "", "", ""])
                selected_task.addChild(subtask_item)
        else:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите задачу для добавления подзадачи!")

    def remove_task(self):
        selected_task = self.task_list.currentItem()
        if selected_task:
            index = self.task_list.indexOfTopLevelItem(selected_task)
            if index >= 0:
                self.task_list.takeTopLevelItem(index)
            else:
                parent = selected_task.parent()
                if parent:
                    parent.removeChild(selected_task)
        else:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите задачу для удаления!")

    def check_deadlines(self):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for index in range(self.task_list.topLevelItemCount()):
            item = self.task_list.topLevelItem(index)
            deadline_str = item.text(3)
            if deadline_str:
                deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
                if deadline < datetime.datetime.now():
                    task_name = item.text(0)
                    notification.notify(
                        title="Просроченная задача",
                        message=f"Задача '{task_name}' просрочена!",
                        timeout=10
                    )

    def filter_tasks(self):
        selected_category = self.filter_input.currentText()
        for index in range(self.task_list.topLevelItemCount()):
            item = self.task_list.topLevelItem(index)
            if selected_category == "Все" or selected_category in item.text(2):
                item.setHidden(False)
            else:
                item.setHidden(True)

    def search_tasks(self):
        search_text = self.search_input.text().lower()
        for i in range(self.task_list.topLevelItemCount()):
            item = self.task_list.topLevelItem(i)
            item.setHidden(search_text not in item.text(0).lower() and search_text not in item.text(1).lower())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())
