from selenium import webdriver
import CPU

driver = webdriver.Chrome()
driver.get('https://bluishcoder.co.nz/js8080')
buttonRun = driver.find_element_by_xpath('html//button[6]')
buttonRunN = driver.find_element_by_xpath('html//button[7]')
textRun = driver.find_element_by_id('n')

af = driver.find_element_by_id('af')
bc = driver.find_element_by_id('bc')
de = driver.find_element_by_id('de')
hl = driver.find_element_by_id('hl')
sp = driver.find_element_by_id('sp')
pc = driver.find_element_by_id('pc')


cpu = CPU.cpu()
ROMPath = 'invaders.rom'    # it should be smaller than 8192bytes
cpu.loadROM(ROMPath)
cpu.InitMap()

beginCycles = 37300

textRun.clear()
textRun.send_keys(str(beginCycles))
buttonRunN.click()
cpu.runCycles(beginCycles)

pre_chrome_pc = 0
pre_cpu_pc = 0

textRun.clear()
textRun.send_keys(str(1000))

i = 1
while True:
    buttonRunN.click()
    cpu_pc = cpu.runCycles(1000)
    # buttonRun.click()
    # cpu_pc = cpu.runCycles(1)
    if int(pc.text, 16) != cpu_pc:
        print "PC problem"
        print i + beginCycles
        cpu.information()
        break

    if int(bc.text, 16) != cpu.BC:
        print "BC problem"
        cpu.information()
        print i + beginCycles
        break

    if int(de.text, 16) != cpu.DE:
        print "DE problem"
        print pc.text
        print cpu_pc
        print i + beginCycles
        print pre_chrome_pc
        print pre_cpu_pc
        break

    if int(hl.text, 16) != cpu.HL:
        print "HL problem"
        print pc.text
        print cpu_pc
        print i + beginCycles
        print pre_chrome_pc
        print pre_cpu_pc
        break

    if int(sp.text, 16) != cpu.SP:
        print "SP problem"
        cpu.information()
        break

    if int(cpu.BC & 0xFF) != cpu.C:
        print "C problem"
        cpu.information()
        break

    pre_chrome_pc = pc.text
    pre_cpu_pc = cpu_pc
    i += 1
    print i*1000 + beginCycles
    # print i + beginCycles

