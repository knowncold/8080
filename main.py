import Cpu
import Input
import pygame
import sys

cpu = Cpu.Cpu()

ROMPath = 'invaders.rom'  # it should be smaller than 8192bytes
cpu.loadROM(ROMPath)
cpu.InitMap()
cpu.reset()

io = Input.Input()

pygame.init()
width, height = 256, 224
size = height, width
black = 0, 0, 0

surface = pygame.display.set_mode(size)
pygame.display.set_caption('Invaders')
surface.fill(black)
pxArray = pygame.PixelArray(surface)


def refresh(processor, px_array):
    for i in range(height):
        index = 0x2400 + (i << 5)
        for j in range(32):
            v_ram = processor.get_memory()[index]
            index += 1
            for k in range(8):
                if (v_ram & 0x01) == 1:
                    px_array[i][255 - j * 8 - k] = (255, 255, 255)
                else:
                    px_array[i][255 - j * 8 - k] = (0, 0, 0)
                v_ram >>= 1


pygame.display.update()
fps = 60
fps_clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:  # coin
                cpu.io.IN_PORT1 |= 0x01  # 1 player
            if event.key == pygame.K_1:
                cpu.io.IN_PORT1 |= 0x04
            if event.key == pygame.K_SPACE:  # fire
                cpu.io.IN_PORT1 |= 0x10
            if event.key == pygame.K_LEFT:
                cpu.io.IN_PORT1 |= 0x20
            if event.key == pygame.K_RIGHT:
                cpu.io.IN_PORT1 |= 0x40
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_c:
                cpu.io.IN_PORT1 &= 255 - 0x01
            if event.key == pygame.K_1:
                cpu.io.IN_PORT1 &= 255 - 0x04
            if event.key == pygame.K_SPACE:
                cpu.io.IN_PORT1 &= 255 - 0x10
            if event.key == pygame.K_LEFT:
                cpu.io.IN_PORT1 &= 255 - 0x20
            if event.key == pygame.K_RIGHT:
                cpu.io.IN_PORT1 &= 255 - 0x40

    cpu.Run()
    refresh(cpu, pxArray)
    fps_clock.tick(fps)
    pygame.display.update()
