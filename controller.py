import pyglet

joysticks = pyglet.input.get_joysticks()
if not joysticks:
    print("No joysticks detected")
    exit(0)

joystick = joysticks[0]
joystick.open()


class Controller:

    def on_joybutton_press(self, joystick, button):
        print('Button %s pressed' % button)

    def on_joybutton_release(self, joystick, button):
        print('Button %s released' % button)

    def on_joyaxis_motion(self, joystick, axis, value):
        print(f"{axis} = {value}")

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print(f"Hat = ({hat_x},{hat_y})")


my_controller = Controller()
joystick.push_handlers(my_controller)


pyglet.app.run()
