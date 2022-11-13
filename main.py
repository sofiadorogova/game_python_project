import turtle
import random
import os
import time

"""
Основные неизменяемые костанты
"""

BASE_PATH = os.path.dirname(os.path.dirname('main.py'))
ENEMY_COUNT = {'1': 2, '2': 3, '3': 5}
BASE_X, BASE_Y = 0, -300
BUILDING_INFOS = {
    'house': [BASE_X - 400, BASE_Y],
    'kremlin': [BASE_X - 200, BASE_Y],
    'nuclear': [BASE_X + 200, BASE_Y],
    'skyscraper': [BASE_X + 400, BASE_Y]
}

class BuildingManager:
    INITIAL_HEALTH = 1000

    def __init__(self, x, y, name):
        """
        Инициализация объектов-зданий, черещ три параметра:
        x, y - координаты положения здания на экране;
        name - имя объекта.
        В артибут health записывается величина здоровья объекта.
        """
        self.name = name
        self.x = x
        self.y = y
        self.health = self.INITIAL_HEALTH

        """Размещение объекта на игровом поле"""

        pen = turtle.Turtle()
        pen.hideturtle()
        pen.speed(0)
        pen.penup()
        pen.setpos(x=self.x, y=self.y)
        pic_path = os.path.join(BASE_PATH, "images", self.get_pic_name())
        window.register_shape(pic_path)
        pen.shape(pic_path)
        pen.showturtle()
        self.pen = pen

        """Отображение количества жизней на экране."""

        title = turtle.Turtle(visible=False)
        title.speed(0)
        title.penup()
        title.setpos(x=self.x, y=self.y - 85)
        title.color('white')
        title.write(str(self.health), align="center", font=["Arial", 20, "bold"])
        self.title = title
        self.title_health = self.health

    def get_pic_name(self):
        """
        Анимация повреждения зданий. Функция возращает имя картинки
        с необходимой анимацией в зависимости от количества оставшихся жизней.
        """

        if self.health < self.INITIAL_HEALTH * 0.2:
            return f"{self.name}_3.gif"
        if self.health < self.INITIAL_HEALTH * 0.8:
            return f"{self.name}_2.gif"
        return f"{self.name}_1.gif"

    def draw(self):
        """
        Прорисовка зданий и их количества их жизней.
        Функция устанавливает на экране новую картинку здания, перезаписывает
        информацию о количестве жизней здания.
        """
        pic_name = self.get_pic_name()
        pic_path = os.path.join(BASE_PATH, "images", pic_name)
        if self.pen.shape() != pic_path:
            window.register_shape(pic_path)
            self.pen.shape(pic_path)
        if self.health != self.title_health:
            self.title_health = self.health
            self.title.clear()
            self.title.write(str(self.title_health), align="center", font=["Arial", 20, "bold"])

    def is_alive(self):
        return self.health >= 0



class MissileBase(BuildingManager):
    INITIAL_HEALTH = 2000
    """
    Анимация открытия базы для совершения выстрела, при отлете ракеты
    больше, чем на 50 пикселей, база закрывается
    """
    def get_pic_name(self):
        for missile in our_missiles:
            if missile.distance(self.x, self.y) < 50:
                pic_name = f"{self.name}_opened.gif"
                break
        else:
            pic_name = f"{self.name}.gif"
        return pic_name


class Missile:
    """
    Создание ракеты. Задание основных характеристик.
    """

    def __init__(self, x, y, color, x2, y2):
        """
        Инициализация объекта через 5 параметров:
        x1, y1 - начальные координаты;
        color - цвет ракеты;
        x2, y2 - координаты цели ракеты.
        В теле функции также задается отображение ракеты на экране
        с помощью атрибута pen;
        cостояние ракеты - state (в начальный момент времени считаем
        ракеты готовой к запуску);
        цель - target;
        радиус - 0 (на экране ракета прорисовывается, как дивжущаяся стрелка,
        во время взрыва ее радуис будет увеличиваться)
        """
        self.color = color

        pen = turtle.Turtle(visible=False)
        pen.speed(0)
        pen.color(color)
        pen.penup()
        pen.setpos(x=x, y=y)
        pen.pendown()
        pen.setheading(pen.towards(x=x2, y=y2))
        pen.showturtle()
        self.pen = pen

        self.state = 'launched'
        self.target = x2, y2
        self.radius = 0

    def distance(self, x, y):
        """
        Определяем расстояние до цели (для вражеских ракет)
        """
        return self.pen.distance(x=x, y=y)

    def missile_step(self):
        """
        Изменение состояния ракеты - уставновка, взрыв, смерть.
        Если ракеты установлена, то начинаем ее движение,
        когда расстояние до заданной цели меньше 20 пикселей - взрыв.
        Задаем стрелке (ракете) форму круга для дальнейшей визуализации взрыва.

        Увеличение радиуса ракеты для визуализации взрыва.
        Если ракета уже взорвана, то меняем ее состояние на - dead.
        """
        if self.state == 'launched':
            self.pen.forward(6)
            if self.pen.distance(x=self.target[0], y=self.target[1]) < 30:
                self.state = 'explode'
                self.pen.shape('circle')
        elif self.state == 'explode':
            self.radius += 1
            if self.radius > 5:
                self.pen.clear()
                self.pen.hideturtle()
                self.state = 'dead'
            else:
                self.pen.shapesize(self.radius)
        elif self.state == 'dead':
            self.pen.clear()
            self.pen.hideturtle()

    @property
    def x(self):
        return self.pen.xcor()

    @property
    def y(self):
        return self.pen.ycor()


def fire_missile(x, y):
    """
    Анимация движения пользовательских ракет.
    """
    info = Missile(color='white', x=BASE_X, y=BASE_Y + 30, x2=x, y2=y)
    our_missiles.append(info)

def fire_enemy_missile():
    """
    Анимация движения вражеских ракет.
    x, y - координаты вылета вражеской ракеты,
    alive_buildings - список еще не разрушенных зданий, по которым
    должны прицеливаться вражеские ракеты
    """

    x = random.randint(-600, 600)
    y = 400
    alive_buildings = [object for object in buildings if object.is_alive()]
    if alive_buildings:
        target = random.choice(alive_buildings)
        info = Missile(color='red', x=x, y=y, x2=target.x, y2=target.y)
        enemy_missiles.append(info)

def move_missiles(missiles):
    """Функция запуска ракет. Если наша ракета мертва, то мы удаляем этот объект"""
    for missile in missiles:
        missile.missile_step()

    dead_missiles = [object for object in missiles if object.state == 'dead']
    for dead in dead_missiles:
        missiles.remove(dead)


def check_enemy_count(level):
    """Проверка количества выпущенных вражестких ракет.
    Их количество не должно превышать ENEMY_COUNT,
    для котроля уровня сложности."""
    if len(enemy_missiles) < ENEMY_COUNT[level]:
        fire_enemy_missile()


def check_interceptions():
    """
    Проверка перехвата вражеских ракет (столкновений).
    Если ракеты столкнулись, то требуется изменить
    состояние вражеской ракеты на dead.
    Функция отслеживает состояние каждой вражеской ракеты.
    """
    for our_missile in our_missiles:
        if our_missile.state != 'explode':
            continue
        for enemy_missile in enemy_missiles:
            if enemy_missile.distance(our_missile.x, our_missile.y) < our_missile.radius * 10:
                enemy_missile.state = 'dead'


def check_impact():
    """
    Проверка поверждения зданий. Если вражеская ракета близка к зданию,
    то здоровье здания уменьшается
    """
    for enemy_missile in enemy_missiles:
        if enemy_missile.state != 'explode':
            continue
        for building in buildings:
            if enemy_missile.distance(building.x, building.y) < enemy_missile.radius * 10:
                building.health -= 100


def game_over():
    return base.health < 0


def draw_buildings():
    for building in buildings:
        building.draw()


def game(level):
    """
    Запуск игры, объявление и определение списков зданий, наших ракет,
    вражеских ракет.
    Запуск игрового цикла.
    Объявление об окончании игры.
    """
    global our_missiles, enemy_missiles, buildings, base

    window.clear()
    window.bgpic(os.path.join(BASE_PATH, "images", "background.png"))
    window.tracer(n=2)

    window.onclick(fire_missile)
    our_missiles = []
    enemy_missiles = []
    buildings = []

    base = MissileBase(x=BASE_X, y=BASE_Y, name='base')
    buildings.append(base)

    for name, position in BUILDING_INFOS.items():
        building = BuildingManager(x=position[0], y=position[1], name=name)
        buildings.append(building)

    while True:
        window.update()
        if game_over():
            break
        draw_buildings()
        check_impact()
        check_enemy_count(level)
        check_interceptions()
        move_missiles(missiles=our_missiles)
        move_missiles(missiles=enemy_missiles)
        time.sleep(.01)

    pen = turtle.Turtle(visible=False)
    pen.speed(0)
    pen.penup()
    pen.color('red')
    pen.write('Game over', align="center", font=["Arial", 80, "bold"])


def hello_board():
    window.clear()
    window.bgpic(os.path.join(BASE_PATH, "images", "background.png"))
    pen = turtle.Turtle(visible=False)
    pen.speed(0)
    pen.penup()
    pen.color('white')
    pen.write('CosmoWar', align="center", font=["Arial", 80, "bold"])
    display_window = window.textinput(title='Привет!', prompt='Какой уровень игры вы хотите выбрать? (1, 2, 3)')
    user_ans = display_window.lower()
    if user_ans in ('1', '2', '3'):
        game(user_ans)


window = turtle.Screen()
window.setup(1200 + 3, 800 + 3)
window.screensize(1200, 800)

while True:
    hello_board()
    answer = window.textinput(title='Привет!', prompt='Хотите сыграть еще? д/н')
    if answer.lower() not in ('д', 'да', 'y', 'yes'):
        break
