from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

import ui.login
import ui.translation
import ui.filter
import ui.range
import ui.settin
import ui.register
import threading
import utils
from utils import http
import utils.screen_rate
from utils import MessageBox


class DangoTranslator() :

    def __init__(self) :

        # 从配置文件获取配置信息
        self.config = utils.openConfig()


    # 登录
    def login(self) :

        if not self.Login.login() :
            return

        self.config["user"] = self.Login.user
        self.config["password"] = self.Login.password

        # 从云端获取配置信息
        self.config = utils.getSettin(self.config, self.logger)
        self.config = utils.loginDangoOCR(self.config, self.logger)
        utils.saveConfig(self.config)

        # 翻译界面
        self.Translation = ui.translation.Translation(self.config, self.logger)
        # 设置界面
        self.Settin = ui.settin.Settin(self.config, self.logger, self.Translation)
        # 屏蔽词界面
        self.Filter = ui.filter.Filter(self.Translation)
        # 范围框界面
        self.Range = ui.range.Range(self.config["range"]['X1'],
                                    self.config["range"]['Y1'],
                                    self.config["range"]['X2'],
                                    self.config["range"]['Y2'],
                                    self.config["screenScaleRate"],
                                    self.Translation)
        self.Translation.range_window = self.Range

        self.Login.close()
        self.Translation.show()

        # 翻译界面设置页面按键信号
        self.Translation.settinButton.clicked.connect(self.clickSettin)

        # 翻译界面按下退出键
        self.Translation.quitButton.clicked.connect(self.Range.close)
        self.Translation.quitButton.clicked.connect(self.Translation.quit)

        # 翻译界面屏蔽词按键信号
        self.Translation.filterWordButton.clicked.connect(self.clickFilter)

        # 翻译界面选择范围键信号
        self.Translation.rangeButton.clicked.connect(self.chooseRange)

        # 翻译界面充电按钮信号
        self.Translation.batteryButton.clicked.connect(self.clickBattery)

        # 范围快捷键
        self.Translation.range_hotkey_sign.connect(self.chooseRange)

        # 检查邮箱
        #self.checkEmail()


    # 按下充电键后做的事情
    def clickBattery(self) :

        # 如果处于自动模式下则暂停
        if self.Translation.translateMode:
            self.Translation.stop_sign = True

        self.Settin.config = self.Translation.config
        self.Translation.unregisterHotKey()
        self.Translation.close()
        self.Range.close()
        self.Settin.tabWidget.setCurrentIndex(4)
        self.Settin.show()


    # 按下屏蔽词键后做的事情
    def clickFilter(self) :

        # 如果处于自动模式下则暂停
        if self.Translation.translateMode :
            self.Translation.stop_sign = True

        self.Filter.refreshTable()
        self.Filter.show()


    # 按下设置键后做的事情
    def clickSettin(self) :

        # 如果处于自动模式下则暂停
        if self.Translation.translateMode :
            self.Translation.stop_sign = True

        self.Settin.config = self.Translation.config
        self.Translation.unregisterHotKey()
        self.Translation.close()
        self.Range.close()
        self.Settin.show()


    # 进入范围框选
    def chooseRange(self) :

        # 如果处于自动模式下则暂停
        if self.Translation.translateMode :
            self.Translation.stop_sign = True

        self.WScreenShot = ui.range.WScreenShot(self.Translation, self.Range)
        self.WScreenShot.show()
        self.Translation.show()


    # 点击注册
    def clickRegister(self) :

        self.Login.hide()
        self.Register.setWindowTitle("注册")
        self.Register.password_text.setPlaceholderText("请输入密码:")
        self.Register.register_button.clicked.connect(self.Register.register)
        self.Register.show()


    # 点击修改密码
    def clickForgetPassword(self) :

        self.Login.hide()
        self.Register.setWindowTitle("修改密码")
        self.Register.password_text.setPlaceholderText("请输入新密码:")
        self.Register.register_button.clicked.connect(self.Register.modifyPassword)
        self.Register.show()


    # 检查邮箱
    def checkEmail(self) :

        url = self.config["dictInfo"]["dango_check_email"]
        body = {
            "User": self.config["user"]
        }
        # 请求注册服务器
        res, err = http.post(url, body)
        if err:
            self.logger.error(err)
            MessageBox("绑定邮箱失败", err)
            return

        if res.get("Message", "") == "未绑定邮箱":
            MessageBox("邮箱绑定检查",
                       "检测到您未绑定邮箱, 请先完成邮箱绑定\n"
                       "邮箱绑定有以下好处:\n"
                       "1. 忘记密码时用于修改密码;\n"
                       "2. 购买在线OCR时作为接收购买成功的凭证;     ")
            self.Register.user_text.setText(self.config["user"])
            self.Register.password_text.setText(self.config["password"])
            self.Register.user_text.setEnabled(False)
            self.Register.password_text.setEnabled(False)
            self.Register.show()


    def main(self) :

        # 记录日志
        self.logger = utils.setLog()

        # 获取屏幕分辨率
        self.config = utils.screen_rate.getScreenRate(self.config)

        # 自适应高分辨率
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        app = QApplication(sys.argv)

        # 检查字体
        utils.checkFont(self.logger)

        # 登录界面
        self.Login = ui.login.Login(self.config, self.logger)
        self.Login.show()
        self.Login.login_button.clicked.connect(self.login)

        # 注册页面
        self.Register = ui.register.Register(self.Login)
        self.Login.register_button.clicked.connect(self.clickRegister)
        self.Login.forget_password_button.clicked.connect(self.clickForgetPassword)

        app.exit(app.exec_())


if __name__ == "__main__" :

    app = DangoTranslator()
    app.main()