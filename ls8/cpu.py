"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.op_table = {'0b10000010': self.LDI, '0b10000011': self.LD, '0b00000001': self.HLT, 
                         '0b01000111': self.PRN, '0b10100010': self.MLT, '0b01000101': self.PUSH,
                         '0b01000110': self.POP, 
                         '0b1010000': self.CALL}
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.reg[7] = len(self.ram) - 1
        self.running = False

    def load_memory(self, filename):
        address = 0
        try:
            with open(filename) as f:
                for line in f:
                    comment_split = line.split("#")
                    num = comment_split[0].strip()
                    if num == '':
                        continue
                    code = f"0b{num.zfill(8)}"
                    self.ram[address] = code
                    address += 1

        except FileNotFoundError:
            print("File not found")
            self.load()

    def load(self):
        """Load a program into memory."""
        address = 0

        program = [
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b10000010, # LDI R1,9
            0b00000001,
            0b00001001,
            0b10100010, # MUL R0,R1
            0b00000000,
            0b00000001,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001 # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        if MAR < len(self.ram) and MAR >= 0:
            return self.ram[MAR]
        else:
            print(f"ERROR: Memory address {MAR} is outside of RAM range!\nCurrent address: {self.pc}")
            self.running = False

    def ram_write(self, MDR, MAR):
        if MAR < len(self.ram) and MAR >= 0:
            self.ram[MAR] = MDR
        else:
            print(f"ERROR: Memory address {MAR} is outside of RAM range!\nCurrent address: {self.pc}")
            self.running = False

    def reset_registers(self):
        for i in range(7):
            self.reg[i] = 0
        self.reg[7] = len(self.ram) - 1
        self.pc = 0
            
    def LDI(self, operand_a, operand_b):
        reg_num = int(operand_a)
        if reg_num > len(self.reg):
            self.running = False
        else:
            self.reg[reg_num] = operand_b
            self.pc += 2

    def LD(self, operand_a, operand_b):
        reg_a_num = int(operand_a)
        reg_b_num = int(operand_b)
        if reg_a_num > len(self.reg):
            print(f"ERROR: There is no register {reg_a_num}!\nCurrent address: {self.pc}")
            self.running = False
        elif reg_b_num > len(self.reg):
            print(f"ERROR: There is no register {reg_b_num}!\nCurrent address: {self.pc}")
            self.running = False
        else:
            self.reg[reg_a_num] = self.reg[reg_b_num]
            self.pc += 2

    def HLT(self, operand_a, operand_b):
        self.running = False

    def PRN(self, operand_a, operand_b):
        print(self.reg[int(operand_a)])
        self.pc += 1

    def MLT(self, operand_a, operand_b):
        self.reg[operand_a] = self.reg[operand_a] * self.reg[operand_b]
        self.pc += 2

    def CALL(self, operand_a, operand_b):
        pass
        # self.reg[7] = self.pc
        # self.pc = operand_a

    def PUSH(self, operand_a, operand_b):
        val = self.reg[operand_a] # 0
        self.ram_write(val, self.reg[7])
        self.reg[7] -= 1
        self.pc += 1

    def POP(self, operand_a, operand_b):
        if self.reg[7] < 256:
            self.reg[7] += 1
            val = self.ram_read(self.reg[7])
            self.reg[operand_a] = val
            self.pc += 1
        else:
            self.running = False
            print(f"ERROR: No values left in stack, stack could not be popped!\nCurrent address: {self.pc}")

    def run(self):
        """Run the CPU."""
        self.reset_registers()
        self.running = True
        ir = ""
        operand_a = 0
        operand_a = 0
        while self.running:
            ir = self.ram_read(self.pc)
            if ir not in self.op_table:
                self.running = False
                print(f"ERROR: Unknown instruction \"{ir}\" called!\nCurrent address: {self.pc}")
            elif self.pc >= len(self.ram):
                print(f"ERROR: PC went above length of ram!\nCurrent address: {self.pc}")
                self.running = False
            else:
                operand_a = int(str(self.ram_read(self.pc + 1)), 2)
                operand_b = int(str(self.ram_read(self.pc + 2)), 2)
                self.op_table[ir](operand_a, operand_b)
                self.pc += 1
        print("Halting...")