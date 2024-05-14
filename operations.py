import time
import pyautogui as pag

class operations:

    """操作类，进行鼠标键盘的一系列操作"""

    @staticmethod
    def click(picPath, wait=120):
        """
        点击方法
        @params
            picPath: 要点击的图片路径
        """
        x, y = pag.locateCenterOnScreen( picPath, confidence=0.8, minSearchTime=wait )
        pag.moveTo( x, y, 1 )
        pag.click()

    def moveAndClick(x,y,wait=1):
        """在同一界面中相对位置移动鼠标并点击按钮"""
        pag.moveRel(x,y,0.5)
        pag.click()
        time.sleep(wait)

    @staticmethod
    def type(message, alphabetTime=0.1):        
        pag.typewrite(message, interval=alphabetTime)

    @staticmethod
    def fullPath(path):
        return './pics/' + path
    
    @staticmethod
    def center(box):
        """获取一个BOX的中心点"""
        left, top, width, height = box
        x = left + int(width/2)
        y = top + int(height/2)
        return [x, y]