import CPU
import Input
import pygame
import sys

cpu = CPU.cpu()

ROMPath = 'invaders.rom'  # it should be smaller than 8192bytes
cpu.loadROM(ROMPath)
cpu.InitMap()
cpu.reset()

io = Input.input()

pygame.init()
width, height = 256, 224
size = height, width
black = 0, 0, 0

surface = pygame.display.set_mode(size)
pygame.display.set_caption('Invaders')
surface.fill(black)
pxarray = pygame.PixelArray(surface)


def refresh(processor, pxArray):
    for i in range(height):
        index = 0x2400 + (i << 5)
        for j in range(32):
            vRAM = processor._memory[index]
            index += 1
            for k in range(8):
                if (vRAM & 0x01) == 1:
                    pxArray[i][255 - j * 8 - k] = (255, 255, 255)
                else:
                    pxArray[i][255 - j * 8 - k] = (0, 0, 0)
                vRAM >>= 1


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
    refresh(cpu, pxarray)
    fps_clock.tick(fps)
    pygame.display.update()
