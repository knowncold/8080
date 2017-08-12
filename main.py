import CPU
import Input
import OpenGL
# import pyglet
# from pyglet.window import key

cpu = CPU.cpu()


ROMPath = 'invaders.rom'    # it should be smaller than 8192bytes
cpu.loadROM(ROMPath)

cpu.InitMap()

cpu.reset()

# cpu.Run()
cpu.runCycles(1550)
# cpu.runCycles(1)
cpu.information()
# window = pyglet.window.Window()
#
# label = pyglet.text.Label('Hello',
#                           font_name='Ubuntu mono',
#                           font_size=36,
#                           x=window.width//2,
#                           y=window.height//2,
#                           anchor_x='center',anchor_y='center')
#
# @window.event
# def on_draw():
#     window.clear()
#     label.draw()
#
# @window.event
# def on_key_press(symbol, modifiers):
#     if symbol == key.UP:
#
#
#
#
#
# pyglet.app.run()
#
#
#
#
#
#

