from PyQt5 import QtWidgets

class ErrorDialog(QtWidgets.QMessageBox):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setIcon(QtWidgets.QMessageBox.Critical)
        self.setText("Error")
        self.setInformativeText(message)
        self.setWindowTitle("Error Dialog")
        self.addButton(QtWidgets.QMessageBox.Ok)


def error_dialog_run(str) :
    # 创建ErrorDialog对象
    error_dialog = ErrorDialog(str)

    # 显示对话框
    error_dialog.exec()