
from pycraft.gamestate import GameState
from pycraft.world import World
from pycraft.objects.player import Player
from pycraft.objects.block import get_block
from pyglet.window import key, mouse
import pyglet.graphics
from pycraft.util import sectorize, cube_vertices, normalize
import pyglet.window
import pyglet.gl as GL
import math

# Convenience list of num keys.
NUMERIC_KEYS = [
    key._1, key._2, key._3, key._4, key._5,
    key._6, key._7, key._8, key._9, key._0
]


class GameStateRunning(GameState):
    def __init__(self, config, height, width):
        self.world = World()
        self.player = Player(config["world"])

        # The crosshairs at the center of the screen.
        self.reticle = None
        # The label that is displayed in the top left of the canvas.
        self.game_info_label = pyglet.text.Label(
            '', font_name='Arial', font_size=18,
            x=10, y=height - 10, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))
        self.current_item_label = pyglet.text.Label(
            '', font_name='Arial', font_size=18,
            x=width - 10, y=10, anchor_x='right', anchor_y='bottom',
            color=(0, 0, 0, 255))

        # Initialise joystick
        joysticks = pyglet.input.get_joysticks()
        if joysticks:
            joystick = joysticks[0]
            joystick.open()
            joystick.push_handlers(self)

    def on_mouse_press(self, x, y, button, modifiers):
        vector = self.player.get_sight_vector()
        block, previous = self.world.hit_test(self.player.position, vector)
        if (button == mouse.RIGHT) or \
                ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
            # ON OSX, control + left click = right click.
            player_x, player_y, player_z = normalize(self.player.position)
            if previous and previous != (player_x, player_y, player_z) and \
                    previous != (player_x, player_y - 1, player_z):
                # make sure the block isn't in the players head or feet
                if self.player.current_item:
                    self.world.add_block(previous, get_block(self.player.get_block()))

        elif button == pyglet.window.mouse.LEFT and block:
            texture = self.world.objects[block]
            if texture.hit_and_destroy():
                self.world.remove_block(block)

    def on_mouse_motion(self, x, y, dx, dy):
        m = 0.15
        x, y = self.player.rotation
        x, y = x + dx * m, y + dy * m
        y = max(-90, min(90, y))
        self.player.rotation = (x, y)

    def on_key_press(self, symbol, modifiers, controls):
        if symbol == getattr(key, controls['forward']):
            self.player.strafe_forward()
        elif symbol == getattr(key, controls['backward']):
            self.player.strafe_backward()
        elif symbol == getattr(key, controls['right']):
            self.player.strafe_right()
        elif symbol == getattr(key, controls['left']):
            self.player.strafe_left()
        elif symbol == getattr(key, controls['jump']):
            self.player.jump()
        elif symbol == getattr(key, controls['down']):
            self.player.strafe_down()
        elif symbol == getattr(key, controls['fly']):
            self.player.fly()
        elif symbol in NUMERIC_KEYS:
            self.player.switch_inventory(symbol - NUMERIC_KEYS[0])

    def on_key_release(self, symbol, modifiers, controls):
        if symbol == getattr(key, controls['forward']):
            self.player.strafe_backward()
        elif symbol == getattr(key, controls['backward']):
            self.player.strafe_forward()
        elif symbol == getattr(key, controls['left']):
            self.player.strafe_right()
        elif symbol == getattr(key, controls['right']):
            self.player.strafe_left()
        elif symbol == getattr(key, controls['jump']):
            self.player.strafe_down()
        elif symbol == getattr(key, controls['down']):
            self.player.strafe_up()

    def on_joybutton_press(self, joystick, button):
        vector = self.player.get_sight_vector()
        block, previous = self.world.hit_test(self.player.position, vector)
        if button == 0:
            player_x, player_y, player_z = normalize(self.player.position)
            if previous and previous != (player_x, player_y, player_z) and \
                    previous != (player_x, player_y - 1, player_z):
                # make sure the block isn't in the players head or feet
                if self.player.current_item:
                    self.world.add_block(previous, get_block(self.player.get_block()))

        elif button == 1:
            self.player.jump()

        elif button == 2 and block:
            texture = self.world.objects[block]
            if texture.hit_and_destroy():
                self.world.remove_block(block)

        elif button == 3:
            self.player.fly()

        elif button == 4:
            self.player.previous_inventory_item()

        elif button == 5:
            self.player.next_inventory_item()

        print('Button %s pressed' % button)

    def on_joybutton_release(self, joystick, button):
        print('Button %s released' % button)

    def on_joyaxis_motion(self, joystick, axis, value):
        print(f"{axis} = {value}")
        if axis in ["rx", "ry"]:
            if abs(value) < 0.05:
                value = 0

            if axis == "rx":  # Turn left/right
                self.player.strafe[3] = value
            elif axis == "ry":  # Look up/down
                self.player.strafe[2] = -value

        elif axis in ["hat_x", "hat_y"]:
            int_value = int(value)
            if axis == "hat_y":
                if int_value == 1:
                    self.player.strafe_forward()
                elif int_value == -1:
                    self.player.strafe_backward()
                elif int_value == 0:
                    self.player.strafe[0] = 0

            elif axis == "hat_x":
                if int_value == 1:
                    self.player.strafe_right()
                elif int_value == -1:
                    self.player.strafe_left()
                elif int_value == 0:
                    self.player.strafe[1] = 0

        elif axis in ["x", "y"]:
            if abs(value) < 0.05:
                value = 0

            if axis == "y":
                self.player.strafe[0] = value

            elif axis == "x":
                self.player.strafe[1] = value

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print(f"Hat = ({hat_x},{hat_y})")
        m = 0.15
        x, y = self.player.rotation
        x, y = x + hat_x * m, y + hat_y * m
        y = max(-90, min(90, y))
        self.player.rotation = (x, y)

    def on_resize(self, width, height):
        # label
        self.game_info_label.y = height - 10
        self.current_item_label.x = width - 10
        # reticle
        if self.reticle:
            self.reticle.delete()
        x, y = width // 2, height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(
            4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )

    def on_draw(self, size):
        self.set_3d(size)
        GL.glColor3d(1, 1, 1)
        self.world.start_shader()
        self.world.batch.draw()
        self.world.stop_shader()
        self.draw_focused_block()
        self.set_2d(size)
        self.draw_labels()
        self.draw_reticle()

    def set_3d(self, size):
        """Configure OpenGL to draw in 3d."""
        width, height = size
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.gluPerspective(65.0, width / float(height), 0.1, 60.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        x, y = self.player.rotation
        GL.glRotatef(x, 0, 1, 0)
        GL.glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.player.position
        GL.glTranslatef(-x, -y, -z)

    def set_2d(self, size):
        """Configure OpenGL to draw in 2d."""
        width, height = size
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, width, 0, height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

    def update(self, dt, ticks_per_second):
        self.world.process_queue(ticks_per_second)
        sector = sectorize(self.player.position)
        if sector != self.world.sector:
            self.world.change_sectors(self.world.sector, sector)
            if self.world.sector is None:
                self.world.process_entire_queue()
            self.world.sector = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in range(m):
            self.player.update(dt / m, self.world.objects)

    def draw_focused_block(self):
        """Draw black edges around the block that is currently under the
        crosshairs.
        """
        vector = self.player.get_sight_vector()
        block = self.world.hit_test(self.player.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            GL.glColor3d(0, 0, 0)
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
            pyglet.graphics.draw(24, GL.GL_QUADS, ('v3f/static', vertex_data))
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

    def draw_labels(self):
        """Draw the label in the top left of the screen."""
        x, y, z = self.player.position
        self.game_info_label.text = '%02d (%.2f, %.2f, %.2f) %d / %d' % (
            pyglet.clock.get_fps(), x, y, z,
            len(self.world._shown), len(self.world.objects))
        self.game_info_label.draw()
        self.current_item_label.text = self.player.current_item if self.player.current_item else "No items in this inventory"
        self.current_item_label.draw()

    def draw_reticle(self):
        """Draw the crosshairs in the center of the screen."""
        GL.glColor3d(0, 0, 0)
        self.reticle.draw(GL.GL_LINES)
