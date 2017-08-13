import CPU
import Input
import pygame
import sys

cpu = CPU.cpu()

ROMPath = 'invaders.rom'    # it should be smaller than 8192bytes
cpu.loadROM(ROMPath)
cpu.InitMap()
cpu.reset()



pygame.init()

size = width, height = 256, 224
size = height, width
black = 0, 0, 0

surface = pygame.display.set_mode(size)
pygame.display.set_caption('Invaders')
surface.fill(black)
pxarray = pygame.PixelArray(surface)
print pxarray

# pxarray[100,100] = (255,255,255)

def refresh(processor, pxArray):
    for i in range(height):
        index = 0x2400 + (i << 5)
        for j in range(32):
            vRAM = processor._memory[index]
            index += 1
            for k in range(8):
                if (vRAM & 0x01) == 1:
                    pxArray[i][255-j*8-k] = (255, 0, 0)
                else:
                    pxArray[i][255-j*8-k] = (0,0,0)
                vRAM >>= 1

# pxarray.replace(black, (255,255,255), distance=0)
pygame.display.update()

cpu.runCycles(40000)
print cpu._memory
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    # ballrect = ballrect.move(speed)
    # if ballrect.left < 0 or ballrect.right > width:
    #     speed[0] = -speed[0]
    # if ballrect.top < 0 or ballrect.bottom > height:
    #     speed[1] = -speed[1]
    # for i in range(0,width):
    #     for j in range(0,height):
    #         pxarray[i,j] = (255,255,255)
    #         pygame.display.update()
    cpu.runCycles(1)
    print "%x" % cpu.PC
    refresh(cpu, pxarray)
    pygame.display.update()




# cpu = CPU.cpu()
#
# ROMPath = 'invaders.rom'    # it should be smaller than 8192bytes
# cpu.loadROM(ROMPath)
# cpu.InitMap()
# cpu.reset()
#
# while True:
#     cpu.runCycles(1)
#     print "%x" % cpu.PC

