from selenium import webdriver
import CPU

driver = webdriver.Chrome()
driver.get('https://bluishcoder.co.nz/js8080')
buttonRun = driver.find_element_by_xpath('html//button[6]')
buttonRunN = driver.find_element_by_xpath('html//button[7]')
textRun = driver.find_element_by_id('n')
pc = driver.find_element_by_id('pc')

cpu = CPU.cpu()
ROMPath = 'invaders.rom'    # it should be smaller than 8192bytes
cpu.loadROM(ROMPath)
cpu.InitMap()

textRun.clear()
textRun.send_keys('1500')
buttonRunN.click()
cpu.runCycles(1500)

pre_chrome_pc = 0
pre_cpu_pc = 0

i = 1
while True:
    buttonRun.click()
    cpu_pc = cpu.runCycles(1)
    if int(pc.text, 16) != cpu_pc:
        print pc.text
        print cpu_pc
        print  i+1500
        print pre_chrome_pc
        print pre_cpu_pc
        break
    pre_chrome_pc = pc.text
    pre_cpu_pc = cpu_pc
    i += 1

