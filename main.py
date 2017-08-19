import CPU
import Input
import pygame
import sys

cpu = CPU.cpu()

ROMPath = 'invaders.rom'    # it should be smaller than 8192bytes
cpu.loadROM(ROMPath)
cpu.InitMap()
cpu.reset()

io = Input.input()

pygame.init()
size = width, height = 256, 224
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
                    pxArray[i][255-j*8-k] = (255, 255, 255)
                else:
                    pxArray[i][255-j*8-k] = (0,0,0)
                vRAM >>= 1

# pxarray.replace(black, (255,255,255), distance=0)
pygame.display.update()
fps = 60
fps_clock = pygame.time.Clock()

# cpu.runCycles(8111000)

# print cpu._memory[9217]
# cpu.runCycles(42434)
# cpu.runCycles(2597707)
# 27300
# a = cpu._memory[0x2400:0x3fff]
cpu.information()
# print cpu._memory[0x2400:0x3fff]
pygame.display.update()
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c: # coin
                cpu.io.IN_PORT1 |= 0x01     # 1 player
            if event.key == pygame.K_1:
                cpu.io.IN_PORT1 |= 0x04
            if event.key == pygame.K_SPACE: # fire
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
    # print "%x" % cpu.PC
    fps_clock.tick(fps)
    pygame.display.update()
    # print "count:", cpu.count

