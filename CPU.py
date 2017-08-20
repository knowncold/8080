import struct
import Input


class cpu:
    def __init__(self):
        self._memory = []
        self.PC = 0
        self.SP = 0xF000  # stack pointer
        self.A = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.H = 0
        self.L = 0
        self.BC = 0
        self.DE = 0
        self.HL = 0
        self.SIGN = False  # True minus    MST
        self.ZERO = False
        self.HALFCARRY = False
        self.PARITY = False  # odd or even
        self.CARRY = False
        self.INTERRUPT = False
        self.current_inst = 0  # current instruction

        self.interrupt_alternate = False
        self.count_inst = 0

        self.count = 0
        self.cycles = 0
        self.prev = 0

        self.disassembly_pc = 0
        self.mappingTable = [0] * 0x100
        self.inst_per_frame = 4000
        self.half_inst_per_frame = 2000

        self.io = Input.input()

    def loadROM(self, path):
        f = open(path, 'rb')
        while True:
            byte = f.read(1)
            if byte == '':
                break
            else:
                a, = struct.unpack('c', byte)
                self._memory.append(ord(a))
        # self._memory += [0] * (16384 - len(self._memory))   # ROM + RAM(work RAM and video RAM) = 16384 0x3fff
        self._memory += [0] * (65536 - len(self._memory))   # ROM + RAM(work RAM and video RAM) = 16384 0x3fff

    def reset(self):
        self.PC = 0
        self.A = 0
        self.setBC(0)
        self.setHL(0)
        self.SIGN = False
        self.ZERO = False
        self.HALFCARRY = False
        self.PARITY = False
        self.CARRY = False
        self.INTERRUPT = False

    def Run(self):
        for i in range(16667):
            self.execINST()

    def runCycles(self, cycles):
        for i in range(cycles):
            self.execINST()
        # print "PC: " + "%x"%self.PC
        # print "oprand: " + "%x"%(self.current_inst)
        return self.PC

    def flag(self):
        value = 0
        if self.CARRY:
            value += 0x01
        if self.PARITY:
            value += 0x04
        if self.ZERO:
            value += 0x40
        if self.SIGN:
            value += 0x80
        if self.INTERRUPT:
            value += 0x20
        if self.HALFCARRY:
            value += 0x10
        return value

    def execINST(self):
        self.disassembly_pc = self.PC
        self.current_inst = self.FetchRomNext1Byte()
        if not self.mappingTable[self.current_inst] == None:
            self.mappingTable[self.current_inst]()
            # print "PC: " + "%x"%self
            # print "oprand: " + str(self.current_inst)
        else:
            print "Oprand Error: " + str(self.current_inst)
        self.count_inst += 1
        self.count += 1

        # if self.count_inst >= self.half_inst_per_frame:
        #     # print "INTERRUPUT"
        #     if self.INTERRUPT:
        #         if self.interrupt_alternate == False:
        #             self.callInterrupt(0x08)
        #         else:
        #             self.callInterrupt(0x10)
        #     self.interrupt_alternate = not self.interrupt_alternate
        #     self.count_inst = 0
        if self.cycles >= 16667:
            self.cycles -= 16667
            if self.INTERRUPT:
                if self.interrupt_alternate == True:
                    self.callInterrupt(0x08)
                else:
                    self.callInterrupt(0x10)
                self.interrupt_alternate = not self.interrupt_alternate
        if self.A>0xFF or self.B>0xFF or self.C>0xFF or self.D>0xFF or self.E>0xFF or self.H>0xFF or self.L>0xFF:
            print self.count
            self.information()
            print "INST"

            exit(1)

        # if self.HL == 65286:
        #     print "HL changed", self.count, self.current_inst
        #     exit(1)

        # if self._memory[8310] != self.prevHL:
            # print "fuck", self.count, self.current_inst
            # exit(1)
        # self.prevHL = self._memory[8310]

        # if self._memory[0x20c0] != self.prev:
        #     print "memory changed:", self._memory[0x20c0]
        # self.prev = self._memory[0x20c0]
        # if self.HL !=self.prev:
        #     print "fuck", self.HL
        # self.prev = self.HL
        if self.HL == 0x4017:
            print self.count

    def callInterrupt(self, address):
        # self.INTERRUPT = False
        self.stackPush(self.PC)
        self.PC = address

    def INST_NOP(self):
        """do nothing"""
        self.cycles += 4

    def INST_toImplement(self):
        print str(self.current_inst) + " is not implement."
        exit(1)

    def INST_JMP(self):  # JMP group     size 3
        condition = True
        data_16 = self.FetchRomNext2Bytes()  # fetch the next 2 data
        if 0xC3 == self.current_inst:  # JMP
            self.PC = data_16
            self.cycles += 10
            return
        elif self.current_inst == 0xC2:  # JNZ
            condition = not self.ZERO  # if not z
        elif self.current_inst == 0xCA:  # JZ
            condition = self.ZERO  # if z
        elif self.current_inst == 0xD2:  # JNC
            condition = not self.CARRY  # if not c
        elif self.current_inst == 0xDA:  # JC
            condition = self.CARRY  # if C
        elif self.current_inst == 0xF2:  # JP
            condition = not self.SIGN  # if P
        elif self.current_inst == 0xFA:  # JM
            condition = self.SIGN  # if not P(M)

        self.cycles += 10

        if condition:
            self.PC = data_16
            self.cycles += 5

    def INST_LXI_BC(self):  # B <- byte 3, C <- byte 2
        self.setBC(self.FetchRomNext2Bytes())
        self.cycles += 10

    def INST_LXI_DE(self):  # D <- byte 3, E <- byte 2
        self.setDE(self.FetchRomNext2Bytes())
        self.cycles += 10

    def INST_LXI_HL(self):  # H <- byte 3, L <- byte 2
        self.setHL(self.FetchRomNext2Bytes())
        self.cycles += 10

    def INST_LXI_SP(self):  # SP.hi <- byte 3, SP.lo <- byte 2
        self.SP = self.FetchRomNext2Bytes()
        self.cycles += 10

    def INST_MVI_A(self):  # A <- byte 2
        self.A = self.FetchRomNext1Byte()
        self.cycles += 7

    def INST_MVI_B(self):  # B <- byte2
        self.setB(self.FetchRomNext1Byte())
        self.cycles += 7

    def INST_MVI_C(self):  # C <- byte2
        self.setC(self.FetchRomNext1Byte())
        self.cycles += 7

    def INST_MVI_D(self):  # D <- byte2
        self.setD(self.FetchRomNext1Byte())
        self.cycles += 7

    def INST_MVI_E(self):  # E <- byte2
        self.setE(self.FetchRomNext1Byte())
        self.cycles += 7

    def INST_MVI_H(self):  # H <- byte2
        self.setH(self.FetchRomNext1Byte())
        self.cycles += 7

    def INST_MVI_L(self):  # L <- byte2
        self.setL(self.FetchRomNext1Byte())
        self.cycles += 7

    def INST_MVI_M(self):
        self.writeByte(self.HL, self.FetchRomNext1Byte())
        self.cycles += 10

    def INST_CALL(self):
        condition = True
        data_16 = self.FetchRomNext2Bytes()

        if self.current_inst == 0xCD:  # CALL adr	3		(SP-1)<-PC.hi;(SP-2)<-PC.lo;SP<-SP+2;PC=adr
            self.stackPush(self.PC)
            self.PC = data_16
            self.cycles += 17
            return
        elif self.current_inst == 0xC4:  # if NZ, CALL adr
            condition = not self.ZERO
        elif self.current_inst == 0xCC:
            condition = self.ZERO
        elif self.current_inst == 0xD4:
            condition = not self.CARRY
        elif self.current_inst == 0xDC:
            condition = self.CARRY

        self.cycles += 11

        if condition:
            self.stackPush(self.PC)
            self.PC = data_16
            self.cycles += 7

    def INST_RET(self):
        condition = True

        if self.current_inst == 0xC9:
            self.PC = self.stackPop()
            self.cycles += 10
            return
        elif self.current_inst == 0xC0:
            condition = not self.ZERO
        elif self.current_inst == 0xC8:
            condition = self.ZERO
        elif self.current_inst == 0xD0:
            condition = not self.CARRY
        elif self.current_inst == 0xD8:
            condition = self.CARRY

        self.cycles += 5
        if condition:
            self.PC = self.stackPop()
            self.cycles += 6

    def INST_LDA(self):
        if self.current_inst == 0x0A:
            source = self.BC
            self.cycles += 7
        elif self.current_inst == 0x1A:
            source = self.DE
            self.cycles += 7
        elif self.current_inst == 0x3A:
            source = self.FetchRomNext2Bytes()
            self.cycles += 13
        else:
            source = 0
            print "LDA problem"
            exit(1)

        self.A = self.readByte(source)

    def INST_PUSH(self):
        if self.current_inst == 0xC5:
            value = self.BC
        elif self.current_inst == 0xD5:
            value = self.DE
        elif self.current_inst == 0xE5:
            value = self.HL
        elif self.current_inst == 0xF5:
            value = (self.A << 8) + 0x02
            value += 0x80 if self.SIGN else 0
            value += 0x40 if self.ZERO else 0
            value += 0x10 if self.HALFCARRY else 0
            value += 0x04 if self.PARITY else 0
            value += 0x01 if self.CARRY else 0
        else:
            value = 0
            print "Instruction Push Error: " + str(self.current_inst)
            exit(1)

        self.stackPush(value)
        self.cycles += 11

    def INST_POP_BC(self):
        self.setBC(self.stackPop())
        self.cycles += 10

    def INST_POP_DE(self):
        self.setDE(self.stackPop())
        self.cycles += 10

    def INST_POP_HL(self):
        self.setHL(self.stackPop())
        self.cycles += 10

    def INST_POP_FLAGS(self):
        value = self.stackPop()
        self.A = value >> 8
        self.SIGN = True if (value & 0x80) > 0 else False
        self.ZERO = True if (value & 0x40) > 0 else False
        self.HALFCARRY = True if (value & 0x10) > 0 else False
        self.PARITY = True if (value & 0x04) > 0 else False
        self.CARRY = True if (value & 0x01) > 0 else False
        self.cycles += 10

    def INST_MOVHL(self):
        if self.current_inst == 0x77:
            self.writeByte(self.HL, self.A)
        elif self.current_inst == 0x70:
            self.writeByte(self.HL, self.B)
        elif self.current_inst == 0x71:
            self.writeByte(self.HL, self.C)
        elif self.current_inst == 0x72:
            self.writeByte(self.HL, self.D)
        elif self.current_inst == 0x73:
            self.writeByte(self.HL, self.E)
        elif self.current_inst == 0x74:
            self.writeByte(self.HL, self.H)
        elif self.current_inst == 0x75:
            self.writeByte(self.HL, self.L)

        self.cycles += 7

    def INST_MOV(self):
        if self.current_inst == 0x7F:
            self.A = self.A
        elif self.current_inst == 0x78:
            self.A = self.B
        elif self.current_inst == 0x79:
            self.A = self.C
        elif self.current_inst == 0x7A:
            self.A = self.D
        elif self.current_inst == 0x7B:
            self.A = self.E
        elif self.current_inst == 0x7C:
            self.A = self.H
        elif self.current_inst == 0x7D:
            self.A = self.L
        elif self.current_inst == 0x7E:
            self.A = self.readByte(self.HL)
            self.cycles += 2

        elif self.current_inst == 0x47:
            self.setB(self.A)
        elif self.current_inst == 0x40:
            self.B = self.B
        elif self.current_inst == 0x41:
            self.setB(self.C)
        elif self.current_inst == 0x42:
            self.setB(self.D)
        elif self.current_inst == 0x43:
            self.setB(self.E)
        elif self.current_inst == 0x44:
            self.setB(self.H)
        elif self.current_inst == 0x45:
            self.setB(self.L)
        elif self.current_inst == 0x46:
            self.setB(self.readByte(self.HL))
            self.cycles += 2

        elif self.current_inst == 0x4F:
            self.setC(self.A)
        elif self.current_inst == 0x48:
            self.setC(self.B)
        elif self.current_inst == 0x49:
            self.C = self.C
        elif self.current_inst == 0x4A:
            self.setC(self.D)
        elif self.current_inst == 0x4B:
            self.setC(self.E)
        elif self.current_inst == 0x4C:
            self.setC(self.H)
        elif self.current_inst == 0x4D:
            self.setC(self.L)
        elif self.current_inst == 0x4E:
            # print "HL:", self.HL
            # print "4E:", self.HL
            self.setC(self.readByte(self.HL))
            self.cycles += 2

        elif self.current_inst == 0x57:
            self.setD(self.A)
        elif self.current_inst == 0x50:
            self.setD(self.B)
        elif self.current_inst == 0x51:
            self.setD(self.C)
        elif self.current_inst == 0x52:
            self.D = self.D
        elif self.current_inst == 0x53:
            self.setD(self.E)
        elif self.current_inst == 0x54:
            self.setD(self.H)
        elif self.current_inst == 0x55:
            self.setD(self.L)
        elif self.current_inst == 0x56:
            self.setD(self.readByte(self.HL))
            self.cycles  += 2

        elif self.current_inst == 0x5F:
            self.setE(self.A)
        elif self.current_inst == 0x58:
            self.setE(self.B)
        elif self.current_inst == 0x59:
            self.setE(self.C)
        elif self.current_inst == 0x5A:
            self.setE(self.D)
        elif self.current_inst == 0x5B:
            self.E = self.E
        elif self.current_inst == 0x5C:
            self.setE(self.H)
        elif self.current_inst == 0x5D:
            self.setE(self.L)
        elif self.current_inst == 0x5E:
            self.setE(self.readByte(self.HL))
            self.cycles += 2

        elif self.current_inst == 0x67:
            self.setH(self.A)
        elif self.current_inst == 0x60:
            self.setH(self.B)
        elif self.current_inst == 0x61:
            self.setH(self.C)
        elif self.current_inst == 0x62:
            self.setH(self.D)
        elif self.current_inst == 0x63:
            self.setH(self.E)
        elif self.current_inst == 0x64:
            self.H = self.H
        elif self.current_inst == 0x65:
            self.setH(self.L)
        elif self.current_inst == 0x66:
            self.setH(self.readByte(self.HL))
            self.cycles += 2

        elif self.current_inst == 0x6F:
            self.setL(self.A)
        elif self.current_inst == 0x68:
            self.setL(self.B)
        elif self.current_inst == 0x69:
            self.setL(self.C)
        elif self.current_inst == 0x6A:
            self.setL(self.D)
        elif self.current_inst == 0x6B:
            self.setL(self.E)
        elif self.current_inst == 0x6C:
            self.setL(self.H)
        elif self.current_inst == 0x6D:
            self.L = self.L
        elif self.current_inst == 0x6E:
            self.setL(self.readByte(self.HL))
            self.cycles += 2
        else:
            print "NO matching rules"
            exit(1)

        self.cycles += 5

    def INST_INX(self):
        """"""
        if self.current_inst == 0x03:
            self.setBC(self.BC + 1)
            self.cycles += 6
        elif self.current_inst == 0x13:
            self.setDE(self.DE + 1)
            self.cycles += 6
        elif self.current_inst == 0x23:
            self.setHL(self.HL+1)
            self.cycles += 6
        elif self.current_inst == 0x33:
            self.SP = (self.SP + 1) & 0xFF
            self.cycles += 6

    def INST_DAD_BC(self):
        """"""
        self.addHL(self.BC)
        self.cycles += 11

    def INST_DAD_DE(self):
        """"""
        self.addHL(self.DE)
        self.cycles += 11

    def INST_DAD_HL(self):
        """"""
        self.addHL(self.HL)
        self.cycles += 11

    def INST_DAD_SP(self):
        """"""
        self.addHL(self.SP)
        self.cycles += 11

    def INST_DCX(self):
        """"""
        if self.current_inst == 0x0B:
            self.setBC(self.BC - 1)
            self.cycles += 6
        elif self.current_inst == 0x1B:
            self.setDE(self.DE - 1)
            self.cycles += 6
        elif self.current_inst == 0x2B:
            self.setHL(self.HL - 1)
            self.cycles += 6
        elif self.current_inst == 0x3B:
            self.SP = (self.SP - 1) & 0xFF
            self.cycles += 6
        else:
            print "DCX ERROR"
            exit(1)

    def INST_DEC(self):
        if self.current_inst == 0x3D:
            self.A = self.Dec(self.A)
            self.cycles += 5
        elif self.current_inst == 0x05:
            self.setB(self.Dec(self.B))
            self.cycles += 5
        elif self.current_inst == 0x0D:
            self.setC(self.Dec(self.C))
            self.cycles += 5
        elif self.current_inst == 0x15:
            self.setD(self.Dec(self.D))
            self.cycles += 5
        elif self.current_inst == 0x1D:
            self.setE(self.Dec(self.E))
            self.cycles += 5
        elif self.current_inst == 0x25:
            self.setH(self.Dec(self.H))
            self.cycles += 5
        elif self.current_inst == 0x2D:
            self.setL(self.Dec(self.L))
            self.cycles += 5
        elif self.current_inst == 0x35:
            self.writeByte(self.HL, self.Dec(self.readByte(self.HL)))
            self.cycles += 10
        else:
            print "DEC ERROR"
            exit(1)

    def INST_INR(self):
        if self.current_inst == 0x3C:
            self.A = self.Inc(self.A)
            self.cycles += 5
        elif self.current_inst == 0x04:
            self.setB(self.Inc(self.B))
            self.cycles += 5
        elif self.current_inst == 0x0C:
            self.setC(self.Inc(self.C))
            self.cycles += 5
        elif self.current_inst == 0x14:
            self.setD(self.Inc(self.D))
            self.cycles += 5
        elif self.current_inst == 0x1C:
            self.setE(self.Inc(self.E))
            self.cycles += 5
        elif self.current_inst == 0x24:
            self.setH(self.Inc(self.H))
            self.cycles += 5
        elif self.current_inst == 0x2C:
            self.setL(self.Inc(self.L))
            self.cycles += 5
        elif self.current_inst == 0x34:
            self.writeByte(self.HL, self.Inc(self.readByte(self.HL)))
            self.cycles += 10

    def INST_AND(self):
        if self.current_inst == 0xA7:
            self.And(self.A)
        elif self.current_inst == 0xA0:
            self.And(self.B)
        elif self.current_inst == 0xA1:
            self.And(self.C)
        elif self.current_inst == 0xA2:
            self.And(self.D)
        elif self.current_inst == 0xA3:
            self.And(self.E)
        elif self.current_inst == 0xA4:
            self.And(self.H)
        elif self.current_inst == 0xA5:
            self.And(self.L)
        elif self.current_inst == 0xA6:
            self.And(self.readByte(self.HL))
            self.cycles += 3
        elif self.current_inst == 0xE6:
            self.And(self.FetchRomNext1Byte())
            self.cycles += 3

        self.cycles += 4

    def INST_XOR(self):
        if self.current_inst == 0xAF:
            self.Xor(self.A)
        elif self.current_inst == 0xA8:
            self.Xor(self.B)
        elif self.current_inst == 0xA9:
            self.Xor(self.C)
        elif self.current_inst == 0xAA:
            self.Xor(self.D)
        elif self.current_inst == 0xAB:
            self.Xor(self.E)
        elif self.current_inst == 0xAC:
            self.Xor(self.H)
        elif self.current_inst == 0xAD:
            self.Xor(self.L)
        elif self.current_inst == 0xAE:
            self.Xor(self.readByte(self.HL))
            self.cycles += 3
        elif self.current_inst == 0xEE:
            self.Xor(self.FetchRomNext1Byte())
            self.cycles += 3

        self.cycles += 4

    def INST_OR(self):
        if self.current_inst == 0xB7:
            self.Or(self.A)
        elif self.current_inst == 0xB0:
            self.Or(self.B)
        elif self.current_inst == 0xB1:
            self.Or(self.C)
        elif self.current_inst == 0xB2:
            self.Or(self.D)
        elif self.current_inst == 0xB3:
            self.Or(self.E)
        elif self.current_inst == 0xB4:
            self.Or(self.H)
        elif self.current_inst == 0xB5:
            self.Or(self.L)
        elif self.current_inst == 0xB6:
            self.Or(self.readByte(self.HL))
            self.cycles += 3
        elif self.current_inst == 0xF6:
            self.Or(self.FetchRomNext1Byte())
            self.cycles += 3

        self.cycles += 4

    def INST_ADD(self):
        if self.current_inst == 0x87:
            self.Add(self.A)
        elif self.current_inst == 0x80:
            self.Add(self.B)
        elif self.current_inst == 0x81:
            self.Add(self.C)
        elif self.current_inst == 0x82:
            self.Add(self.D)
        elif self.current_inst == 0x83:
            self.Add(self.E)
        elif self.current_inst == 0x84:
            self.Add(self.H)
        elif self.current_inst == 0x85:
            self.Add(self.L)
        elif self.current_inst == 0x86:
            self.Add(self.readByte(self.HL))
            self.cycles += 3
        elif self.current_inst == 0xC6:
            self.Add(self.FetchRomNext1Byte())
            self.cycles += 3

        self.cycles += 4

    def INST_ADC(self):
        carry = 1 if self.CARRY else 0
        if self.current_inst == 0x8F:
            self.Add(self.A, carry)
        elif self.current_inst == 0x88:
            self.Add(self.B, carry)
        elif self.current_inst == 0x89:
            self.Add(self.C, carry)
        elif self.current_inst == 0x8A:
            self.Add(self.D, carry)
        elif self.current_inst == 0x8B:
            self.Add(self.E, carry)
        elif self.current_inst == 0x8C:
            self.Add(self.H, carry)
        elif self.current_inst == 0x8D:
            self.Add(self.L, carry)
        elif self.current_inst == 0x8E:
            self.Add(self.readByte(self.HL), carry)
            self.cycles += 3
        elif self.current_inst == 0xCE:
            self.Add(self.FetchRomNext1Byte(), carry)
            self.cycles += 3

        self.cycles += 4

    def INST_SUB(self):
        if self.current_inst == 0x97:
            self.Sub(self.A)
        elif self.current_inst == 0x90:
            self.Sub(self.B)
        elif self.current_inst == 0x91:
            self.Sub(self.C)
        elif self.current_inst == 0x92:
            self.Sub(self.D)
        elif self.current_inst == 0x93:
            self.Sub(self.E)
        elif self.current_inst == 0x94:
            self.Sub(self.H)
        elif self.current_inst == 0x95:
            self.Sub(self.L)
        elif self.current_inst == 0x96:
            self.Sub(self.readByte(self.HL))
            self.cycles += 3
        elif self.current_inst == 0xD6:
            self.Sub(self.FetchRomNext1Byte())
            self.cycles += 3

        self.cycles += 4

    def INST_SBBI(self):
        data = self.FetchRomNext1Byte()
        carry = 1 if self.CARRY else 0
        self.Sub(data, carry=carry)
        self.cycles += 7

    def INST_CMP(self):
        if self.current_inst == 0xBF:
            value = self.A
        elif self.current_inst == 0xB8:
            value = self.B
        elif self.current_inst == 0xB9:
            value = self.C
        elif self.current_inst == 0xBA:
            value = self.D
        elif self.current_inst == 0xBB:
            value = self.E
        elif self.current_inst == 0xBC:
            value = self.H
        elif self.current_inst == 0xBD:
            value = self.L
        elif self.current_inst == 0xBE:
            value = self.readByte(self.HL)
            self.cycles += 3
        elif self.current_inst == 0xFE:
            value = self.FetchRomNext1Byte()
            self.cycles += 3
        else:
            print "CMP ERROR"
            exit(1)
        self.CmpSub(value)

        self.cycles += 4

    def INST_XCHG(self):
        """"""
        temp = self.HL
        self.setHL(self.DE)
        self.setDE(temp)
        self.cycles += 4

    def INST_XTHL(self):
        temp = self.H
        self.setH(self.readByte(self.SP+1))
        self.writeByte(self.SP+1, temp)

        temp = self.L
        self.setL(self.readByte(self.SP))
        self.writeByte(self.SP, temp)

        self.cycles += 4

    def INST_OUTP(self):    # TODO IO
        port = self.FetchRomNext1Byte()
        self.io.OutPutPort(port, self.A)
        self.cycles += 10

    def INST_INP(self):
        port = self.FetchRomNext1Byte()
        self.A = self.io.InPutPort(port)
        if self.A > 255:
            print "Input Error"
        self.cycles += 10

    def INST_PCHL(self):
        self.PC = self.HL
        self.cycles += 4

    def INST_RST(self):
        address = 0
        if self.current_inst == 0xC7:
            address = 0x00
        elif self.current_inst == 0xCF:
            address = 0x08
        elif self.current_inst == 0xD7:
            address = 0x10
        elif self.current_inst == 0xDF:
            address = 0x18
        elif self.current_inst == 0xE7:
            address = 0x20
        elif self.current_inst == 0xEF:
            address = 0x28
        elif self.current_inst == 0xF7:
            address = 0x30
        elif self.current_inst == 0xFF:
            address = 0x38

        self.stackPush(self.PC)
        self.PC = address

        self.cycles += 11

    def INST_RLC(self):
        """"""
        self.CARRY = True if (self.A >> 7) == 1 else False
        self.A = ((self.A << 1) & 0xFF) + (self.A >> 7)
        self.cycles += 4

    def INST_RAL(self):
        """"""
        temp = self.A
        self.A = (self.A << 1) & 0xFF
        self.A += 1 if self.CARRY else 0
        self.CARRY = True if (temp & 0x80) > 0 else False
        self.cycles += 4

    def INST_RRC(self):
        """"""
        self.CARRY = True if (self.A & 0x01) == 1 else False
        self.A = ((self.A >> 1) & 0xFF) + ((self.A << 7) & 0xFF)
        self.cycles += 4

    def INST_RAR(self):
        """"""
        temp = self.A
        self.A = (self.A >> 1)
        self.A += 0x80 if self.CARRY else 0
        self.CARRY = True if (temp & 0x01) > 0 else False
        self.cycles += 4

    def INST_RIM(self):     # TODO nothing?
        print "Unimplemtnyed"
        pass

    def INST_STA(self):
        if self.current_inst == 0x02:
            self.writeByte(self.BC, self.A)
            self.cycles += 7
        elif self.current_inst == 0x12:
            self.writeByte(self.DE, self.A)
            self.cycles += 7
        elif self.current_inst == 0x32:     # TODO more INST than manual
            self.writeByte(self.FetchRomNext2Bytes(), self.A)
            self.cycles += 13
        else:
            print "no matching rules"
            exit(1)

    def INST_DI(self):
        self.INTERRUPT = False
        self.cycles += 4

    def INST_EI(self):
        self.INTERRUPT = True
        self.cycles += 4

    def INST_STC(self):
        """C<-1"""
        self.CARRY = True
        self.cycles += 4

    def INST_CMC(self):
        """C<-!C"""
        self.CARRY = not self.CARRY
        self.cycles += 4

    def INST_LHLD(self):
        a = self.FetchRomNext2Bytes()
        # print self.read2Bytes(a)
        self.setHL(self.read2Bytes(a))
        # print "now:", self.HL
        self.cycles += 16

    def INST_SHLD(self):
        self.write2Bytes(self.FetchRomNext2Bytes(), self.HL)
        self.cycles += 16

    def INST_DAA(self):
        """BCD"""
        if (self.A & 0x0F) > 9 or self.HALFCARRY:
            self.A += 0x06
            self.HALFCARRY = True

        if (self.A > 0x9F) or self.CARRY:
            self.A += 0x60
            self.CARRY = True

        self.ZERO = True if self.A == 0 else False
        self.SIGN = True if (self.A & 0x80) > 0 else False
        self.PARITY = True if self.A % 2 == 0 else False
        self.cycles += 4

    def INST_CMA(self):
        """A<-~A"""
        self.A = (~self.A) & 0xFF
        self.cycles += 4

    @staticmethod
    def INST_HLT():
        print "HLT"
        exit(0)

    def setB(self, data):
        self.B = data & 0xFF
        self.BC = (self.B << 8) + self.C

    def setC(self, data):
        self.C = data & 0xFF
        self.BC = (self.B << 8) + self.C

    def setD(self, data):
        self.D = data & 0xFF
        self.DE = (self.D << 8) + self.E

    def setE(self, data):
        self.E = data & 0xFF
        self.DE = (self.D << 8) + self.E

    def setH(self, data):
        self.H = data & 0xFF
        self.HL = (self.H << 8) + self.L

    def setL(self, data):
        self.L = data & 0xFF
        self.HL = (self.H << 8) + self.L

    def setBC(self, data):
        self.BC = data & 0xFFFF
        self.B = self.BC >> 8
        self.C = self.BC & 0xFF

    def setDE(self, data):
        self.DE = data & 0xFFFF
        self.D = self.DE >> 8
        self.E = self.DE & 0xFF

    def setHL(self, data):
        self.HL = data & 0xFFFF
        self.H = self.HL >> 8
        self.L = self.HL & 0xFF

    def addHL(self, data):
        value = self.HL + data
        self.setHL(value)
        # self.CARRY = True if value > 0xFFFF else False
        if value > 0xFFFF:
            self.CARRY = True

    def Inc(self, data):
        """i++"""
        value = (data + 1) & 0xFF
        self.ZERO = True if value == 0 else False
        self.SIGN = True if (value & 0x80) > 0 else False   # TODO may error
        self.HALFCARRY = True if data == 0x0F else False    # TODO may error
        self.PARITY = True if value % 2 == 0 else False
        return value

    def Dec(self, data):
        """i--"""
        value = (data - 1) & 0xFF
        self.HALFCARRY = True if (data & 0x0F) == 0 else False    # TODO may error
        self.SIGN = True if (value & 0x80) > 0 else False
        self.ZERO = True if value == 0 else False
        self.PARITY = True if value % 2 == 0 else False
        return value

    def And(self, value):
        """"""
        if value > 0x0FF:
            print "And in value error"
            exit(1)
        temp = self.A
        self.A = (self.A & value) & 0xFF
        self.CARRY = False
        self.ZERO = True if self.A == 0 else False
        self.SIGN = True if self.A & 0x80 > 0 else False
        self.PARITY = True if self.A % 2 == 0 else False
        # self.HALFCARRY = True if (self.A%10) != ((temp&0x0F) & (value&0x0F)) else False
        self.HALFCARRY = False if ((temp & 8)>>3) | ((value & 8)>>3) > 0 else True


    def Xor(self, value):
        """"""
        temp = self.A
        self.A = self.A ^ value
        self.CARRY = False
        self.ZERO = True if self.A == 0 else False
        self.SIGN = True if self.A & 0x80 > 0 else False
        self.PARITY = True if self.A % 2 == 0 else False
        # self.HALFCARRY = True if (self.A%10) != ((temp&0x0F) ^ (value&0x0F)) else False
        self.HALFCARRY = False

    def Or(self, value):
        """"""
        self.A = self.A | value
        self.CARRY = False
        self.HALFCARRY = False  # js8080
        self.ZERO = True if self.A == 0 else False
        self.SIGN = True if self.A & 0x80 > 0 else False
        self.PARITY = True if self.A % 2 == 0 else False

    def Add(self, in_value, carry=0):
        """"""
        value = self.A + in_value + carry
        # self.HALFCARRY = True if (self.A & 0x0F) + (in_value & 0x0F) + carry > 0x0F else False
        self.HALFCARRY = True if (((self.A ^ value) ^ in_value) & 0x10) > 0 else False
        self.A = value & 0xFF
        self.CARRY = True if value > 255 or value < 0 else False
        self.SIGN = True if self.A & 0x80 > 0 else False
        self.ZERO = True if self.A == 0 else False
        self.PARITY = True if self.A % 2 == 0 else False

    def Sub(self, in_value, carry=0):
        """"""
        # in_value = ~(in_value + carry) & 0xFF # TODO may get error
        # value = self.A + in_value + self.CARRY
        value = self.A - in_value + carry
        x = value & 0xFF
        # self.HALFCARRY = True if (self.A & 0x0F) + (in_value & 0x0F) + carry > 0x0F else False
        self.HALFCARRY = True if ((self.A ^ value) ^ in_value) & 0x10 > 0 else False
        self.CARRY = True if value > 255 or value < 0 else  False
        self.A = value & 0xFF
        self.SIGN = True if x & 0x80 > 0 else False
        self.ZERO = True if x == 0 else False
        self.PARITY = True if x % 2== 0 else False

    def CmpSub(self, in_value):        # TODO
        value = self.A - in_value
        self.CARRY = True if value >= 255 or value < 0 else False
        self.HALFCARRY = True if ((self.A ^ value) ^ in_value) & 0x10 > 0 else False
        self.ZERO = True if value & 0xFF== 0 else False
        self.SIGN = True if (value & 0x80) > 0 else False
        self.PARITY = True if value%2==0 else False

    def stackPush(self, data):
        if data > 0xFFFF:
            print "PUSH ERROR DATA:", data
            print "Count:", self.count
            exit(1)
        self.SP -= 2
        self.write2Bytes(self.SP, data)

    def stackPop(self):
        address = self.read2Bytes(self.SP)
        self.SP += 2
        return address

    def readByte(self, address):
        if self._memory[address] > 0xFF:
            print "readByte Error"
            exit(1)
        return self._memory[address]

    def read2Bytes(self, address):
        return (self._memory[address + 1] << 8) + self._memory[address]

    def writeByte(self, address, data):
        if data > 0xFF:
            print "writeByte Error:"
            exit(1)
        # if address > 16384:
            # print "address error:"
            # exit(1)
        self._memory[address] = data & 0xFF

    def write2Bytes(self, address, data):
        if data > 0xFFFF:
            print "write2Bytes Error:"
            exit(1)
        self._memory[address + 1] = data >> 8
        self._memory[address] = data & 0xFF

    def FetchRomNext1Byte(self):  # read next 8bit
        data = self._memory[self.PC]
        self.PC += 1
        return data

    def FetchRomNext2Bytes(self):  # read next 16bit
        """byte2+byte1"""
        data = (self._memory[self.PC + 1] << 8) + self._memory[self.PC]  # notice the endian
        self.PC += 2
        return data

    def InitMap(self):
        for i in range(len(self._memory)):
            if self._memory[i] == 0x00:
                self.mappingTable[self._memory[i]] = self.INST_NOP
            elif self._memory[i] == 0x01:
                self.mappingTable[self._memory[i]] = self.INST_LXI_BC
            elif self._memory[i] == 0x02:
                self.mappingTable[self._memory[i]] = self.INST_STA
            elif self._memory[i] == 0x03:
                self.mappingTable[self._memory[i]] = self.INST_INX
            elif self._memory[i] == 0x04:
                self.mappingTable[self._memory[i]] = self.INST_INR
            elif self._memory[i] == 0x05:
                self.mappingTable[self._memory[i]] = self.INST_DEC
            elif self._memory[i] == 0x06:
                self.mappingTable[self._memory[i]] = self.INST_MVI_B
            elif self._memory[i] == 0x07:
                self.mappingTable[self._memory[i]] = self.INST_RLC
            elif self._memory[i] == 0x08:
                self.mappingTable[self._memory[i]] = self.INST_NOP  # TODO nothing
            elif self._memory[i] == 0x09:
                self.mappingTable[self._memory[i]] = self.INST_DAD_BC
            elif self._memory[i] == 0x0A:
                self.mappingTable[self._memory[i]] = self.INST_LDA
            elif self._memory[i] == 0x0B:
                self.mappingTable[self._memory[i]] = self.INST_DCX
            elif self._memory[i] == 0x0C:
                self.mappingTable[self._memory[i]] = self.INST_INR
            elif self._memory[i] == 0x0D:
                self.mappingTable[self._memory[i]] = self.INST_DEC
            elif self._memory[i] == 0x0E:
                self.mappingTable[self._memory[i]] = self.INST_MVI_C
            elif self._memory[i] == 0x0F:
                self.mappingTable[self._memory[i]] = self.INST_RRC
            elif self._memory[i] == 0x10:
                self.mappingTable[self._memory[i]] = self.INST_NOP  # TODO nothing
            elif self._memory[i] == 0x11:
                self.mappingTable[self._memory[i]] = self.INST_LXI_DE
            elif self._memory[i] == 0x12:
                self.mappingTable[self._memory[i]] = self.INST_STA
            elif self._memory[i] == 0x13:
                self.mappingTable[self._memory[i]] = self.INST_INX
            elif self._memory[i] == 0x14:
                self.mappingTable[self._memory[i]] = self.INST_INR
            elif self._memory[i] == 0x15:
                self.mappingTable[self._memory[i]] = self.INST_DEC
            elif self._memory[i] == 0x16:
                self.mappingTable[self._memory[i]] = self.INST_MVI_D
            elif self._memory[i] == 0x17:
                self.mappingTable[self._memory[i]] = self.INST_RAL
            elif self._memory[i] == 0x18:
                self.mappingTable[self._memory[i]] = self.INST_NOP  # TODO nothing
            elif self._memory[i] == 0x19:
                self.mappingTable[self._memory[i]] = self.INST_DAD_DE
            elif self._memory[i] == 0x1A:
                self.mappingTable[self._memory[i]] = self.INST_LDA
            elif self._memory[i] == 0x1B:
                self.mappingTable[self._memory[i]] = self.INST_DCX
            elif self._memory[i] == 0x1C:
                self.mappingTable[self._memory[i]] = self.INST_INR
            elif self._memory[i] == 0x1D:
                self.mappingTable[self._memory[i]] = self.INST_DEC
            elif self._memory[i] == 0x1E:
                self.mappingTable[self._memory[i]] = self.INST_MVI_E
            elif self._memory[i] == 0x1F:
                self.mappingTable[self._memory[i]] = self.INST_RAR
            elif self._memory[i] == 0x20:
                self.mappingTable[self._memory[i]] = self.INST_RIM
            elif self._memory[i] == 0x21:
                self.mappingTable[self._memory[i]] = self.INST_LXI_HL
            elif self._memory[i] == 0x22:
                self.mappingTable[self._memory[i]] = self.INST_SHLD
            elif self._memory[i] == 0x23:
                self.mappingTable[self._memory[i]] = self.INST_INX
            elif self._memory[i] == 0x24:
                self.mappingTable[self._memory[i]] = self.INST_INR
            elif self._memory[i] == 0x25:
                self.mappingTable[self._memory[i]] = self.INST_DEC
            elif self._memory[i] == 0x26:
                self.mappingTable[self._memory[i]] = self.INST_MVI_H
            elif self._memory[i] == 0x27:
                self.mappingTable[self._memory[i]] = self.INST_DAA
            elif self._memory[i] == 0x28:
                self.mappingTable[self._memory[i]] = self.INST_NOP  # nothing
            elif self._memory[i] == 0x29:
                self.mappingTable[self._memory[i]] = self.INST_DAD_HL
            elif self._memory[i] == 0x2A:
                self.mappingTable[self._memory[i]] = self.INST_LHLD
            elif self._memory[i] == 0x2B:
                self.mappingTable[self._memory[i]] = self.INST_DCX
            elif self._memory[i] == 0x2C:
                self.mappingTable[self._memory[i]] = self.INST_INR
            elif self._memory[i] == 0x2D:
                self.mappingTable[self._memory[i]] = self.INST_DEC
            elif self._memory[i] == 0x2E:
                self.mappingTable[self._memory[i]] = self.INST_MVI_L
            elif self._memory[i] == 0x2F:
                self.mappingTable[self._memory[i]] = self.INST_CMA
            elif self._memory[i] == 0x30:
                self.mappingTable[self._memory[i]] = self.INST_NOP  # TODO special
            elif self._memory[i] == 0x31:
                self.mappingTable[self._memory[i]] = self.INST_LXI_SP
            elif self._memory[i] == 0x32:
                self.mappingTable[self._memory[i]] = self.INST_STA
            elif self._memory[i] == 0x33:
                self.mappingTable[self._memory[i]] = self.INST_INX
            elif self._memory[i] == 0x34:
                self.mappingTable[self._memory[i]] = self.INST_INR
            elif self._memory[i] == 0x35:
                self.mappingTable[self._memory[i]] = self.INST_DEC
            elif self._memory[i] == 0x36:
                self.mappingTable[self._memory[i]] = self.INST_MVI_M
            elif self._memory[i] == 0x37:
                self.mappingTable[self._memory[i]] = self.INST_STC
            elif self._memory[i] == 0x38:
                self.mappingTable[self._memory[i]] = self.INST_NOP  # TODO nothing
            elif self._memory[i] == 0x39:
                self.mappingTable[self._memory[i]] = self.INST_DAD_SP
            elif self._memory[i] == 0x3A:
                self.mappingTable[self._memory[i]] = self.INST_LDA
            elif self._memory[i] == 0x3B:
                self.mappingTable[self._memory[i]] = self.INST_DCX
            elif self._memory[i] == 0x3C:
                self.mappingTable[self._memory[i]] = self.INST_INR
            elif self._memory[i] == 0x3D:
                self.mappingTable[self._memory[i]] = self.INST_DEC
            elif self._memory[i] == 0x3E:
                self.mappingTable[self._memory[i]] = self.INST_MVI_A
            elif self._memory[i] == 0x3F:
                self.mappingTable[self._memory[i]] = self.INST_CMC
            elif self._memory[i] == 0x40:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x41:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x42:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x43:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x44:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x45:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x46:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x47:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x48:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x49:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x4A:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x4B:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x4C:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x4D:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x4E:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x4F:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x50:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x51:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x52:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x53:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x54:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x55:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x56:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x57:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x58:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x59:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x5A:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x5B:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x5C:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x5D:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x5E:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x5F:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x60:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x61:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x62:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x63:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x64:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x65:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x66:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x67:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x68:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x69:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x6A:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x6B:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x6C:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x6D:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x6E:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x6F:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x70:
                self.mappingTable[self._memory[i]] = self.INST_MOVHL
            elif self._memory[i] == 0x71:
                self.mappingTable[self._memory[i]] = self.INST_MOVHL
            elif self._memory[i] == 0x72:
                self.mappingTable[self._memory[i]] = self.INST_MOVHL
            elif self._memory[i] == 0x73:
                self.mappingTable[self._memory[i]] = self.INST_MOVHL
            elif self._memory[i] == 0x74:
                self.mappingTable[self._memory[i]] = self.INST_MOVHL
            elif self._memory[i] == 0x75:
                self.mappingTable[self._memory[i]] = self.INST_MOVHL
            elif self._memory[i] == 0x76:
                self.mappingTable[self._memory[i]] = self.INST_HLT  # TODO HLT
            elif self._memory[i] == 0x77:
                self.mappingTable[self._memory[i]] = self.INST_MOVHL
            elif self._memory[i] == 0x78:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x79:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x7A:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x7B:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x7C:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x7D:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x7E:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x7F:
                self.mappingTable[self._memory[i]] = self.INST_MOV
            elif self._memory[i] == 0x80:
                self.mappingTable[self._memory[i]] = self.INST_ADD
            elif self._memory[i] == 0x81:
                self.mappingTable[self._memory[i]] = self.INST_ADD
            elif self._memory[i] == 0x82:
                self.mappingTable[self._memory[i]] = self.INST_ADD
            elif self._memory[i] == 0x83:
                self.mappingTable[self._memory[i]] = self.INST_ADD
            elif self._memory[i] == 0x84:
                self.mappingTable[self._memory[i]] = self.INST_ADD
            elif self._memory[i] == 0x85:
                self.mappingTable[self._memory[i]] = self.INST_ADD
            elif self._memory[i] == 0x86:
                self.mappingTable[self._memory[i]] = self.INST_ADD
            elif self._memory[i] == 0x87:
                self.mappingTable[self._memory[i]] = self.INST_ADD
            elif self._memory[i] == 0x88:
                self.mappingTable[self._memory[i]] = self.INST_ADC
            elif self._memory[i] == 0x89:
                self.mappingTable[self._memory[i]] = self.INST_ADC
            elif self._memory[i] == 0x8A:
                self.mappingTable[self._memory[i]] = self.INST_ADC
            elif self._memory[i] == 0x8B:
                self.mappingTable[self._memory[i]] = self.INST_ADC
            elif self._memory[i] == 0x8C:
                self.mappingTable[self._memory[i]] = self.INST_ADC
            elif self._memory[i] == 0x8D:
                self.mappingTable[self._memory[i]] = self.INST_ADC
            elif self._memory[i] == 0x8E:
                self.mappingTable[self._memory[i]] = self.INST_ADC
            elif self._memory[i] == 0x8F:
                self.mappingTable[self._memory[i]] = self.INST_ADC
            elif self._memory[i] == 0x90:
                self.mappingTable[self._memory[i]] = self.INST_SUB
            elif self._memory[i] == 0x91:
                self.mappingTable[self._memory[i]] = self.INST_SUB
            elif self._memory[i] == 0x92:
                self.mappingTable[self._memory[i]] = self.INST_SUB
            elif self._memory[i] == 0x93:
                self.mappingTable[self._memory[i]] = self.INST_SUB
            elif self._memory[i] == 0x94:
                self.mappingTable[self._memory[i]] = self.INST_SUB
            elif self._memory[i] == 0x95:
                self.mappingTable[self._memory[i]] = self.INST_SUB
            elif self._memory[i] == 0x96:
                self.mappingTable[self._memory[i]] = self.INST_SUB
            elif self._memory[i] == 0x97:
                self.mappingTable[self._memory[i]] = self.INST_SUB
            elif self._memory[i] == 0x98:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO not implemented
            elif self._memory[i] == 0x99:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO not implemented
            elif self._memory[i] == 0x9A:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO not implemented
            elif self._memory[i] == 0x9B:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO not implemented
            elif self._memory[i] == 0x9C:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO not implemented
            elif self._memory[i] == 0x9D:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO not implemented
            elif self._memory[i] == 0x9E:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO not implemented
            elif self._memory[i] == 0x9F:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO not implemented
            elif self._memory[i] == 0xA0:
                self.mappingTable[self._memory[i]] = self.INST_AND
            elif self._memory[i] == 0xA1:
                self.mappingTable[self._memory[i]] = self.INST_AND
            elif self._memory[i] == 0xA2:
                self.mappingTable[self._memory[i]] = self.INST_AND
            elif self._memory[i] == 0xA3:
                self.mappingTable[self._memory[i]] = self.INST_AND
            elif self._memory[i] == 0xA4:
                self.mappingTable[self._memory[i]] = self.INST_AND
            elif self._memory[i] == 0xA5:
                self.mappingTable[self._memory[i]] = self.INST_AND
            elif self._memory[i] == 0xA6:
                self.mappingTable[self._memory[i]] = self.INST_AND
            elif self._memory[i] == 0xA7:
                self.mappingTable[self._memory[i]] = self.INST_AND
            elif self._memory[i] == 0xA8:
                self.mappingTable[self._memory[i]] = self.INST_XOR
            elif self._memory[i] == 0xA9:
                self.mappingTable[self._memory[i]] = self.INST_XOR
            elif self._memory[i] == 0xAA:
                self.mappingTable[self._memory[i]] = self.INST_XOR
            elif self._memory[i] == 0xAB:
                self.mappingTable[self._memory[i]] = self.INST_XOR
            elif self._memory[i] == 0xAC:
                self.mappingTable[self._memory[i]] = self.INST_XOR
            elif self._memory[i] == 0xAD:
                self.mappingTable[self._memory[i]] = self.INST_XOR
            elif self._memory[i] == 0xAE:
                self.mappingTable[self._memory[i]] = self.INST_XOR
            elif self._memory[i] == 0xAF:
                self.mappingTable[self._memory[i]] = self.INST_XOR
            elif self._memory[i] == 0xB0:
                self.mappingTable[self._memory[i]] = self.INST_OR
            elif self._memory[i] == 0xB1:
                self.mappingTable[self._memory[i]] = self.INST_OR
            elif self._memory[i] == 0xB2:
                self.mappingTable[self._memory[i]] = self.INST_OR
            elif self._memory[i] == 0xB3:
                self.mappingTable[self._memory[i]] = self.INST_OR
            elif self._memory[i] == 0xB4:
                self.mappingTable[self._memory[i]] = self.INST_OR
            elif self._memory[i] == 0xB5:
                self.mappingTable[self._memory[i]] = self.INST_OR
            elif self._memory[i] == 0xB6:
                self.mappingTable[self._memory[i]] = self.INST_OR
            elif self._memory[i] == 0xB7:
                self.mappingTable[self._memory[i]] = self.INST_OR
            elif self._memory[i] == 0xB8:
                self.mappingTable[self._memory[i]] = self.INST_CMP
            elif self._memory[i] == 0xB9:
                self.mappingTable[self._memory[i]] = self.INST_CMP
            elif self._memory[i] == 0xBA:
                self.mappingTable[self._memory[i]] = self.INST_CMP
            elif self._memory[i] == 0xBB:
                self.mappingTable[self._memory[i]] = self.INST_CMP
            elif self._memory[i] == 0xBC:
                self.mappingTable[self._memory[i]] = self.INST_CMP
            elif self._memory[i] == 0xBD:
                self.mappingTable[self._memory[i]] = self.INST_CMP
            elif self._memory[i] == 0xBE:
                self.mappingTable[self._memory[i]] = self.INST_CMP
            elif self._memory[i] == 0xBF:
                self.mappingTable[self._memory[i]] = self.INST_CMP
            elif self._memory[i] == 0xC0:
                self.mappingTable[self._memory[i]] = self.INST_RET
            elif self._memory[i] == 0xC1:
                self.mappingTable[self._memory[i]] = self.INST_POP_BC
            elif self._memory[i] == 0xC2:
                self.mappingTable[self._memory[i]] = self.INST_JMP
            elif self._memory[i] == 0xC3:
                self.mappingTable[self._memory[i]] = self.INST_JMP
            elif self._memory[i] == 0xC4:
                self.mappingTable[self._memory[i]] = self.INST_CALL
            elif self._memory[i] == 0xC5:
                self.mappingTable[self._memory[i]] = self.INST_PUSH
            elif self._memory[i] == 0xC6:
                self.mappingTable[self._memory[i]] = self.INST_ADD
            elif self._memory[i] == 0xC7:
                self.mappingTable[self._memory[i]] = self.INST_RST
            elif self._memory[i] == 0xC8:
                self.mappingTable[self._memory[i]] = self.INST_RET
            elif self._memory[i] == 0xC9:
                self.mappingTable[self._memory[i]] = self.INST_RET
            elif self._memory[i] == 0xCA:
                self.mappingTable[self._memory[i]] = self.INST_JMP
            elif self._memory[i] == 0xCB:
                self.mappingTable[self._memory[i]] = self.INST_NOP  # TODO nothing
            elif self._memory[i] == 0xCC:
                self.mappingTable[self._memory[i]] = self.INST_CALL
            elif self._memory[i] == 0xCD:
                self.mappingTable[self._memory[i]] = self.INST_CALL
            elif self._memory[i] == 0xCE:
                self.mappingTable[self._memory[i]] = self.INST_ADC
            elif self._memory[i] == 0xCF:
                self.mappingTable[self._memory[i]] = self.INST_RST
            elif self._memory[i] == 0xD0:
                self.mappingTable[self._memory[i]] = self.INST_RET
            elif self._memory[i] == 0xD1:
                self.mappingTable[self._memory[i]] = self.INST_POP_DE
            elif self._memory[i] == 0xD2:
                self.mappingTable[self._memory[i]] = self.INST_JMP
            elif self._memory[i] == 0xD3:
                self.mappingTable[self._memory[i]] = self.INST_OUTP
            elif self._memory[i] == 0xD4:
                self.mappingTable[self._memory[i]] = self.INST_CALL
            elif self._memory[i] == 0xD5:
                self.mappingTable[self._memory[i]] = self.INST_PUSH
            elif self._memory[i] == 0xD6:
                self.mappingTable[self._memory[i]] = self.INST_SUB
            elif self._memory[i] == 0xD7:
                self.mappingTable[self._memory[i]] = self.INST_RST
            elif self._memory[i] == 0xD8:
                self.mappingTable[self._memory[i]] = self.INST_RET
            elif self._memory[i] == 0xD9:
                self.mappingTable[self._memory[i]] = self.INST_NOP  # TODO nothing
            elif self._memory[i] == 0xDA:
                self.mappingTable[self._memory[i]] = self.INST_JMP
            elif self._memory[i] == 0xDB:
                self.mappingTable[self._memory[i]] = self.INST_INP
            elif self._memory[i] == 0xDC:
                self.mappingTable[self._memory[i]] = self.INST_CALL
            elif self._memory[i] == 0xDD:
                self.mappingTable[self._memory[i]] = self.INST_NOP  # TODO nothing
            elif self._memory[i] == 0xDE:
                self.mappingTable[self._memory[i]] = self.INST_SBBI
            elif self._memory[i] == 0xDF:
                self.mappingTable[self._memory[i]] = self.INST_RST
            elif self._memory[i] == 0xE0:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO implement    cycles += 5 11
            elif self._memory[i] == 0xE1:
                self.mappingTable[self._memory[i]] = self.INST_POP_HL
            elif self._memory[i] == 0xE2:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO implement    cycles += 10 15
            elif self._memory[i] == 0xE3:
                self.mappingTable[self._memory[i]] = self.INST_XTHL
            elif self._memory[i] == 0xE4:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO implement
            elif self._memory[i] == 0xE5:
                self.mappingTable[self._memory[i]] = self.INST_PUSH
            elif self._memory[i] == 0xE6:
                self.mappingTable[self._memory[i]] = self.INST_AND
            elif self._memory[i] == 0xE7:
                self.mappingTable[self._memory[i]] = self.INST_RST
            elif self._memory[i] == 0xE8:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO implement    cycles += 5 11
            elif self._memory[i] == 0xE9:
                self.mappingTable[self._memory[i]] = self.INST_PCHL
            elif self._memory[i] == 0xEA:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO implement    cycles += 10 15
            elif self._memory[i] == 0xEB:
                self.mappingTable[self._memory[i]] = self.INST_XCHG
            elif self._memory[i] == 0xEC:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # cycles += 11 18
            elif self._memory[i] == 0xED:
                self.mappingTable[self._memory[i]] = self.INST_NOP  # TODO nothing
            elif self._memory[i] == 0xEE:
                self.mappingTable[self._memory[i]] = self.INST_XOR
            elif self._memory[i] == 0xEF:
                self.mappingTable[self._memory[i]] = self.INST_RST
            elif self._memory[i] == 0xF0:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # cycles += 5 11
            elif self._memory[i] == 0xF1:
                self.mappingTable[self._memory[i]] = self.INST_POP_FLAGS
            elif self._memory[i] == 0xF2:
                self.mappingTable[self._memory[i]] = self.INST_JMP
            elif self._memory[i] == 0xF3:
                self.mappingTable[self._memory[i]] = self.INST_DI
            elif self._memory[i] == 0xF4:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # cycles += 11 18
            elif self._memory[i] == 0xF5:
                self.mappingTable[self._memory[i]] = self.INST_PUSH
            elif self._memory[i] == 0xF6:
                self.mappingTable[self._memory[i]] = self.INST_OR
            elif self._memory[i] == 0xF7:
                self.mappingTable[self._memory[i]] = self.INST_RST
            elif self._memory[i] == 0xF8:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # cycles += 5 11
            elif self._memory[i] == 0xF9:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # cycles += 6
            elif self._memory[i] == 0xFA:
                self.mappingTable[self._memory[i]] = self.INST_JMP
            elif self._memory[i] == 0xFB:
                self.mappingTable[self._memory[i]] = self.INST_EI
            elif self._memory[i] == 0xFC:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # cycles += 11 18
            elif self._memory[i] == 0xFD:
                self.mappingTable[self._memory[i]] = self.INST_NOP
            elif self._memory[i] == 0xFE:
                self.mappingTable[self._memory[i]] = self.INST_CMP
            elif self._memory[i] == 0xFF:
                self.mappingTable[self._memory[i]] = self.INST_RST

    def information(self):
        print " a:%x" % self.A, self.A
        print "bc:%x B:%x C:%x" % (self.BC, self.B, self.C)
        print "de:%x D:%x E:%x" % (self.DE, self.D, self.E)
        print "HL:%x H:%x L:%x" % (self.HL, self.H, self.L)
        print "SP:%x" % self.SP, self.SP
        print "ZERO:", self.ZERO
        print "SIGN:", self.SIGN
        print "Parity:", self.PARITY
        print "HALFCARRY:", self.HALFCARRY
        print "INTERRUPT:", self.INTERRUPT
        print "CARRY:", self.CARRY
        print "COUNT:", self.count
        print
        for i in range(10):
            print "%x: %x" % (self.PC+i, self._memory[self.PC+i])
