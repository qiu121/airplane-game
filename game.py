from game_hud import *
from game_music import *


class Game(object):
    """游戏类"""

    def __init__(self):
        # 1. 游戏主窗口
        self.main_window = pygame.display.set_mode(SCREEN_RECT.size)
        pygame.display.set_caption("飞机大战")

        # 2. 游戏状态属性
        self.is_game_over = True  # 游戏结束标记
        self.is_pause = False  # 游戏暂停标记

        # 3. 精灵组属性
        self.all_group = pygame.sprite.Group()  # 所有精灵组
        self.enemies_group = pygame.sprite.Group()  # 敌机精灵组
        self.supplies_group = pygame.sprite.Group()  # 道具精灵组

        # 4. 创建精灵
        # 背景精灵，交替滚动
        self.all_group.add(Background(False), Background(True))

        # 指示器面板
        self.hud_panel = HUDPanel(self.all_group)

        # 创建敌机
        self.create_enemies()

        # 英雄精灵
        self.hero = Hero(self.all_group)

        # 设置面板中炸弹数量
        self.hud_panel.show_bomb(self.hero.bomb_count)

        # 创建道具
        self.create_supplies()

        # 5. 创建音乐播放器
        self.player = MusicPlayer("game_music.ogg")
        self.player.play_music()

    def create_supplies(self):
        """创建道具"""
        Supply(0, self.supplies_group, self.all_group)
        Supply(1, self.supplies_group, self.all_group)

        # 设置 30s 投放道具定时器事件
        pygame.time.set_timer(THROW_SUPPLY_EVENT, 10000)

    def create_enemies(self):
        """根据游戏级别创建不同数量的敌机"""

        # 敌机精灵组中的精灵数量
        count = len(self.enemies_group.sprites())
        # 要添加到的精灵组
        groups = (self.all_group, self.enemies_group)

        # 判断游戏级别及已有的敌机数量
        if self.hud_panel.level == 1 and count == 0:  # 关卡 1
            for i in range(16):
                Enemy(0, 3, *groups)
        elif self.hud_panel.level == 2 and count == 16:  # 关卡 2
            # 1> 增加敌机的最大速度
            for enemy in self.enemies_group.sprites():
                enemy.max_speed = 5
            # 2> 创建敌机
            for i in range(8):
                Enemy(0, 5, *groups)
            for i in range(2):
                Enemy(1, 1, *groups)
        elif self.hud_panel.level == 3 and count == 26:  # 关卡 3
            # 1> 增加敌机的最大速度
            for enemy in self.enemies_group.sprites():
                enemy.max_speed = 7 if enemy.kind == 0 else 3
            # 2> 创建敌机
            for i in range(8):
                Enemy(0, 7, *groups)
            for i in range(2):
                Enemy(1, 3, *groups)
            for i in range(2):
                Enemy(2, 1, *groups)

    def reset_game(self):
        """重设游戏"""
        self.is_game_over = False  # 游戏结束标记
        self.is_pause = False  # 游戏暂停标记

        self.hud_panel.reset_panel()  # 重置指示器面板

        # 设置英雄的初始位置
        self.hero.rect.midbottom = HERO_DEFAULT_MID_BOTTOM

        # 清空所有敌机
        for enemy in self.enemies_group:
            enemy.kill()

        # 清空残留子弹
        for bullet in self.hero.bullets_group:
            bullet.kill()

        # 重新创建敌机
        self.create_enemies()

    def event_handler(self):
        """事件监听

        :return: 如果监听到退出事件，返回 True，否则返回 False
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.is_game_over:  # 游戏已经结束
                    self.reset_game()
                else:  # 切换暂停状态
                    self.is_pause = not self.is_pause

                    # 暂停或恢复背景音乐
                    self.player.pause_music(self.is_pause)

            # 判断是否正在游戏
            if not self.is_game_over and not self.is_pause:
                # 监听关闭子弹增强事件
                if event.type == BULLET_ENHANCED_OFF_EVENT:
                    self.hero.bullets_kind = 0

                    pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 0)

                # 监听投放道具事件
                if event.type == THROW_SUPPLY_EVENT:
                    self.player.play_sound("supply.wav")

                    supply = random.choice(self.supplies_group.sprites())

                    supply.throw_supply()

                # 监听发射子弹事件
                if event.type == HERO_FIRE_EVENT:
                    self.player.play_sound("bullet.wav")

                    self.hero.fire(self.all_group)

                # 监听取消英雄无敌事件
                if event.type == HERO_POWER_OFF_EVENT:
                    print("取消无敌状态...")

                    # 设置英雄属性
                    self.hero.is_power = False

                    # 取消定时器
                    pygame.time.set_timer(HERO_POWER_OFF_EVENT, 0)

                # 监听英雄牺牲事件
                if event.type == HERO_DEAD_EVENT:
                    print("英雄牺牲了...")

                    # 生命计数 -1
                    self.hud_panel.lives_count -= 1

                    # 更新生命计数显示
                    self.hud_panel.show_lives()
                    # 更新炸弹显示
                    self.hud_panel.show_bomb(self.hero.bomb_count)

                # 监听玩家按下字母 b，引爆炸弹
                if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    # 如果英雄没有牺牲同时有炸弹
                    if self.hero.hp > 0 and self.hero.bomb_count > 0:
                        self.player.play_sound("use_bomb.wav")

                    # 引爆炸弹
                    score = self.hero.blowup(self.enemies_group)

                    # 更新炸弹数量显示
                    self.hud_panel.show_bomb(self.hero.bomb_count)

                    # 更新游戏得分，如果游戏等级提升，创建新的敌机
                    if self.hud_panel.increase_score(score):
                        self.create_enemies()

        return False

    def start(self):
        """开始游戏"""

        clock = pygame.time.Clock()  # 游戏时钟
        frame_counter = 0  # 逐帧动画计数器

        while True:
            # 生命计数等于 0，表示游戏结束
            self.is_game_over = self.hud_panel.lives_count == 0

            if self.event_handler():  # 事件监听
                self.hud_panel.save_best_score()

                return

            # 判断游戏状态
            if self.is_game_over:
                self.hud_panel.panel_pause(True, self.all_group)
            elif self.is_pause:
                self.hud_panel.panel_pause(False, self.all_group)
            else:
                self.hud_panel.panel_resume(self.all_group)

                # 碰撞检测
                self.check_collide()

                # 获得当前时刻的按键元组
                keys = pygame.key.get_pressed()
                # 水平移动基数
                move_hor = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                # 垂直移动基数
                move_ver = keys[pygame.K_DOWN] - keys[pygame.K_UP]

                # 修改逐帧动画计数器
                frame_counter = (frame_counter + 1) % FRAME_INTERVAL

                # 更新 all_group 中所有精灵内容
                self.all_group.update(frame_counter == 0, move_hor, move_ver)

            # 绘制 all_group 中的所有精灵
            self.all_group.draw(self.main_window)

            pygame.display.update()  # 更新显示
            clock.tick(60)  # 设置刷新帧率

    def check_collide(self):
        """碰撞检测"""

        # 1. 检测英雄飞机和敌机的碰撞 - 如果英雄处于无敌状态，彼此不能碰撞
        if not self.hero.is_power:
            enemies = pygame.sprite.spritecollide(self.hero,
                                                  self.enemies_group,
                                                  False,
                                                  pygame.sprite.collide_mask)

            # 过滤掉已经被摧毁的敌机
            enemies = list(filter(lambda x: x.hp > 0, enemies))

            # 是否撞到敌机
            if enemies:
                # 播放英雄被撞毁音效
                self.player.play_sound(self.hero.wav_name)

                self.hero.hp = 0  # 英雄被撞毁

            for enemy in enemies:
                enemy.hp = 0  # 敌机同样被撞毁

        # 2. 检测敌机被子弹击中
        hit_enemies = pygame.sprite.groupcollide(self.enemies_group,
                                                 self.hero.bullets_group,
                                                 False,
                                                 False,
                                                 pygame.sprite.collide_mask)

        # 遍历字典
        for enemy in hit_enemies:

            # 已经被摧毁的敌机不需要浪费子弹
            if enemy.hp <= 0:
                continue

            # 遍历击中敌机的子弹列表
            for bullet in hit_enemies[enemy]:

                # 1> 将子弹从所有精灵组中清除
                bullet.kill()

                # 2> 修改敌机的生命值
                enemy.hp -= bullet.damage

                # 3> 如果敌机没有被摧毁，继续下一颗子弹
                if enemy.hp > 0:
                    continue

                # 4> 修改游戏得分并判断是否升级
                if self.hud_panel.increase_score(enemy.value):
                    # 播放升级音效
                    self.player.play_sound("upgrade.wav")

                    self.create_enemies()

                # 播放敌机炸弹音效
                self.player.play_sound(enemy.wav_name)

                # 5> 退出遍历子弹列表循环
                break

        # 3. 英雄拾取道具
        supplies = pygame.sprite.spritecollide(self.hero,
                                               self.supplies_group,
                                               False,
                                               pygame.sprite.collide_mask)
        if supplies:
            supply = supplies[0]

            # 播放使用道具音效
            self.player.play_sound(supply.wav_name)

            # 将道具设置到游戏窗口下方
            supply.rect.y = SCREEN_RECT.h

            # 判断道具类型
            if supply.kind == 0:  # 炸弹补给
                self.hero.bomb_count += 1
                self.hud_panel.show_bomb(self.hero.bomb_count)
            else:  # 设置子弹增强
                self.hero.bullets_kind = 1

                # 设置关闭子弹增强的定时器事件
                pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 8000)


if __name__ == '__main__':
    pygame.init()

    Game().start()

    pygame.quit()
