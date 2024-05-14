import configparser
from operations import operations as op

class game:
    """游戏类"""

    def __init__(self, name ) :
        """初始化，读取ini中的设置"""
        self.name = name
        con = configparser.ConfigParser()
        con.read('settings.ini', encoding='utf-8')
        dic = dict(con.items(name))
        self.logoPath = dic.get('logo')
        self.startPicPath = dic.get('start')

    # @staticmethod
    def start(self, startTime=120):
        """开始游戏的方法，点击游戏图标并等待启动"""
        op.click( op.fullPath(self.logoPath) )                          #点击logo打开游戏
        op.click( op.fullPath(self.startPicPath), wait=startTime)       #点击游戏中的开始游戏按钮，需要等待游戏启动完成

    

        
    