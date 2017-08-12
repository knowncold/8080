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
        self.PARITY = 0  # odd or even
        self.CARRY = False
        self.INTERRUPT = False
        self.current_inst = 0  # current instruction

        self.interrupt_alternate = False
        self.count_inst = 0

        self.disassembly_pc = 0
        self.mappingTable = [0] * 0x100
        self.inst_per_frame = 40000
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
        self._memory += [0] * (16384 - len(self._memory))   # ROM + RAM(work RAM and video RAM) = 16384 0x3fff

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
        for i in range(self.inst_per_frame):
            self.execINST()

    def runCycles(self, cycles):
        for i in range(cycles):
            self.execINST()
        # print "PC: " + "%x"%self.PC
        # print "oprand: " + "%x"%(self.current_inst)
        return self.PC

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

        if self.count_inst >= self.half_inst_per_frame:
            if self.INTERRUPT:
                if self.interrupt_alternate == False:
                    self.callInterrupt(0x08)
                else:
                    self.callInterrupt(0x10)
            self.interrupt_alternate = not self.interrupt_alternate
            self.count_inst = 0

    def callInterrupt(self, address):
        self.INTERRUPT = False
        self.stackPush(self.PC)
        self.PC = address

    def INST_NOP(self):  # nop
        pass

    def INST_toImplement(self):
        print str(self.current_inst) + " is not implement."

    def INST_JMP(self):  # JMP group     size 3
        condition = True
        data_16 = self.FetchRomNext2Bytes()  # fetch the next 2 data
        if 0xC3 == self.current_inst:  # JMP
            pass
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

        if condition:
            self.PC = data_16

    def INST_LXI_BC(self):  # B <- byte 3, C <- byte 2
        self.BC = self.FetchRomNext2Bytes()
        # data_16 &= 0xFFFF     # is this necessary
        self.B = self.BC >> 8
        self.C = self.BC & 0xFF

    def INST_LXI_DE(self):  # D <- byte 3, E <- byte 2
        self.DE = self.FetchRomNext2Bytes()
        self.D = self.DE >> 8
        self.C = self.DE & 0xFF

    def INST_LXI_HL(self):  # H <- byte 3, L <- byte 2
        self.HL = self.FetchRomNext2Bytes()
        self.H = self.HL >> 8
        self.L = self.HL & 0xFF

    def INST_LXI_SP(self):  # SP.hi <- byte 3, SP.lo <- byte 2
        self.SP = self.FetchRomNext2Bytes()

    def INST_MVI_A(self):  # A <- byte 2
        self.A = self.FetchRomNext1Byte()

    def INST_MVI_B(self):  # B <- byte2
        self.B = self.FetchRomNext1Byte()
        self.BC = (self.B << 8) + self.C

    def INST_MVI_C(self):  # C <- byte2
        self.C = self.FetchRomNext1Byte()
        self.BC = (self.B << 8) + self.C

    def INST_MVI_D(self):  # D <- byte2
        self.D = self.FetchRomNext1Byte()
        self.DE = (self.D << 8) + self.E

    def INST_MVI_E(self):  # E <- byte2
        self.E = self.FetchRomNext1Byte()
        self.DE = (self.D << 8) + self.E

    def INST_MVI_H(self):  # H <- byte2
        self.H = self.FetchRomNext1Byte()
        self.HL = (self.H << 8) + self.L

    def INST_MVI_L(self):  # L <- byte2
        self.L = self.FetchRomNext1Byte()
        self.HL = (self.H << 8) + self.L

    def INST_MVI_M(self):
        self.write2Bytes(self.HL, self.FetchRomNext2Bytes())

    def INST_CALL(self):
        condition = True
        data_16 = self.FetchRomNext2Bytes()

        if self.current_inst == 0xCD:  # CALL adr	3		(SP-1)<-PC.hi;(SP-2)<-PC.lo;SP<-SP+2;PC=adr
            pass
        elif self.current_inst == 0xC4:  # if NZ, CALL adr
            condition = not self.ZERO
        elif self.current_inst == 0xCC:
            condition = self.ZERO
        elif self.current_inst == 0xD4:
            condition = not self.CARRY
        elif self.current_inst == 0xDC:
            condition = self.CARRY

        if condition:
            self.stackPush(self.PC)
            self.PC = data_16

    def INST_RET(self):
        condition = True

        if self.current_inst == 0xC9:
            pass
        elif self.current_inst == 0xC0:
            condition = not self.ZERO
        elif self.current_inst == 0xC8:
            condition = self.ZERO
        elif self.current_inst == 0xD0:
            condition = not self.CARRY
        elif self.current_inst == 0xD8:
            condition = self.CARRY

        if condition:
            self.PC = self.stackPop()

    def INST_LDA(self):
        if self.current_inst == 0x0A:
            source = self.BC
        elif self.current_inst == 0x1A:
            source = self.DE
        elif self.current_inst == 0x3A:
            source = self.FetchRomNext2Bytes()
        else:
            source = 0

        self.A = self.readByte(source)

    def INST_PUSH(self):
        if self.current_inst == 0xC5:
            value = self.BC
        elif self.current_inst == 0xD5:
            value = self.DE
        elif self.current_inst == 0xE5:
            value = self.HL
        elif self.current_inst == 0xF5:
            value = self.A << 8
            value += 0x80 if self.SIGN else 0
            value += 0x40 if self.ZERO else 0
            value += 0x20 if self.INTERRUPT else 0
            value += 0x10 if self.HALFCARRY else 0
            value += 0x01 if self.CARRY else 0
        else:
            value = 0
            print "Instruction Push Error: " + str(self.current_inst)
            exit(1)

        self.stackPush(value)

    def INST_POP_BC(self):
        self.BC = self.stackPop()
        self.B = self.BC >> 8
        self.C = self.BC & 0xFF

    def INST_POP_DE(self):
        self.DE = self.stackPop()
        self.D = self.DE >> 8
        self.E = self.DE & 0xFF

    def INST_POP_HL(self):
        self.HL = self.stackPop()
        self.H = self.HL >> 8
        self.L = self.HL & 0xFF

    def INST_POP_FLAGS(self):
        value = self.stackPop()
        self.A = value >> 8
        self.SIGN = True if (value & 0x80) > 0 else False
        self.ZERO = True if (value & 0x40) > 0 else False
        self.INTERRUPT = True if (value & 0x20) > 0 else False
        self.HALFCARRY = True if (value & 0x10) > 0 else False
        self.CARRY = True if (value & 0x01) > 0 else False

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
            self.setC(self.readByte(self.HL))

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

    def INST_INX(self):
        if self.current_inst == 0x03:
            self.setBC(self.BC + 1)
        elif self.current_inst == 0x13:
            self.setDE(self.DE + 1)
        elif self.current_inst == 0x23:
            self.setHL(self.HL+1)
        elif self.current_inst == 0x33:
            self.SP += 1

    def INST_DAD_BC(self):
        self.addHL(self.BC)

    def INST_DAD_DE(self):
        self.addHL(self.DE)

    def INST_DAD_HL(self):
        self.addHL(self.HL)

    def INST_DAD_SP(self):
        self.addHL(self.SP)

    def INST_DCX(self):
        if self.current_inst == 0x0B:
            self.setBC(self.BC - 1)
        elif self.current_inst == 0x1B:
            self.setDE(self.DE - 1)
        elif self.current_inst == 0x2B:
            self.setHL(self.HL - 1)
        elif self.current_inst == 0x3B:
            self.SP = self.SP - 1

    def INST_DEC(self):
        if self.current_inst == 0x3D:
            self.A = self.Dec(self.A)
        elif self.current_inst == 0x05:
            self.setB(self.Dec(self.B))
        elif self.current_inst == 0x0D:
            self.setC(self.Dec(self.C))
        elif self.current_inst == 0x15:
            self.setD(self.Dec(self.D))
        elif self.current_inst == 0x1D:
            self.setE(self.Dec(self.E))
        elif self.current_inst == 0x25:
            self.setH(self.Dec(self.H))
        elif self.current_inst == 0x2D:
            self.setL(self.Dec(self.L))
        elif self.current_inst == 0x35:
            self.writeByte(self.HL, self.Dec(self.readByte(self.HL)))

    def INST_INR(self):
        if self.current_inst == 0x3C:
            self.A = self.Inc(self.A)
        elif self.current_inst == 0x04:
            self.setB(self.Inc(self.B))
        elif self.current_inst == 0x0C:
            self.setC(self.Inc(self.C))
        elif self.current_inst == 0x14:
            self.setD(self.Inc(self.D))
        elif self.current_inst == 0x1C:
            self.setE(self.Inc(self.E))
        elif self.current_inst == 0x24:
            self.setH(self.Inc(self.H))
        elif self.current_inst == 0x2C:
            self.setL(self.Inc(self.L))
        elif self.current_inst == 0x34:
            self.writeByte(self.HL, self.Inc(self.readByte(self.HL)))

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
        elif self.current_inst == 0xE6:
            self.And(self.FetchRomNext1Byte())

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
        elif self.current_inst == 0xEE:
            self.Xor(self.FetchRomNext1Byte())

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
        elif self.current_inst == 0xF6:
            self.Or(self.FetchRomNext1Byte())

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
        elif self.current_inst == 0xC6:
            self.Add(self.FetchRomNext1Byte())

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
        elif self.current_inst == 0xCE:
            self.Add(self.FetchRomNext1Byte(), carry)

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
        elif self.current_inst == 0xD6:
            self.Sub(self.FetchRomNext1Byte())

    def INST_SBBI(self):
        data = self.FetchRomNext1Byte()
        carry = 1 if self.CARRY else 0
        self.Sub(data, carry)

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
        elif self.current_inst == 0xFE:
            value = self.FetchRomNext1Byte()
        else:
            value = 0
        self.CmpSub(value)

    def INST_XCHG(self):
        temp = self.HL
        self.setHL(self.DE)
        self.setDE(temp)

    def INST_XTHL(self):
        temp = self.H
        self.setH(self.readByte(self.SP+1))
        self.writeByte(self.SP+1, temp)

        temp = self.L
        self.setL(self.readByte(self.SP))
        self.writeByte(self.SP, temp)

    def INST_OUTP(self):    # TODO IO
        port = self.FetchRomNext1Byte()
        self.io.OutPutPort(port, self.A)

    def INST_INP(self):     # TODO IO
        port = self.FetchRomNext1Byte()
        self.A = self.io.InPutPort(port)

    def INST_PCHL(self):
        self.PC = self.HL

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

    def INST_RLC(self):
        self.CARRY = self.A >> 7
        self.A = (self.A << 1) | (self.A >> 7)

    def INST_RAL(self):
        temp = self.A
        self.A = self.A << 1
        self.A |= 1 if self.CARRY else 0
        self.CARRY = temp & 0x80

    def INST_RRC(self):
        self.CARRY = self.A >> 7
        self.A = (self.A >> 1) | (self.A << 7)

    def INST_RAR(self):     # TODO manual wrong???????????????????????
        temp = self.A & 0xFF
        self.A = self.A >> 1 | (self.A >> 7 << 7)
        self.CARRY = temp << 7 >> 7

    def INST_RIM(self):     # TODO nothing?
        pass

    def INST_STA(self):
        if self.current_inst == 0x02:
            self.writeByte(self.BC, self.A)
        elif self.current_inst == 0x12:
            self.writeByte(self.DE, self.A)
        elif self.current_inst == 0x32:
            self.writeByte(self.FetchRomNext2Bytes(), self.A)

    def INST_DI(self):
        self.INTERRUPT = False

    def INST_EI(self):
        self.INTERRUPT = True

    def INST_STC(self):
        self.CARRY = 1

    def INST_CMC(self):
        self.CARRY = not self.CARRY

    def INST_LHLD(self):
        self.setHL(self.read2Bytes(self.FetchRomNext2Bytes()))

    def INST_SHLD(self):
        self.write2Bytes(self.FetchRomNext2Bytes(), self.HL)

    def INST_DAA(self):     # TODO no manual
        if (self.A & 0x0F) > 9 or self.HALFCARRY:
            self.A += 0x06
            self.HALFCARRY = True
        else:
            self.HALFCARRY = False

        if (self.A > 0x9F) or self.CARRY:
            self.A += 0x60
            self.CARRY = True
        else:
            self.CARRY = False

        self.ZERO = True if self.A == 0 else False
        self.SIGN = True if (self.A & 0x80) > 0 else False

    def INST_CMA(self):
        self.A = self.A ^ 0xFF

    @staticmethod
    def INST_HLT():
        print "HLT"
        exit(0)

    def setB(self, data):
        self.B = data
        self.BC = (self.B << 8) + self.C

    def setC(self, data):
        self.C = data
        self.BC = (self.B << 8) + self.C

    def setD(self, data):
        self.D = data
        self.DE = (self.D << 8) + self.E

    def setE(self, data):
        self.E = data
        self.DE = (self.D << 8) + self.E

    def setH(self, data):
        self.H = data
        self.HL = (self.H << 8) + self.L

    def setL(self, data):
        self.L = data
        self.HL = (self.H << 8) + self.L

    def setBC(self, data):
        self.BC = data
        self.B = self.BC >> 8
        self.C = self.BC & 0xFF

    def setDE(self, data):
        self.DE = data
        self.D = self.DE >> 8
        self.E = self.DE & 0xFF

    def setHL(self, data):
        self.HL = data & 0xFFFF     # & used for addHL()
        self.H = self.HL >> 8
        self.L = self.HL & 0xFF

    def addHL(self, data):
        value = self.HL + data
        self.setHL(value)
        self.CARRY = True if value > 0xFFFF else False

    def Inc(self, data):
        value = (data + 1) & 0xFF
        self.ZERO = True if value == 0 else False
        self.SIGN = True if value & 128 & 0xFF else False   # TODO may error
        self.HALFCARRY = True if value & 0xF == 0 else False    # TODO may error
        return value

    def Dec(self, data):
        value = (data - 1) & 0xFF
        self.HALFCARRY = True if (value & 0xF) == 0xF else False    # TODO may error
        self.SIGN = True if value & 128 > 0 else False
        self.ZERO = True if value == 0 else False
        return value

    def And(self, value):
        self.A = (self.A & value)
        self.CARRY = False
        self.HALFCARRY = False
        self.ZERO = True if self.A == 0 else False
        self.SIGN = True if self.A & 0x80 > 0 else False

    def Xor(self, value):
        self.A = self.A ^ value
        self.CARRY = False
        self.HALFCARRY = False
        self.ZERO = True if self.A == 0 else False
        self.SIGN = True if self.A & 0x80 > 0 else False

    def Or(self, value):
        self.A = self.A | value
        self.CARRY = False
        self.HALFCARRY = False
        self.ZERO = True if self.A == 0 else False
        self.SIGN = True if self.A & 0x80 > 0 else False

    def Add(self, in_value, carry=0):
        value = self.A + in_value + carry
        self.HALFCARRY = (self.A ^ in_value ^ (value & 0xFF)) & 0x10  # TODO
        self.A = value & 0xFF
        self.CARRY = True if value > 255 else False
        self.SIGN = True if self.A & 0x80 > 0 else False
        self.ZERO = True if self.A == 0 else False

    def Sub(self, in_value, carry=0):
        value = self.A - in_value - carry
        self.HALFCARRY = (self.A ^ in_value ^ (value & 0xFF)) & 0x10  # TODO
        self.CARRY = True if ((value & 0xFF) >= self.A and (in_value | carry) > 0) else False
        self.A = value & 0xFF
        self.SIGN = True if self.A & 0x80 > 0 else False
        self.ZERO = True if self.A == 0 else False

    def CmpSub(self, in_value):        # TODO
        value = (self.A - in_value) & 0xFF
        self.CARRY = True if ((value >= self.A) and (in_value > 0)) else False
        self.HALFCARRY = (self.A ^ in_value ^ value) & 0x10
        self.ZERO = True if value == 0 else False
        self.SIGN = value & 128

    def stackPush(self, data):
        self.SP -= 2
        self.write2Bytes(self.SP, data)

    def stackPop(self):
        address = self.read2Bytes(self.SP)
        self.SP += 2
        return address

    def readByte(self, address):
        return self._memory[address]

    def read2Bytes(self, address):
        return (self._memory[address + 1] << 8) + self._memory[address]

    def writeByte(self, address, data):
        self._memory[address] = data & 0xFF

    def write2Bytes(self, address, data):
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
                self.mappingTable[self._memory[i]] = self.INST_DCX
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
                self.mappingTable[self._memory[i]] = self.INST_DCX
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
                self.mappingTable[self._memory[i]] = self.INST_DCX
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
                self.mappingTable[self._memory[i]] = self.INST_DCX
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
                self.mappingTable[self._memory[i]] = self.INST_DCX
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
                self.mappingTable[self._memory[i]] = self.INST_DCX
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
                self.mappingTable[self._memory[i]] = self.INST_DCX
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
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO not implement
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
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO implement
            elif self._memory[i] == 0xE1:
                self.mappingTable[self._memory[i]] = self.INST_POP_HL
            elif self._memory[i] == 0xE2:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO implement
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
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO implement
            elif self._memory[i] == 0xE9:
                self.mappingTable[self._memory[i]] = self.INST_PCHL
            elif self._memory[i] == 0xEA:
                self.mappingTable[self._memory[i]] = self.INST_toImplement  # TODO implement
            elif self._memory[i] == 0xEB:
                self.mappingTable[self._memory[i]] = self.INST_XCHG
            elif self._memory[i] == 0xEC:
                self.mappingTable[self._memory[i]] = self.INST_toImplement
            elif self._memory[i] == 0xED:
                self.mappingTable[self._memory[i]] = self.INST_NOP  # TODO nothing
            elif self._memory[i] == 0xEE:
                self.mappingTable[self._memory[i]] = self.INST_XOR
            elif self._memory[i] == 0xEF:
                self.mappingTable[self._memory[i]] = self.INST_RST
            elif self._memory[i] == 0xF0:
                self.mappingTable[self._memory[i]] = self.INST_toImplement
            elif self._memory[i] == 0xF1:
                self.mappingTable[self._memory[i]] = self.INST_POP_FLAGS
            elif self._memory[i] == 0xF2:
                self.mappingTable[self._memory[i]] = self.INST_JMP
            elif self._memory[i] == 0xF3:
                self.mappingTable[self._memory[i]] = self.INST_DI
            elif self._memory[i] == 0xF4:
                self.mappingTable[self._memory[i]] = self.INST_toImplement
            elif self._memory[i] == 0xF5:
                self.mappingTable[self._memory[i]] = self.INST_PUSH
            elif self._memory[i] == 0xF6:
                self.mappingTable[self._memory[i]] = self.INST_OR
            elif self._memory[i] == 0xF7:
                self.mappingTable[self._memory[i]] = self.INST_RST
            elif self._memory[i] == 0xF8:
                self.mappingTable[self._memory[i]] = self.INST_toImplement
            elif self._memory[i] == 0xF9:
                self.mappingTable[self._memory[i]] = self.INST_toImplement
            elif self._memory[i] == 0xFA:
                self.mappingTable[self._memory[i]] = self.INST_JMP
            elif self._memory[i] == 0xFB:
                self.mappingTable[self._memory[i]] = self.INST_EI
            elif self._memory[i] == 0xFC:
                self.mappingTable[self._memory[i]] = self.INST_toImplement
            elif self._memory[i] == 0xFD:
                self.mappingTable[self._memory[i]] = self.INST_NOP
            elif self._memory[i] == 0xFE:
                self.mappingTable[self._memory[i]] = self.INST_CMP
            elif self._memory[i] == 0xFF:
                self.mappingTable[self._memory[i]] = self.INST_RST

    def information(self):
        print "a:%x" % self.A
        print "bc:%x" % self.BC
        print "de:%x" % self.DE
        print "HL:%x" % self.HL
        print "SP:%x" % self.SP
        print "ZERO:", self.ZERO
        for i in range(10):
            print "%x: %x" % (self.PC+i, self._memory[self.PC+i])
