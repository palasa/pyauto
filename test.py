import time
import pyautogui as pag
from operations import operations as op
from logger import logger

# time.sleep(2)

# pag.locateAllOnScreen
# x, y = pag.locateCenterOnScreen('./pics/dljj/smallYellowConfirm.png', confidence=0.8, minSearchTime=3)
# pag.moveTo(x , y , 0.5)
# pag.click( clicks=3, interval=1)

x, y  = pag.locateCenterOnScreen( op.fullPath("dljj/guildTeam.png"), minSearchTime=3 )

pag.moveTo(x, y+600, 0.5) 

    

