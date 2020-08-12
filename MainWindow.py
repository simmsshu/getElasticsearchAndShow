from TitleBar import *
WINDOW_QSS = "./theme.qss"
WINDOW_ICON = "./pic/Kibana.png"
WINDOW_TITLE = "测试窗口"

WINDOW_DEFAULT_WIDTH = 640
WINDOW_DEFAULT_HEIGHT = 480
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.tittle = WINDOW_TITLE
        self.InitializeWindow()
    def InitializeWindow(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT);
        self.InitializeViews()
        self.setStyleSheet(str(self.LoadStyleFromQss(WINDOW_QSS)))

    def InitializeViews(self):
        self.titleBar = TitleBar(self)
        self.client = QWidget(self)
        self.center = QWidget(self)

        self.setCentralWidget(self.center)

        self.lay = QVBoxLayout(self)
        self.center.setLayout(self.lay)

        self.lay.addWidget(self.titleBar)
        self.lay.addWidget(self.client)
        self.lay.setStretch(1, 100)
        self.lay.setSpacing(0)
        self.lay.setContentsMargins(0, 0, 0, 0)

        self.titleBar.SetIcon(QPixmap(WINDOW_ICON))
        self.titleBar.SetTitle(self.tittle);

    def LoadStyleFromQss(self, f):
        file = open(f)
        lines = file.readlines()
        file.close()
        res = ''
        for line in lines:
            res += line

        return res


if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
    pass
