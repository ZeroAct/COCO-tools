import os

from PyQt5.QtWidgets import \
    QApplication, QMainWindow, \
    QWidget, QLabel, QPushButton, QLineEdit, QFileDialog, \
    QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import \
    QDoubleValidator, QIntValidator
from PyQt5.QtCore import \
    pyqtSignal, pyqtSlot

from src.coco import COCOManager

class CocoWidget(QWidget):
    add_manager = pyqtSignal(str, COCOManager)

    def __init__(self, parent, title='', coco_mananger=None):

        super().__init__()

        self.parent = parent

        self.init_variables(coco_mananger)
        self.init_widgets(title)
        self.init_layout()

    def init_variables(self, coco_mananger=None):
        self.coco_manager = coco_mananger

    def init_widgets(self, title):

        self.title = QLabel(title)

        self.w_file_path = QLineEdit('')
        self.w_file_path.setReadOnly(True)

        self.w_load_btn = QPushButton('COCO 불러오기')
        self.w_load_btn.clicked.connect(self.load_coco_file)
        if self.coco_manager is not None:
            self.w_load_btn.setDisabled(True)

        self.w_img_num = QLabel('')
        self.w_ann_num = QLabel('')
        self.w_cat_num = QLabel('')

        double_validator = QDoubleValidator(0., 1., 2)
        self.w_split_ratio = QLineEdit('0.8')
        self.w_split_ratio.setValidator(double_validator)

        int_validator = QIntValidator()
        self.w_split_seed = QLineEdit('123')
        self.w_split_seed.setValidator(int_validator)

        self.w_split_btn = QPushButton('split')
        self.w_split_btn.clicked.connect(self.train_val_split)

        self.w_save_btn = QPushButton('Save')
        self.w_save_btn.clicked.connect(self.save)

        self.plot_nums()
    
    def init_layout(self):
        layout = QVBoxLayout()


        top_layout = QHBoxLayout()
        top_layout.addWidget(self.w_file_path)
        top_layout.addWidget(self.w_load_btn)

        mid_layout = QHBoxLayout()
        mid_layout.addWidget(QLabel(' Image num : '))
        mid_layout.addWidget(self.w_img_num)
        mid_layout.addWidget(QLabel(' Ann num : '))
        mid_layout.addWidget(self.w_ann_num)
        mid_layout.addWidget(QLabel(' Category num : '))
        mid_layout.addWidget(self.w_cat_num)

        bot_layout = QHBoxLayout()
        bot_layout.addWidget(QLabel('train ratio : '))
        bot_layout.addWidget(self.w_split_ratio)
        bot_layout.addWidget(QLabel('random seed : '))
        bot_layout.addWidget(self.w_split_seed)
        bot_layout.addWidget(self.w_split_btn)

        layout.addWidget(self.title)
        layout.addItem(top_layout)
        layout.addItem(mid_layout)
        layout.addItem(bot_layout)
        layout.addWidget(self.w_save_btn)

        self.setLayout(layout)
    
    def plot_nums(self):
        if self.coco_manager:
            img_num, ann_num, cat_num = self.coco_manager.get_nums()
            self.w_img_num.setText(str(img_num))
            self.w_ann_num.setText(str(ann_num))
            self.w_cat_num.setText(str(cat_num))

    def load_coco_file(self):
        self.coco_path, _ = QFileDialog.getOpenFileName(self, 'get coco file', './', '*.json')
        
        if len(self.coco_path) > 0:
            self.title.setText(os.path.splitext(os.path.split(self.coco_path)[-1])[0])
            self.w_file_path.setText(self.coco_path)

            self.coco_manager = COCOManager(self.coco_path)
            self.plot_nums()
    
    def train_val_split(self):
        train_ratio = float(self.w_split_ratio.text())
        random_seed = int(self.w_split_seed.text())

        train_manager, val_manager = self.coco_manager.train_val_split(train_ratio, random_seed)
        
        self.add_manager.emit(self.title.text()+f'_train_{train_ratio:.2f}', train_manager)
        self.add_manager.emit(self.title.text()+f'_val_{1-train_ratio:.2f}', val_manager)
    
    def save(self):
        if isinstance(self.coco_manager, COCOManager):
            self.coco_manager.save(os.path.join('outputs', self.title.text()+'.json'))
        

class MainWindow(QMainWindow):
    def __init__(self):

        super().__init__()

        self.init_variables()
        self.init_widgets()
        self.init_layout()

        self.setWindowTitle('coco spliter')

    def init_variables(self):
        self.coco_widgets = [CocoWidget(self)]
        self.coco_widgets[0].add_manager.connect(self.add_split)

    def init_widgets(self):
        pass
    
    def init_layout(self):

        main_widget = QWidget()

        self.coco_layout = QVBoxLayout()

        for coco_widget in self.coco_widgets:
            self.coco_layout.addWidget(coco_widget)
        
        main_widget.setLayout(self.coco_layout)
        self.setCentralWidget(main_widget)
        self.show()
    
    @pyqtSlot(str, COCOManager)
    def add_split(self, name, manager):
        coco_widget = CocoWidget(self, name, manager)
        coco_widget.add_manager.connect(self.add_split)

        self.coco_widgets.append(coco_widget)
        self.coco_layout.addWidget(coco_widget)




if __name__ == "__main__":
    app = QApplication([])
    mainwindow = MainWindow()
    app.exec_()
