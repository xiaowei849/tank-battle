# -*- coding: utf-8 -*-
import codecs
import random
import time
import pygame

# 窗口宽度
SCREEN_WEIGHT = 1200
# 窗口高度
SCREEN_HEIGHT = 800
# 要创建的敌方坦克数量
Enemy_Tank_count = 20


# 主逻辑类
class MainGame:
    # 游戏主窗口
    window = None
    # 创建我方坦克
    MY_TANK = None
    # 初始化分数
    mark = 0
    # 存储敌方坦克
    Enemy_Tank_list = []
    # 存储我方坦克子弹的列表image
    Bullet_list = []
    # 存储敌方坦克子弹的列表
    E_Bullet_list = []
    # 爆炸效果列表
    Explode_list = []
    # 墙壁列表
    Wall_list = []
    # 道具列表
    Food_list = []
    # 创建老家
    MY_HOME = None
    # 胜利状态
    IS_WIN = None

    def __init__(self):
        pass

    # 开始游戏
    def start_game(self):
        # 初始化展示窗口
        pygame.display.init()
        # 创建展示窗口
        MainGame.window = pygame.display.set_mode((SCREEN_WEIGHT, SCREEN_HEIGHT))
        # 创建我方坦克
        MainGame.MY_TANK = MyTank(SCREEN_WEIGHT / 2 + 70, SCREEN_HEIGHT - 46)
        # 创建老家
        MainGame.MY_HOME = Home(SCREEN_WEIGHT / 2 - 48, SCREEN_HEIGHT - 48)
        # 创建音乐对象，调用音乐播放的方法
        music = Music('resource/music/start.wav')
        music.play()
        # 创建敌方坦克
        self.creat_empty_tank()
        # 创建墙壁
        self.creat_wall()
        # 创建道具
        self.creat_food()
        # 设置游戏标题
        pygame.display.set_caption('坦克大战1990')
        # 持续刷新窗口
        while True:
            # 创建窗口颜色
            MainGame.window.fill(pygame.Color(0, 0, 0))
            # 持续获取事件
            self.get_event()
            # 把小画布粘贴到窗口中
            MainGame.window.blit(self.get_text_surface(
                '敌方剩余坦克：%d辆 分数：%d 老家护甲值：%d 我方坦克护甲值：%d' %
                (len(MainGame.Enemy_Tank_list), self.mark,
                 MainGame.MY_HOME.hp if MainGame.MY_HOME and MainGame.MY_HOME.live else 0,
                 MainGame.MY_TANK.hp if MainGame.MY_TANK and MainGame.MY_TANK.live else 0), 30), (10, 10))
            # 加载墙壁到窗口中
            self.blit_wall()
            # 将道具加载到窗口中
            self.blit_food()
            # 将我方坦克加载到窗口中
            if MainGame.MY_TANK and MainGame.MY_TANK.live:
                MainGame.MY_TANK.display_tank()
            # 将我方老家加载到窗口中
            if MainGame.MY_HOME and MainGame.MY_HOME.live:
                MainGame.MY_HOME.display_home()
            # 游戏状态改变时退出循环
            if self.IS_WIN is not None:
                # 记录分数
                self.change_txt()
                break
            self.blit_empty_tank()
            # 根据坦克的开关状态调用坦克的移动方法
            if MainGame.MY_TANK and not MainGame.MY_TANK.stop:
                MainGame.MY_TANK.move()
                MainGame.MY_TANK.hit_wall()
                MainGame.MY_TANK.hit_enemy_tank()
                MainGame.MY_TANK.hit_food()
            # 调用渲染我方坦克子弹列表的方法
            self.blit_bullet()
            # 调用渲染敌方坦克子弹列表的方法
            self.blit_e_bullet()
            # 调用展示爆炸效果的方法
            self.display_explodes()
            time.sleep(0.02)
            # 持续刷新窗口
            pygame.display.update()
        while True:
            # 创建窗口
            MainGame.window.fill(pygame.Color(0, 0, 0))
            # 根据游戏状态展示胜利或者失败
            if MainGame.IS_WIN is True:
                MainGame.STATUS = Over(SCREEN_WEIGHT / 2 - 454, 0, 'win')
            else:
                MainGame.STATUS = Over(SCREEN_WEIGHT / 2 - 272, 200, 'defeat')
            MainGame.STATUS.over_game()
            # 展示分数，排行榜，重新开始，退出
            MainGame.window.blit(self.get_text_surface('分数：%d' % self.mark, 50), (50, 620))
            MainGame.window.blit(self.get_text_surface('排行榜', 50), (430, 620))
            MainGame.window.blit(self.get_text_surface('重新开始', 50), (700, 620))
            MainGame.window.blit(self.get_text_surface('退出', 50), (1000, 620))
            # 初始化点击排行榜状态
            is_click = False
            # 持续获取事件
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    self.quit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    left, top = pygame.mouse.get_pos()
                    if 430 < left < 580 and 620 < top < 670:
                        print('点击排行榜')
                        # 如果点击了排行榜则标记为True
                        is_click = True
                    elif 700 <= left <= 900 and 620 <= top <= 670:
                        print('点击重新开始')
                        # 初始化游戏并重新开始游戏
                        self.init_game()
                        self.start_game()
                    elif 1000 <= left <= 1100 and 620 <= top <= 670:
                        self.quit_game()

            # 如果点击了排行榜就退出循环
            if is_click:
                break
            # 刷新窗口
            pygame.display.update()
        while True:
            # 创建窗口
            MainGame.window.fill(pygame.Color(0, 0, 0))
            # 运行排行榜方法
            self.game_ranking()
            # 持续获取事件
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    self.quit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    left, top = pygame.mouse.get_pos()
                    if 200 <= left <= 400 and 700 <= top <= 750:
                        print('点击重新开始')
                        # 初始化游戏并重新开始游戏
                        self.init_game()
                        self.start_game()
                    elif 850 <= left <= 950 and 700 <= top <= 750:
                        # 退出游戏
                        self.quit_game()
            # 刷新窗口
            pygame.display.update()

    # 获取程序所有的事件
    def get_event(self):
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN:
                # 只有坦克存活才能移动和发射子弹
                if MainGame.MY_TANK and MainGame.MY_TANK.live:
                    if event.key == pygame.K_LEFT:
                        print('坦克向左移动')
                        # 修改坦克方向为向左，并修改坦克的状态
                        MainGame.MY_TANK.direction = 'L'
                        MainGame.MY_TANK.stop = False
                    elif event.key == pygame.K_RIGHT:
                        print('坦克向右移动')
                        # 修改坦克方向为向右，并修改坦克的状态
                        MainGame.MY_TANK.direction = 'R'
                        MainGame.MY_TANK.stop = False
                    elif event.key == pygame.K_UP:
                        print('坦克向上移动')
                        # 修改坦克方向为向上，并修改坦克的状态
                        MainGame.MY_TANK.direction = 'U'
                        MainGame.MY_TANK.stop = False
                    elif event.key == pygame.K_DOWN:
                        print('坦克向下移动')
                        # 修改坦克方向为向下，并修改坦克的状态
                        MainGame.MY_TANK.direction = 'D'
                        MainGame.MY_TANK.stop = False
                    elif event.key == pygame.K_SPACE:
                        # 限制最多同时存在5颗子弹
                        if len(MainGame.Bullet_list) < 5:
                            print('发射子弹')
                            # 产生一颗子弹
                            m = Bullet(MainGame.MY_TANK)
                            # 将子弹加入到子弹列表
                            MainGame.Bullet_list.append(m)
                            # 加载音乐并播放
                            music = Music('resource/music/fire.wav')
                            music.play()
                        else:
                            print('最多同时发射5颗子弹')
            elif event.type == pygame.KEYUP and self.IS_WIN is None:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    if MainGame.MY_TANK and MainGame.MY_TANK.live:
                        # 修改坦克的状态
                        MainGame.MY_TANK.stop = True

    # 创建敌方坦克
    def creat_empty_tank(self):
        for i in range(Enemy_Tank_count):
            left = random.randint(1, 15)
            top = random.randint(1, 3)
            speed = random.randint(3, 6)
            e_tank = EmptyTank(left * 80, top * 50, speed)
            MainGame.Enemy_Tank_list.append(e_tank)

    # 将坦克加入到窗口中
    def blit_empty_tank(self):
        for e_tank in MainGame.Enemy_Tank_list:
            if e_tank.live:
                e_tank.display_tank()
                # 坦克的移动方法
                e_tank.rand_move()
                # 调用敌方坦克和墙壁的碰撞方法
                e_tank.hit_wall()
                # 调用敌方坦克和我方坦克的碰撞方法
                e_tank.hit_my_tank()
                # 我方坦克子弹与敌方坦克的碰撞
                e_tank.hit_enemy_tank()
                # 调用敌方坦克和道具的碰撞方法
                e_tank.hit_food()
                # 调用敌方坦克的射击方法
                e_bullet = e_tank.shot()
                # 当子弹不为空时把子弹加入到敌方子弹列表中
                if e_bullet:
                    MainGame.E_Bullet_list.append(e_bullet)
            else:
                MainGame.Enemy_Tank_list.remove(e_tank)
                if len(MainGame.Enemy_Tank_list) == 0:
                    MainGame.IS_WIN = True

    # 创建墙壁的方法
    def creat_wall(self):
        # 循环随机生成墙壁
        for m in range(3):
            for i in range(10):
                ran_list = []
                ran = random.randint(1, 9)
                if ran not in ran_list:
                    ran_list.append(ran_list)
                    wall = Wall(125 * ran, 200 + m * 120)
                    MainGame.Wall_list.append(wall)
        # 生成一排墙壁
        for i in range(20):
            wall = Wall(150 + 50 * i, 550)
            MainGame.Wall_list.append(wall)
        # 在家的周围生成墙壁
        MainGame.Wall_list.append(Wall(SCREEN_WEIGHT / 2 - 50 * 2, SCREEN_HEIGHT - 50))
        MainGame.Wall_list.append(Wall(SCREEN_WEIGHT / 2 - 50 * 2, SCREEN_HEIGHT - 50 * 2))
        MainGame.Wall_list.append(Wall(SCREEN_WEIGHT / 2 - 50, SCREEN_HEIGHT - 50 * 2))
        MainGame.Wall_list.append(Wall(SCREEN_WEIGHT / 2, SCREEN_HEIGHT - 50 * 2))
        MainGame.Wall_list.append(Wall(SCREEN_WEIGHT / 2, SCREEN_HEIGHT - 50))

    # 将墙壁加入到窗口中
    def blit_wall(self):
        for wall in MainGame.Wall_list:
            if wall.live > 0:
                wall.display_wall()
            else:
                MainGame.Wall_list.remove(wall)

    # 创建道具
    def creat_food(self):
        lists = [50, 90, 130, 170]
        MainGame.Food_list.append(Food(random.choice(lists), SCREEN_HEIGHT - random.choice(lists)))
        MainGame.Food_list.append(Food(SCREEN_WEIGHT - random.choice(lists), SCREEN_HEIGHT - random.choice(lists)))

    # 将道具加入到窗口中
    def blit_food(self):
        for food in MainGame.Food_list:
            if food.live:
                food.display_food()
            else:
                MainGame.Food_list.remove(food)

    # 将我方子弹加入到窗口中
    def blit_bullet(self):
        for bullet in MainGame.Bullet_list:
            # 子弹存在时绘制出来，否则移除子弹
            if bullet.live:
                bullet.display_bullet()
                # 子弹的移动方法
                bullet.move()
                # 我方坦克子弹和敌方坦克子弹之间的碰撞
                bullet.hit_bullet()
                # 我方坦克子弹和墙壁之间的碰撞
                bullet.hit_wall()
                # 我方坦克子弹和家之间的碰撞
                bullet.hit_home()
            else:
                # 子弹消失则移除子弹
                MainGame.Bullet_list.remove(bullet)

    # 将敌方子弹加入到窗口中
    def blit_e_bullet(self):
        for e_bullet in MainGame.E_Bullet_list:
            # 子弹存在时绘制出来，否则移除子弹
            if e_bullet.live:
                e_bullet.display_bullet()
                # 子弹的移动方法
                e_bullet.move()
                if MainGame.MY_TANK and MainGame.MY_TANK.live:
                    e_bullet.hit_my_tank()
                # 敌方子弹和墙壁之间的碰撞
                e_bullet.hit_wall()
                # 敌方子弹和家之间的碰撞
                e_bullet.hit_home()
            else:
                # 子弹消失则移除子弹
                MainGame.E_Bullet_list.remove(e_bullet)

    # 展示爆炸效果列表
    def display_explodes(self):
        for explode in MainGame.Explode_list:
            if explode.live:
                explode.display_explode()
            else:
                MainGame.Explode_list.remove(explode)

    # 文字描绘
    def get_text_surface(self, text, size):
        # 初始化字体模块
        pygame.font.init()
        # 设置字体和大小
        font = pygame.font.SysFont('SimHei', size)
        # 内容绘制
        text_surface = font.render(text, True, pygame.Color(200, 50, 50))
        return text_surface

    # 排行榜方法
    def game_ranking(self):
        # 显示排行榜，重新开始，退出
        MainGame.window.blit(self.get_text_surface('排行榜', 50), (500, 50))
        MainGame.window.blit(self.get_text_surface('重新开始', 50), (200, 700))
        MainGame.window.blit(self.get_text_surface('退出', 50), (850, 700))
        # 获取排行文档内容
        mark_list = self.read_txt(r'resource/score.txt')[0].split('#')
        # 展示排行榜分数
        for i in range(len(mark_list)):
            MainGame.window.blit(self.get_text_surface('第%d名:' % (i + 1), 40), (450, 100 + (i + 1) * 50))
            MainGame.window.blit(self.get_text_surface(mark_list[i], 40), (600, 100 + (i + 1) * 50))

    # 读取排行榜
    def read_txt(self, path):
        with open(path, 'r', encoding='utf8') as f:
            lines = f.readlines()
        return lines

    # 写入排行榜
    def write_txt(self, content, strim, path):
        f = codecs.open(path, strim, 'utf8')
        f.write(str(content))
        f.close()

    # 修改排行榜
    def change_txt(self):
        # 读取排行榜分数，以#分割成列表
        mark_list = self.read_txt(r'resource/score.txt')[0].split('#')
        # 把列表元素转换成int
        mark_list = list(map(int, mark_list))
        # 判断成绩是否在排行榜中，不在的话在列表追加
        if self.mark not in mark_list:
            mark_list.append(self.mark)
        # 列表的分类和倒序
        mark_list.sort()
        mark_list.reverse()
        # 如果列表数少于等于10，则循环数等于列表数，否则循环数为10
        num = len(mark_list) if len(mark_list) <= 10 else 10
        for i in range(num):
            # 列表第一个采用重写，并加上#号
            if i == 0:
                self.write_txt(str(mark_list[i]) + '#', 'w', r'resource/score.txt')
            # 追加带#号
            elif 0 < i < num - 1:
                self.write_txt(str(mark_list[i]) + '#', 'a', r'resource/score.txt')
            # 最后一次循环不带#追加
            else:
                self.write_txt(str(mark_list[i]), 'a', r'resource/score.txt')

    # 初始化游戏，重新开始时调用
    def init_game(self):
        MainGame.MY_TANK = None
        MainGame.mark = 0
        MainGame.Enemy_Tank_list = []
        MainGame.Bullet_list = []
        MainGame.E_Bullet_list = []
        MainGame.Explode_list = []
        MainGame.Wall_list = []
        MainGame.Food_list = []
        MainGame.MY_HOME = None
        MainGame.IS_WIN = None

    # 退出游戏
    def quit_game(self):
        print('退出游戏')
        exit()


# 基础类，用于继承精灵类
class Base(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


# 坦克父类
class Tank(Base):
    def __init__(self, left, top):
        super().__init__()
        # 初始方向
        self.direction = 'U'
        # 不同方向展示不同的图片
        self.images = {
            'U': pygame.image.load('resource/images/hero/hero1U.gif'),
            'D': pygame.image.load('resource/images/hero/hero1D.gif'),
            'L': pygame.image.load('resource/images/hero/hero1L.gif'),
            'R': pygame.image.load('resource/images/hero/hero1R.gif'),
        }
        self.image = self.images[self.direction]
        # 坦克所在的区域Rect
        self.rect = self.image.get_rect()
        # 指定坦克初始位置
        self.rect.left = left
        self.rect.top = top
        # 坦克移动速度
        self.speed = 5
        # 初始化护甲值
        self.hp = 1
        # 坦克初始状态
        self.live = True
        # 坦克的移动开关
        self.stop = True
        # 记录坦克移动前的坐标(用于还原坐标)
        self.old_left = self.rect.left
        self.old_top = self.rect.top

    # 坦克移动
    def move(self):
        self.old_left = self.rect.left
        self.old_top = self.rect.top
        if self.direction == 'L' and self.rect.left > 0:
            self.rect.left -= self.speed
        elif self.direction == 'R' and self.rect.left + self.rect.width < SCREEN_WEIGHT:
            self.rect.left += self.speed
        elif self.direction == 'U' and self.rect.top > 50:
            self.rect.top -= self.speed
        elif self.direction == 'D' and self.rect.top + self.rect.height < SCREEN_HEIGHT:
            self.rect.top += self.speed

    # 还原坐标方法
    def stay(self):
        self.rect.left = self.old_left
        self.rect.top = self.old_top

    # 射击方法
    def shot(self):
        return Bullet(self)

    # 展示坦克(将坦克绘制到窗口中)
    def display_tank(self):
        # 重新加载坦克图片
        self.image = self.images[self.direction]
        # 将坦克加入到图片中
        MainGame.window.blit(self.image, self.rect)

    # 坦克与墙壁碰撞的方法
    def hit_wall(self):
        for wall in MainGame.Wall_list:
            if pygame.sprite.collide_circle(self, wall):
                self.stay()

    # 坦克碰到道具的方法
    def hit_food(self):
        for food in MainGame.Food_list:
            if pygame.sprite.collide_circle(self, food):
                self.hp += 1
                food.live = False


# 我方坦克类（继承父类）
class MyTank(Tank):
    def __init__(self, left, top):
        super().__init__(left, top)

    # 主动碰撞敌方坦克的方法
    def hit_enemy_tank(self):
        for e_tank in MainGame.Enemy_Tank_list:
            if pygame.sprite.collide_circle(self, e_tank):
                self.stay()


# 敌方坦克类（继承父类）
class EmptyTank(Tank):
    def __init__(self, left, top, speed):
        super().__init__(left, top)
        self.images = {
            'U': pygame.image.load('resource/images/enemy/enemy1U.gif'),
            'D': pygame.image.load('resource/images/enemy/enemy1D.gif'),
            'L': pygame.image.load('resource/images/enemy/enemy1L.gif'),
            'R': pygame.image.load('resource/images/enemy/enemy1R.gif'),
        }
        # 随机敌方坦克方向
        self.direction = random.choice(['U', 'D', 'L', 'R'])
        self.image = self.images[self.direction]
        # 坦克所在的区域Rect
        self.rect = self.image.get_rect()
        # 指定坦克初始位置
        self.rect.left = left
        self.rect.top = top
        # 坦克移动速度
        self.speed = speed
        # 增加步数属性，控制坦克随机移动
        self.step = 50

    # 随机移动
    def rand_move(self):
        if self.step <= 0:
            self.direction = random.choice(['U', 'D', 'L', 'R'])
            self.step = 50
        else:
            self.move()
            self.step -= 1

    # 重写敌方坦克射击方法
    def shot(self):
        num = random.randint(1, 1000)
        if num <= 25:
            return Bullet(self)

    # 我方坦克子弹与敌方坦克的碰撞
    def hit_enemy_tank(self):
        for bullet in MainGame.Bullet_list:
            if pygame.sprite.collide_circle(bullet, self):
                self.hp -= 1
                # 改变我方坦克子弹的状态
                bullet.live = False
                if self.hp <= 0:
                    # 分数加100
                    MainGame.mark += 100
                    # 产生一个爆炸效果
                    explode = Explode(self)
                    # 把爆炸效果加入到爆炸效果列表中
                    MainGame.Explode_list.append(explode)
                    # 改变敌方坦克的状态
                    self.live = False

    # 敌方坦克碰撞我方坦克的方法
    def hit_my_tank(self):
        if MainGame.MY_TANK and MainGame.MY_TANK.live:
            if pygame.sprite.collide_circle(self, MainGame.MY_TANK):
                self.stay()


# 子弹类
class Bullet(Base):
    def __init__(self, tank):
        # 图片
        super().__init__()
        self.image = pygame.image.load('resource/images/bullet/tankmissile.gif')
        # 位置
        self.rect = self.image.get_rect()
        # 速度
        self.speed = 7
        # 子弹是否碰撞
        self.live = True
        # 方向（坦克方向）
        self.direction = tank.direction
        if self.direction == 'U':
            self.rect.left = tank.rect.left + tank.rect.width / 2 - self.rect.width / 2
            self.rect.top = tank.rect.top - self.rect.height
        elif self.direction == 'D':
            self.rect.left = tank.rect.left + tank.rect.width / 2 - self.rect.width / 2
            self.rect.top = tank.rect.top + tank.rect.height
        elif self.direction == 'L':
            self.rect.left = tank.rect.left - self.rect.width
            self.rect.top = tank.rect.top + tank.rect.height / 2 - self.rect.height / 2
        elif self.direction == 'R':
            self.rect.left = tank.rect.left + tank.rect.width
            self.rect.top = tank.rect.top + tank.rect.height / 2 - self.rect.height / 2

    # 子弹移动
    def move(self):
        if self.direction == 'U':
            if self.rect.top > 50:
                self.rect.top -= self.speed
            else:
                self.live = False
        elif self.direction == 'D':
            if self.rect.top < SCREEN_HEIGHT - self.rect.height:
                self.rect.top += self.speed
            else:
                self.live = False
        elif self.direction == 'L':
            if self.rect.left > 0:
                self.rect.left -= self.speed
            else:
                self.live = False
        elif self.direction == 'R':
            if self.rect.left < SCREEN_WEIGHT - self.rect.width:
                self.rect.right += self.speed
            else:
                self.live = False

    # 展示子弹
    def display_bullet(self):
        MainGame.window.blit(self.image, self.rect)

    # 敌方子弹和我方坦克之间的碰撞
    def hit_my_tank(self):
        if pygame.sprite.collide_circle(self, MainGame.MY_TANK):
            # 改变我方坦克和敌方坦克子弹的状态
            self.live = False
            MainGame.MY_TANK.hp -= 1
            if MainGame.MY_TANK.hp <= 0:
                explode = Explode(MainGame.MY_TANK)
                # 把爆炸效果加入到爆炸效果列表中
                MainGame.Explode_list.append(explode)
                MainGame.MY_TANK.live = False
                MainGame.IS_WIN = False

    # 我方坦克子弹和敌方坦克子弹的碰撞
    def hit_bullet(self):
        for e_bullet in MainGame.E_Bullet_list:
            if pygame.sprite.collide_circle(e_bullet, self):
                # 改变我方坦克子弹和敌方坦克子弹的状态
                self.live = False
                e_bullet.live = False

    # 子弹和墙碰撞
    def hit_wall(self):
        for wall in MainGame.Wall_list:
            if pygame.sprite.collide_circle(wall, self):
                # 产生一个爆炸效果
                explode = Explode(wall)
                # 把爆炸效果加入到爆炸效果列表中
                MainGame.Explode_list.append(explode)
                # 改变我方坦克子弹和敌方坦克的状态
                self.live = False
                wall.hp -= 1
                if wall.hp <= 0:
                    wall.live = False

    # 子弹和老家碰撞
    def hit_home(self):
        if MainGame.MY_HOME and MainGame.MY_HOME.live:
            if pygame.sprite.collide_circle(MainGame.MY_HOME, self):
                # 改变子弹和家的状态
                self.live = False
                MainGame.MY_HOME.hp -= 1
                # 每射击一次，家的生命值减1，修改家的状态
                if MainGame.MY_HOME.hp <= 0:
                    # 产生一个爆炸效果
                    explode = Explode(MainGame.MY_HOME)
                    # 把爆炸效果加入到爆炸效果列表中
                    MainGame.Explode_list.append(explode)
                    MainGame.MY_HOME.live = False
                    MainGame.IS_WIN = False


# 爆炸效果类
class Explode:
    def __init__(self, tank):
        self.rect = tank.rect
        self.step = 0
        self.images = [
            pygame.image.load('resource/images/boom/blast1.gif'),
            pygame.image.load('resource/images/boom/blast2.gif'),
            pygame.image.load('resource/images/boom/blast3.gif'),
            pygame.image.load('resource/images/boom/blast4.gif'),
            pygame.image.load('resource/images/boom/blast5.gif'),
            pygame.image.load('resource/images/boom/blast6.gif'),
            pygame.image.load('resource/images/boom/blast7.gif'),
            pygame.image.load('resource/images/boom/blast8.gif'),
        ]
        self.image = self.images[self.step]
        self.live = True

    # 展示爆炸效果
    def display_explode(self):
        if self.step < len(self.images):
            MainGame.window.blit(self.image, self.rect)
            self.image = self.images[self.step]
            self.step += 1
        else:
            self.step = 0
            self.live = False


# 墙壁类
class Wall(Base):
    def __init__(self, left, top):
        super().__init__()
        self.image = pygame.image.load('resource/images/walls/2.png')
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        # 是否显示墙壁
        self.live = True
        # 护甲值
        self.hp = 3

    # 展示墙壁
    def display_wall(self):
        MainGame.window.blit(self.image, self.rect)


# 老家类
class Home(Base):
    def __init__(self, left, top):
        super().__init__()
        # 导入老家图片
        self.image = pygame.image.load('resource/images/walls/5.png')
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        # 是否展示老家
        self.live = True
        # 老家的生命值设置为2
        self.hp = 2

    # 展示老家
    def display_home(self):
        MainGame.window.blit(self.image, self.rect)


# 道具类
class Food(Base):
    def __init__(self, left, top):
        super().__init__()
        # 导入道具图片
        self.image = pygame.image.load('resource/images/food/food_protect.png')
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        # 是否展示道具
        self.live = True

    # 显示道具
    def display_food(self):
        MainGame.window.blit(self.image, self.rect)


# 音乐类
class Music:
    def __init__(self, filename):
        self.filename = filename
        # 初始化混合器
        pygame.mixer.init()
        # 加载音乐
        pygame.mixer.music.load(self.filename)

    # 播放音乐
    def play(self):
        pygame.mixer.music.play()


# 游戏结束类
class Over:
    def __init__(self, left, top, show):
        self.images = {
            'win': pygame.image.load('resource/images/over/win.png'),
            'defeat': pygame.image.load('resource/images/over/defeat.png')
        }
        self.choice = show
        self.image = self.images[self.choice]
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top

    # 游戏胜利方法
    def over_game(self):
        MainGame.window.blit(self.image, self.rect)


MainGame().start_game()
