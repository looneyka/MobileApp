from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from parse_rest.connection import register
from parse_rest.datatypes import Object
from settings_local import APPLICATION_ID, REST_API_KEY
import android

class GameScore(Object):
    pass


class ScoreView(BoxLayout):

    def __init__(self, **kwargs):
        super(ScoreView, self).__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.initialize())

    def initialize(self):
        high_to_low_score_board = GameScore.Query.all().order_by("-score")
        count = 1
        for game_score in high_to_low_score_board:
            text = '{}. {}'.format(count, game_score.score)
            label = Label(text=text)
            self.add_widget(label)
            count += 1

class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        self.ball.move()

        #bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        #bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        #went of to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            android.vibrate(1)
            self.serve_ball(vel=(4, 0))
        if self.ball.x > self.width:
            self.player1.score += 1
            android.vibrate(1)
            self.serve_ball(vel=(-4, 0))

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y


class PongApp(App):
    def build(self):
        register(APPLICATION_ID, REST_API_KEY)
        android.vibrate(2)

    def save(self):
        score1 = self.root.pong_game.player1.score
        score2 = self.root.pong_game.player2.score
        score = max(score1, score2)
        game_score = GameScore(score=score)
        game_score.save()

    def set_state(self, state):
        if state == 'main_game':
            self.root.current = 'main_game'
            game = self.root.pong_game
            game.serve_ball()
            Clock.schedule_interval(game.update, 1.0 / 60.0)

if __name__ == '__main__':
    PongApp().run()