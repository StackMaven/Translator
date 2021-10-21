from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication

from skimage.measure import compare_ssim
from cv2 import imread,cvtColor,COLOR_BGR2GRAY

from traceback import print_exc, format_exc


IMAGE_PATH = ".\config\image.jpg"

class Translater(QThread):

    def __init__(self, window):
        self.window = window
        self.use_translate_signal = pyqtSignal(list, str, dict)
        super(Translater, self).__init__()


    def run(self) :

        # 手动翻译
        if not self.window.translateMode :
            self.translate()


    # 截图
    def image_cut(self):

        x1 = self.window.config["range"]["X1"]
        y1 = self.window.config["range"]["Y1"]
        x2 = self.window.config["range"]["X2"]
        y2 = self.window.config["range"]["Y2"]

        screen = QApplication.primaryScreen()
        pix = screen.grabWindow(QApplication.desktop().winId(), x1, y1, x2-x1, y2-y1)
        pix.save(IMAGE_PATH)


    # 判断图片相似度
    def compare_image(self, imageA, imageB):

        grayA = cvtColor(imageA, COLOR_BGR2GRAY)
        grayB = cvtColor(imageB, COLOR_BGR2GRAY)

        (score, diff) = compare_ssim(grayA, grayB, full=True)
        score = float(score)

        return score


    def translate(self) :

        score = 0
        # 跳过图片判断
        if self.window.first_sign :
            self.image_cut()
            self.window.first_sign = False
        else :
            try :
                # 判断两张图片的相似度
                imageA = imread(IMAGE_PATH)
                self.image_cut()
                imageB = imread(IMAGE_PATH)
                score = self.compare_image(imageA, imageB)
            except :
                print_exc()
                self.window.logger.error(format_exc())

        # 如果相似度过高则不检测
        if score > self.window.config["imageSimilarity"] :
            return

