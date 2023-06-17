import math
import sys
import pygame
import pygame.freetype

RAD = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)

EVENT_START = pygame.USEREVENT
BUTTONCLICK = EVENT_START + 1
LINECLICK = EVENT_START + 2


class Function:
    class one:
        @classmethod
        def base(cls, x: float) -> float:
            return x

        @classmethod
        def sqrt(cls, x: float) -> float:
            return x ** 0.5

        @classmethod
        def ln(cls, x: float) -> float:
            return math.log(x)

    class two:
        @classmethod
        def base(cls, x: float, y: float) -> float:
            return x / y


class Button:
    def __init__(self,
                 rect: tuple[float, float, float, float],
                 color: pygame.Color,
                 font: pygame.freetype.Font = None,
                 text: str = "",
                 text_color: pygame.Color = BLACK):
        self.text_color = text_color
        self.font = font
        self.text = text
        self.color = color
        self.rect = pygame.Rect(*rect)

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)
        if self.text != "":
            width = self.font.size * len(self.text) / 2
            height = self.font.size / 2
            self.font.render_to(surface,
                                pygame.Rect(self.rect.centerx - width, self.rect.centery - height + 3, width, height),
                                self.text, self.text_color)

    def update(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(*event.pos):
                ev = pygame.event.Event(BUTTONCLICK, {"button": self})
                pygame.event.post(ev)


class InputBox:
    def __init__(self,
                 rect: tuple[float, float, float, float],
                 color: pygame.Color,
                 font: pygame.freetype.Font,
                 text_color: pygame.Color = BLACK,
                 frame: int = 0,
                 frame_color: pygame.Color = BLACK):
        self.frame_color = frame_color
        self.text_color = text_color
        self.frame = frame
        self.font = font
        self.color = color
        self.rect = pygame.Rect(*rect)
        self.active = 0
        self.show_text = "1"
        self.text = "1"

    def state_change(self):
        if self.active:
            self.color = pygame.Color(self.color.r - 20, self.color.g - 20, self.color.b - 20)
        else:
            self.color = pygame.Color(self.color.r + 20, self.color.g + 20, self.color.b + 20)

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, self.frame_color, self.rect, self.frame)
        if self.show_text != "":
            self.font.render_to(surface,
                                pygame.Rect(self.rect.left + 5, 15, width - 10, height - 10),
                                self.show_text, self.text_color)

    def update(self, event: pygame.event.Event):
        if self.active == 0:  # no click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(*event.pos):
                    self.active = 1
                    self.state_change()
                    self.update(event)
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # end
                    if len(self.show_text) == 0:
                        self.show_text = "1"
                    if int(self.show_text) > 8:
                        self.show_text = "8"
                    self.text = self.show_text
                    self.active = 0
                    self.state_change()
                elif event.key == pygame.K_BACKSPACE:  # del
                    self.show_text = self.show_text[:-1]
                elif pygame.K_0 <= event.key <= pygame.K_9:  # input
                    if len(self.show_text) < 2:
                        self.show_text += event.unicode


class CircleButton:
    def __init__(self,
                 pos: tuple[float, float],
                 radius: float,
                 color: pygame.Color,
                 frame: int = 0, ):
        self.frame_ = frame
        self.frame = frame
        self.color = color
        self.pos = pos
        self.radius = radius
        self.state = 1

    def state_change(self):
        if self.state:
            self.frame_ = self.frame
            self.frame = 0
            self.state = 0
        else:
            self.frame = self.frame_
            self.state = 1

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, self.pos, self.radius, self.frame)

    def update(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if math.dist(self.pos, event.pos) <= self.radius:
                ev = pygame.event.Event(BUTTONCLICK, {"button": self})
                pygame.event.post(ev)


class Line:
    def __init__(self,
                 start_pos: CircleButton, end_pos: CircleButton,
                 color: pygame.Color, width: int = 1):
        self.width = width
        self.end_pos = end_pos
        self.start_pos = start_pos
        self.color = color

    def pos_on_this(self, pos: tuple[float, float]):
        return point_on_line_with_width(pos, self.width, self.start_pos.pos, self.end_pos.pos)

    def draw(self, surface: pygame.Surface):
        pygame.draw.line(surface, self.color, self.start_pos.pos, self.end_pos.pos, self.width)

    def update(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                if self.pos_on_this(event.pos):
                    ev = pygame.event.Event(LINECLICK, {"line": self})
                    pygame.event.post(ev)


def draw(width: float, height: float):
    # region control UI
    rect_control = pygame.Rect(0, 0, width * k, height)
    control = pygame.Surface(rect_control.size)
    control.fill(pygame.Color(200, 200, 200))
    # update UI
    buttons["start"].rect = pygame.Rect(10, height - 60, rect_control.width - 20, 50)
    buttons["start"].font.size = area_size(rect_control.width - 20, 50, 2)
    # buttons["1"].rect = pygame.Rect(10, 10, rect_control.width - 20, 60)
    input_boxs["floor"].rect = pygame.Rect(10, 10, rect_control.width - 20, 60)
    # draw
    for name in buttons:
        buttons[name].draw(control)
    for name in input_boxs:
        input_boxs[name].draw(control)
    screen.blit(control, (0, 0))
    # endregion

    # game window
    rect_gameWindow = pygame.Rect(rect_control.right, 0, width - rect_control.right, height)
    game_window = pygame.Surface(rect_gameWindow.size)
    game_window.fill(BLACK)
    gameWindow_center = (rect_gameWindow.width / 2, rect_gameWindow.height / 2)

    # region draw circle
    # max radius
    floor = int(input_boxs["floor"].text)
    if rect_gameWindow.height <= rect_gameWindow.width:
        max_r = rect_gameWindow.height * 0.5 * floor / (floor + 1)
    else:
        max_r = rect_gameWindow.width * 0.5 * floor / (floor + 1)
    # draw
    if (max_r / floor - 5) > 5:  # center
        pygame.draw.circle(game_window, BLUE, gameWindow_center, 5, 1)
    else:
        pygame.draw.circle(game_window, BLUE, gameWindow_center, 2, 1)
    thickness = int(10 / floor) + 1  # var
    num = 4
    i_ = 0
    for i in range(floor):  # draw circle
        r = max_r * (i + 1) / floor
        pygame.draw.circle(game_window, BLUE, gameWindow_center, r, thickness)
        if 2 * math.pi / num * r >= max_r / floor:
            num = 4 * (2 ** i_)
            i_ += 1
        for j in range(num):  # draw circle button
            theta = 2 * math.pi / num * j
            x = gameWindow_center[0] + r * math.cos(theta)
            y = gameWindow_center[1] - r * math.sin(theta)
            name = str(i + 1) + "_" + str(theta)
            # r_ = thickness / 2 + 1
            r_ = max(3, int(thickness / 2 + 1))
            if name in circle_buttons.keys():
                circle_buttons[str(i + 1) + "_" + str(theta)].pos = (x, y)
                circle_buttons[str(i + 1) + "_" + str(theta)].radius = r_
            else:
                circle_buttons[str(i + 1) + "_" + str(theta)] = CircleButton((x, y), r_, GREEN, 1)
    # endregion

    # show
    clear_name = []
    for name in circle_buttons:
        if int(name.split("_")[0]) > floor:
            clear_name.append(name)
        else:
            circle_buttons[name].draw(game_window)
    for name in clear_name:
        circle_buttons.pop(name)
    for i in lines:
        if not point_on_segment(gameWindow_center, i.start_pos.pos, i.end_pos.pos) and \
                (i.start_pos in circle_buttons.values()) and (i.end_pos in circle_buttons.values()):
            i.width = thickness
            i.draw(game_window)
        else:
            lines.remove(i)

    screen.blit(game_window, (rect_control.right, 0))


def windows_size_change(width, height):
    draw(width, height)


# region tool function
def area_size(width: float, height: float, num: int) -> int:
    if width <= height * num:
        return int(width / num)
    else:
        return int(height)


def distance(pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
    x1, y1 = pos1
    x2, y2 = pos2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def point_on_segment(point: tuple[float, float],
                     segment_start: tuple[float, float], segment_end: tuple[float, float]) -> bool:
    point_x, point_y = point
    # 确定线段的两个端点的坐标
    start_x, start_y = segment_start
    end_x, end_y = segment_end
    # 计算点到线段起点的向量和点到线段终点的向量
    vector1 = (point_x - start_x, point_y - start_y)
    vector2 = (end_x - start_x, end_y - start_y)
    # 计算叉积
    cross_product = vector1[0] * vector2[1] - vector1[1] * vector2[0]
    # 判断点是否在线段上
    if cross_product == 0:
        # 判断点是否在线段的延长线上
        if (min(start_x, end_x) <= point_x <= max(start_x, end_x) and
                min(start_y, end_y) <= point_y <= max(start_y, end_y)):
            return True
    return False


def point_on_line_with_width(point: tuple[float, float], line_width: float,
                             line_start: tuple[float, float], line_end: tuple[float, float]):
    # 确定点的坐标
    point_x, point_y = point
    # 确定线段的两个端点的坐标
    start_x, start_y = line_start
    end_x, end_y = line_end
    # 计算线段的长度
    line_length = math.dist(line_start, line_end)
    # 计算点到线段的距离
    distance = abs((end_x - start_x) * (start_y - point_y) - (start_x - point_x) * (end_y - start_y)) / line_length

    # 判断点是否在线段上
    half = line_width / 2
    if distance <= half:
        if ((min(start_x, end_x) - half) < point_x < (max(start_x, end_x) + half) and
                (min(start_y, end_y) - half) < point_y < (max(start_y, end_y) + half)):
            return True
    else:
        return False


def remove_duplicates(my_list: list) -> list:
    return list(dict.fromkeys(my_list))
# endregion


if __name__ == "__main__":
    # init
    pygame.init()

    # set windows
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    pygame.display.set_caption("魔法阵")

    # var
    buttons = {}
    circle_buttons = {}
    input_boxs = {}
    lines = []

    # region draw base UI
    k = 1 / 4
    rect_control = pygame.Rect(0, 0, width * k, height)
    control = pygame.Surface(rect_control.size)
    control.fill(pygame.Color(200, 200, 200))

    buttons["start"] = Button((10, height - 60, rect_control.width - 20, 50), RAD,
                              pygame.freetype.Font("./FZQTJW.TTF", area_size(rect_control.width - 20, 50, 2)),
                              "开始", BLACK)
    buttons["start"].draw(control)
    input_boxs["floor"] = InputBox((10, 10, rect_control.width - 20, 60), WHITE,
                                   pygame.freetype.Font("./comic.ttf", 20), BLACK, 1, BLACK)
    input_boxs["floor"].draw(control)

    screen.blit(control, (0, 0))
    # endregion

    # draw game window and update control
    draw(*size)

    # main
    circle_buttons_click = None
    while True:
        for event in pygame.event.get():
            # region update UI
            for name in buttons:
                buttons[name].update(event)
            for name in input_boxs:
                input_boxs[name].update(event)
                input_boxs[name].draw(control)
            if event.type == pygame.MOUSEBUTTONDOWN:
                event.pos = (event.pos[0] - rect_control.right, event.pos[1])
            for name in circle_buttons:
                circle_buttons[name].update(event)
            for line in lines:
                line.update(event)
            # endregion

            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                windows_size_change(width, height)

            if event.type == BUTTONCLICK:
                if event.dict["button"] == buttons["start"]:
                    pass
                if type(event.dict["button"]) == CircleButton:
                    if (circle_buttons_click is not None) and (circle_buttons_click != event.dict["button"]):
                        points = [circle_buttons_click]
                        for name in circle_buttons:
                            line = Line(event.dict["button"], circle_buttons_click, RAD)
                            if line.pos_on_this(circle_buttons[name].pos):
                                points.append(circle_buttons[name])
                        points.append(event.dict["button"])
                        points = remove_duplicates(points)
                        for i in range(len(points)):
                            if i != (len(points) - 1):
                                lines.append(Line(points[i], points[i + 1], RAD))
                        circle_buttons_click.state_change()
                        circle_buttons_click = None
                    else:
                        circle_buttons_click = event.dict["button"]
                        event.dict["button"].state_change()
            if event.type == LINECLICK:
                lines.remove(event.dict["line"])

            draw(width, height)
        pygame.display.update()
