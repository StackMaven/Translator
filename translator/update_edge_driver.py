from selenium import webdriver
from traceback import format_exc
import re
import zipfile
import os
import utils.http

EDGE_DRIVER_PATH = "./config/tools/msedgedriver.exe"
DRIVER_DIR_PATH = "./config/tools"
DRIVER_ZIP_NAME = "edgedriver_win64.zip"


# 获取浏览器版本号
def checkEdgeVersion(object) :

    EDGE = {
        "browserName": "MicrosoftEdge",
        "platform": "WINDOWS",
        "ms:edgeOptions": {
            'extensions': [],
            'args': [
                '--headless',
            ]}
    }
    try:
        driver = webdriver.Edge(executable_path=EDGE_DRIVER_PATH,
                                service_log_path="nul",
                                capabilities=EDGE)
        driver.close()
        driver.quit()
        object.edge_driver_finish = 1
    except Exception as err :
        regex = re.findall("\d+\.\d+\.\d+\.\d+", str(err))
        if regex :
            return regex[0]
        else :
            object.edge_driver_finish = 2


# 下载引擎文件
def downloadDriver(driver_version, object) :

    url = "https://msedgedriver.azureedge.net/{}/edgedriver_win64.zip".format(driver_version)
    if not utils.http.downloadFile(url, DRIVER_ZIP_NAME, object.logger) :
        object.edge_driver_finish = 2
        return

    # 解压压缩包
    try :
        zip_file = zipfile.ZipFile(DRIVER_ZIP_NAME)
        zip_list = zip_file.namelist()
        for f in zip_list :
            if f != "msedgedriver.exe" :
                continue
            zip_file.extract(f, DRIVER_DIR_PATH)
        zip_file.close()
        # 删除压缩包
        os.remove(DRIVER_ZIP_NAME)
        object.edge_driver_finish = 1
    except Exception :
        object.logger.error(format_exc())
        object.edge_driver_finish = 2


# 校验Edge浏览器引擎文件
def updateEdgeDriver(object) :

    # 获取浏览器版本
    driver_version = checkEdgeVersion(object)
    if not driver_version :
        return

    # 下载引擎文件
    downloadDriver(driver_version, object)