import time
from game import game
import configparser
from operations import operations as op
import pyautogui as pag
from logger import logger


class dljj(game):
    """堕落姬甲的游戏类"""

    def __init__(self, name="堕落姬甲" ):
        super().__init__(name)
        con = configparser.ConfigParser()
        con.read('settings.ini', encoding='utf-8')
        dic = dict(con.items(name))
        self.eventPicPath = dic.get('event')        
        self.closeAdButtonPath = dic.get('close_ad')
        self.leftButtomBackButtonPath = dic.get('left_bottom_back_button')
        self.addStamina = dic.get('add_stamina_title')
        self.cancelAddStamina = dic.get('cancel_add_stamina_button')
        self.everydaySignIn = dic.get('everyday_sign_in_title')
        self.yellowConfirm = dic.get('yellow_confirm_button')
        self.eliteChallenge = dic.get('elite_challenge') 
        self.boss = dic.get('boss')
        self.eliteChallenge5 = dic.get('elite_challenge_5') 
        self.max = dic.get('max')
        self.notEnoughTimes = dic.get('not_enough_times')
        self.robotStorage = dic.get('robot_storage')
        self.womenToLevel = dic.get('women_to_level')
        self.robotToLevel = dic.get('robot_to_level')
        self.leveUpButton = dic.get('level_up_button')
        self.expBigItem = dic.get('exp_big_item')
        self.monthlyCardAdsPage = dic.get('monthly_card_ads_page')
        self.robotTab = dic.get('robot_tab')
        self.homePage = dic.get('home_page')
        self.social = dic.get('social')
        self.toDoList = dic.get('to_do_list')
        self.oneKeyHavest = dic.get('one_key_havest')
        self.oneKeyBuild = dic.get('one_key_build')
        self.smallYellowConfirm = dic.get('small_yellow_confirm')
        self.guildTeam = dic.get('guild_team')
        self.send = dic.get('send')
        self.bonus = dic.get('bonus')
        self.task = dic.get('task')
        self.achivement = dic.get('achivement')
        self.everyWeek = dic.get('every_week')
        self.everyMonth = dic.get('every_month')

        logger.log('初始化完成')


    def closeAd(self):
        """关闭自动弹出的广告页"""
        try:
            """查找广告页"""
            pag.locateOnScreen( op.fullPath(self.monthlyCardAdsPage), minSearchTime=3, confidence=0.8 )
            """找到广告页，点击左下后退按钮"""
            self.clickLeftBottomBackButton()
            logger.log('关闭自动弹出的广告页')
        except:
            logger.log('未找到广告页')
            pass

    def clickYellowConfirmButton(self):
        """点击黄色确认按钮"""
        try:
            # print(op.fullPath(self.yellowConfirm))
            box = pag.locateCenterOnScreen( op.fullPath(self.yellowConfirm) )
            # print(box)
            # op.click( op.fullPath(self.yellowConfirm) )
            pag.click(box)
            logger.log('点击黄色确认按钮')
        except:
            logger.log('未找到黄色确认按钮')
            pass

    def clickLeftBottomBackButton(self):
        """点击左下后退按钮"""
        try:
            op.click( op.fullPath(self.leftButtomBackButtonPath) )
            logger.log('点击左下后退按钮')
        except:
            logger.log('未找到左下后退按钮')
            pass

    def closeEverydaySignIn(self):
        """关闭每日签到页面"""
        try:
            """查找每日签到的标题"""
            pag.locateOnScreen( op.fullPath(self.everydaySignIn), minSearchTime=3 )
            """点击签到确认按钮"""
            op.click( op.fullPath(self.closeEverydaySignIn))
            logger.log('关闭自动弹出的每日签到页面')
        except:
            logger.log('未找到每日签到页面')
            pass

    def closeBuyCard(self):
        """关闭购买月卡的广告页"""
        try:
            # 找到广告页面,关闭
            self.clickLeftBottomBackButton()
            logger.log('关闭自动弹出的购买月卡页面')
        except:
            # 找不到说明已经没有广告页面了
            logger.log('未找到购买月卡页面')
            pass

    def enterEliteChallenge(self):
        """从主界面进入到菁英挑战页面"""

        """点击活动按钮"""
        op.click( op.fullPath(self.eventPicPath) )
        logger.log('进入活动页面')
        
        """等待几秒切画面"""
        time.sleep(3)

        """移动到菁英挑战的前往上，点击"""
        op.moveAndClick(140,-220)
        logger.log('进入菁英挑战')
   
    def eliteChallengeScrollToTop(self):
        """把菁英挑战页面拉动到最上面"""
        try:
            """查找菁英挑战的标题"""
            pag.locateOnScreen( op.fullPath(self.eliteChallenge), minSearchTime=3 )
            pag.moveRel(0,-300, 0.5)
            pag.mouseDown()
            pag.moveRel(0,700,0.5)
            pag.mouseUp()
            logger.log('滚动到菁英挑战页面最上端')
        except:
            pass

    def guildScroll(self):
        """把公会远征页面往下拉"""
        
        try:  
            """先找到公会远征队的标题"""
            x, y = pag.locateCenterOnScreen( op.fullPath(self.guildTeam), minSearchTime=3 )
            """把鼠标移动到合适的位置"""
            pag.moveTo(x, y+600, 0.5)         
            pag.mouseDown()
            pag.moveRel(0,-1000,1)
            pag.mouseUp()
            logger.log('把公会远征页面往下拉')
        except:
            pass

    def enterBossPage(self):
        """从菁英挑战页面进入boss关卡"""
        try:
            """查找BOSS文字"""
            x, y = pag.locateCenterOnScreen( op.fullPath(self.boss), minSearchTime=3, confidence=0.8 )
            pag.moveTo(x+80, y-40, 0.5)
            pag.click()
            logger.log('进入boss关卡')
        except:
            logger.log('本日已刷过boss')
            pass

    def enterEliteChallenge5(self):
        """从菁英挑战页面进入菁英挑战5关卡"""
        try:
            """查找菁英挑战5文字"""
            x, y = pag.locateCenterOnScreen( op.fullPath(self.eliteChallenge5), minSearchTime=3, confidence=0.8 )
            pag.moveTo(x+80, y-40, 0.5)
            pag.click()
        except:
            pass

    def fastBattle(self):
        """使用所有剩余体力扫荡关卡,完成后回到菁英挑战页面"""

        """如果弹出体力补充页面"""
        try:
            # 查找“体力补充”标题
            pag.locateOnScreen( op.fullPath(self.addStamina), minSearchTime=3 )
            logger.log('体力不足，退出')

            # 如果找到则点击取消按钮
            op.click( op.fullPath(self.cancelAddStamina), wait=3 )
        except:
            """否则执行扫荡功能"""
            logger.log('开始执行扫荡...')
            try:
                """查找MAX文字"""
                x, y = pag.locateCenterOnScreen( op.fullPath(self.max), minSearchTime=3, confidence=0.8 )
                """移动到MAX上,点击""" 
                pag.moveTo(x, y, 0.5)
                pag.click()
                """移动到扫荡上,点击"""
                op.moveAndClick(-160,60, 3)            

                """移动到确认上,点击"""
                op.moveAndClick(0,-100)
                """点击左下后退按钮 回到菁英挑战页面"""
                self.clickLeftBottomBackButton()
            except:
                pass
            pass

       
    def doBossBattle(self):
        """进行boss扫荡"""
        logger.log('开始进行Boss扫荡')
        self.enterBossPage()
        try:             
            """次数不足"""
            x, y = pag.locateCenterOnScreen( op.fullPath(self.notEnoughTimes), minSearchTime=3, confidence=0.8 )
            """点击黄色确认按钮"""
            self.clickYellowConfirmButton()
            logger.log('剩余次数不足，退出')
        except:
            self.fastBattle()

    def doEliteChallenge5Battle(self):
        """进行菁英挑战5扫荡"""
        logger.log('开始进行菁英挑战5扫荡')
        self.enterEliteChallenge5()
        self.fastBattle()
        

    def clearStamina(self):
        """刷活动清体力，从首页开始执行，执行完毕后返回首页"""
        self.enterEliteChallenge()        

        """"把菁英挑战的页面拉到最上面"""
        self.eliteChallengeScrollToTop()

        """"先扫荡boss关"""
        self.doBossBattle()

        """扫荡菁英挑战5关卡"""
        self.doEliteChallenge5Battle() 

        """返回主界面"""
        """点击左下后退按钮 回到活动关卡"""
        self.clickLeftBottomBackButton()
        logger.log('回到活动关卡')
        """点击左下后退按钮 回到地图页面"""
        self.clickLeftBottomBackButton()
        logger.log('回到地图页面')
        """点击左下后退按钮 回到主页面"""
        self.clickLeftBottomBackButton()
        logger.log('回到主页面')

        """关闭因体力不足自动弹出的购买月卡界面"""
        self.closeBuyCard()

    def enterRobotStorage(self):
        """进入机库"""
        try:
            op.click( op.fullPath(self.robotStorage), wait=3 )
            logger.log('进入机库...')
        except:
            pass

    def enterSocial(self):
        """进入社群"""
        try:
            op.click( op.fullPath(self.social), wait=3 )
            logger.log('进入社群...')
        except:
            logger.log('未进入社群...')
            pass

    def clickToDoList(self):
        """点击左上todo列表"""
        try:
            op.click( op.fullPath(self.toDoList), wait=3 )
            logger.log('点击任务列表')
        except:
            logger.log('未进入任务列表')
            pass

    def clickOneKeyHavest(self):
        """点击一键领取"""
        try:
            op.click( op.fullPath(self.oneKeyHavest), wait=3 )
            logger.log('点击一键领取')
        except:
            logger.log('未进行一键领取')
            pass

    def clickOneKeyBuild(self):
        """点击一键编队"""
        try:
            op.click( op.fullPath(self.oneKeyBuild), wait=3 )
            logger.log('点击一键编队')
        except:
            logger.log('未进行一键编队')
            pass

    def levelUpWomen(self):
        """升级女人"""
        try:
            """点击要升级的女人"""
            op.click( op.fullPath(self.womenToLevel), wait=3 )
            logger.log('点击要升级的女人...')

            """点击升级按钮"""
            self.clickLevelUpButton()

            """点击大经验药水三次"""
            self.clickExpBigItemThreeTimes()

            """点击确认按钮"""
            self.clickYellowConfirmButton()

            """点击左下后退按钮回到女人详情页"""
            self.clickLeftBottomBackButton()

            """点击左下后退按钮回到女人列表页"""
            self.clickLeftBottomBackButton()
        except:
            pass

    def clickExpBigItemThreeTimes(self):
        """点击大经验药水三次"""
        x, y = pag.locateCenterOnScreen( op.fullPath(self.expBigItem) , confidence=0.8, minSearchTime=3)
        pag.moveTo(x , y , 0.5)
        pag.click( clicks=3, interval=1)
        logger.log("点击大经验药水三次")

    def clickLevelUpButton(self):
        """点击升级按钮"""
        op.click( op.fullPath(self.leveUpButton), wait=3 )
        logger.log('点击升级按钮...')


    def levelUpRobot(self):
        """升级机甲"""
        try:
            """点击自动型机甲标签"""
            op.click( op.fullPath(self.robotTab) , wait=3 )
            logger.log( '点击自动型机甲标签' )

            """点击要升级的机甲"""
            op.click( op.fullPath(self.robotToLevel) , wait=3 )
            logger.log( '点击要升级的机甲' )

            """点击升级按钮"""
            self.clickLevelUpButton()

            """点击大经验药水三次"""
            self.clickExpBigItemThreeTimes()

            """点击确认按钮升级"""
            self.clickYellowConfirmButton()

            """点击左下后退按钮回到机甲详情页"""
            self.clickLeftBottomBackButton()

            """点击左下后退按钮回到机甲列表页"""
            self.clickLeftBottomBackButton()

        except:
            pass

    def robotStorageLevelUp(self):
        """机库操作，升级女人和机甲,从主页开始，操作完成回到主页"""
        self.enterRobotStorage()
        self.levelUpWomen()
        self.levelUpRobot()
        """返回主页"""
        self.clickHomePage()

    def doSocialAffairs(self):
        """进行社群操作"""
        self.enterSocial()
        self.clickToDoList()
        self.clickOneKeyHavest()
        self.clickYellowConfirmButton()
        self.clickOneKeyBuild()
        self.confirmEach()
        """返回社群界面"""
        self.clickLeftBottomBackButton()
        """返回主页界面"""
        self.clickLeftBottomBackButton()

    def confirmVisiableEach(self):
        """对本可视页面中的逐一确认"""
        try:
            confirms = pag.locateAllOnScreen( op.fullPath(self.smallYellowConfirm) , confidence=0.8)
            logger.log('对本可视页面中的逐一确认')

            """第一次点击远征"""
            for confirm in confirms:
                # print( op.center(box) )
                """点击小黄色确认"""
                pag.moveTo(op.center(confirm), duration=0.5 )
                pag.click(duration=1)
                """点击弹出的大的确认派遣按钮"""
                self.clickYellowConfirmButton()
                """点击派遣成功的确认按钮"""
                self.clickYellowConfirmButton()
        except:
            logger.log('本视口中已找不到可确认的远征')
            pass

    def confirmEach(self):
        """对公会远征队逐一确认"""
        self.confirmVisiableEach()
        self.guildScroll()
        """再次对本页面中可以点击的确认逐一操作"""
        self.confirmVisiableEach()        


    def clickHomePage(self):
        """点击主页按钮"""
        try:
            op.click( op.fullPath(self.homePage), wait=3 )
            logger.log("点击主页按钮回到主页面")
        except:
            pass

    def doSendAffairs(self):
        """进行派遣操作"""
        try:
            op.click( op.fullPath(self.send), wait=3 )
            logger.log("点击派遣按钮")
        except:
            logger.log("无法找到派遣按钮")

        """进行一键派遣"""

        """返回主页"""
        self.clickLeftBottomBackButton()

    def getMainBonus(self):
        """进入领取界面"""
        try:
            op.click( op.fullPath(self.bonus), wait=3 )
            logger.log("点击奖励按钮")
        except:
            logger.log("无法找到奖励按钮")

        """领取主要界面的所有奖励"""
        self.clickOneKeyHavest()

    def getAllBonus(self):
        """领取所有奖励"""

        self.getMainBonus()

        self.getEveryDayBonus()

        self.getEveryWeekBonus()

        self.getEveryMonthBonus()

        self.getAchivementBonus()

        """后退回到主页界面"""
        self.clickLeftBottomBackButton()

    def getAchivementBonus(self):
        """进入成就界面"""
        try:
            op.click( op.fullPath(self.achivement), wait=3 )
            logger.log("点击成就按钮")
        except:
            logger.log("无法找到成就按钮")

        """领取成就奖励"""
        self.clickOneKeyHavest()

    def getEveryMonthBonus(self):
        """进入每月界面"""
        try:
            op.click( op.fullPath(self.everyMonth), wait=3 )
            logger.log("点击每月按钮")
        except:
            logger.log("无法找到每月按钮")

        """领取每月奖励"""
        self.clickOneKeyHavest()

    def getEveryWeekBonus(self):
        """进入每周界面"""
        try:
            op.click( op.fullPath(self.everyWeek), wait=3 )
            logger.log("点击每周按钮")
        except:
            logger.log("无法找到每周按钮")

        """领取每周奖励"""
        self.clickOneKeyHavest()

    def getEveryDayBonus(self):
        """进入任务界面"""
        try:
            op.click( op.fullPath(self.task), wait=3 )
            logger.log("点击任务按钮")
        except:
            logger.log("无法找到任务按钮")

        """领取每日奖励"""
        self.clickOneKeyHavest()



        