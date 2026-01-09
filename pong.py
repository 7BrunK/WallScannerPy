from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock

from random import randint

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            speedup = 1.2
            offset = 0.02 * Vector(0, ball.center_y - self.center_y)
            ball.velocity = speedup * (offset - ball.velocity)

class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    label1 = ObjectProperty(None)
    label2 = ObjectProperty(None)

    def update(self, delta):
        self.ball.move()

        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1
        if (self.ball.x < 0) or (self.ball.right > self.width):
            if self.ball.x < 0:
                self.player2.score += 1
                self.label2.text = str(self.player2.score)
            else:
                self.player1.score += 1
                self.label1.text = str(self.player1.score)
            self.serve_ball()

    def serve_ball(self):
        self.ball.center = self.center
        self.ball.velocity = Vector(4, 0).rotate(randint(0, 360))

    def on_touch_move(self, touch):
        if touch.x < self.width/2:
            self.player1.center_y = touch.y
        if touch.x > self.width/2:
            self.player2.center_y = touch.y

    def winner_label(self, ):
        pass

class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == "__main__":
    PongApp().run()