import sys
from PyQt6.QtCore import (QDate, QObject, Qt, QTimer,  # Qt is for alignment
                          pyqtSignal)
from PyQt6.QtGui import QColor, QPixmap, QPalette, QIcon
from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow, QFrame,
                             QMessageBox, QPushButton, QSplashScreen, QSplitter, QSizePolicy,
                             QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QTabWidget)


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        # self.setBackgroundRole(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight)
        self.setStyleSheet(
            """
            QWidget{
                color:white;
                font:12px bold;
                font-weight:bold;
                border-radius: 1px;
                height: 11px;
            }
            """
        )

        self.minimize=QPushButton(self)
        self.minimize.setIcon(QIcon('assets/min.png'))

        self.maximize=QPushButton(self)
        self.maximize.setIcon(QIcon('assets/max.png'))

        close=QPushButton(self)
        close.setIcon(QIcon('assets/close.png'))

        self.minimize.setMinimumHeight(10)
        close.setMinimumHeight(10)
        self.maximize.setMinimumHeight(10)

        label=QLabel(self)
        label.setText("MLS Data Sorter")
        
        hbox=QHBoxLayout(self)
        hbox.addWidget(label)
        hbox.addWidget(self.minimize)
        hbox.addWidget(self.maximize)
        hbox.addWidget(close)
        hbox.insertStretch(1,500)
        hbox.setSpacing(0)
        #self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.MinimumExpanding
        )
        self.maxNormal=False
        close.clicked.connect(self.close)
        self.minimize.clicked.connect(self.showSmall)
        self.maximize.clicked.connect(self.showMaxRestore)

    def showSmall(self):
        self.box.showMinimized()

    def showMaxRestore(self):
        if(self.maxNormal):
            self.box.showNormal()
            self.maxNormal= False
            self.maximize.setIcon(QIcon('img/max.png'))
            print('1')
        else:
            self.box.showMaximized()
            self.maxNormal=  True
            print('2')
            self.maximize.setIcon(QIcon('img/max2.png'))

    def close(self):
        self.box.close()

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            self.box.moving = True; self.box.offset = event.pos()

    def mouseMoveEvent(self,event):
        if self.box.moving: self.box.move(event.globalPos()-box.offset)


class Frame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_mouse_down= False
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
        """
            QFrame{
                Background:  #D700D7;
                color:white;
                font:13px ;
                font-weight:bold;
                }
            """
        )
        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint))
        self.setMouseTracking(True)
        self.m_titleBar = TitleBar(self)
        self.m_content = QWidget(self)

        vbox=QVBoxLayout(self)
        vbox.addWidget(self.m_titleBar)
        vbox.setMargin(0)
        vbox.setSpacing(0)

        layout=QtGui.QVBoxLayout(self)
        layout.addWidget(self.m_content)
        layout.setMargin(5)
        layout.setSpacing(0)

        vbox.addLayout(layout)
        # Allows you to access the content area of the frame
        # where widgets and layouts can be added

    def contentWidget(self):
        return self.m_content

    def titleBar(self):
        return self.m_titleBar

    def mousePressEvent(self,event):
        self.m_old_pos = event.pos()
        self.m_mouse_down = event.button()== Qt.LeftButton

    def mouseMoveEvent(self,event):
        x=event.x()
        y=event.y()

    def mouseReleaseEvent(self,event):
        m_mouse_down=False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    box = Frame()
    box.move(60,60)
    l=QVBoxLayout(box.contentWidget())
    l.setMargin(0)
    edit=QLabel("hai")
    l.addWidget(edit)
    box.show()
    app.exec_()