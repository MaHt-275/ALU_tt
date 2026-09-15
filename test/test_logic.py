# test/test_logic.py
# SPDX-FileCopyrightText: © 2026 Joaquín O'Ryan
# SPDX-License-Identifier: Apache-2.0
"""Test unitario de la unidad logica (src/logic.v -> modulo Logico_8bits).
   Corre con: make -B MODULE=logic"""

import random
import cocotb
from cocotb.triggers import Timer


async def apply(dut, a, b, op):
    dut.IN_A.value = a
    dut.IN_B.value = b
    dut.op.value = op
    await Timer(1, unit="ns")


@cocotb.test()
async def test_and(dut):
    await apply(dut, 0xF0, 0x3C, 0b00)
    assert dut.out.value == (0xF0 & 0x3C)


@cocotb.test()
async def test_or(dut):
    await apply(dut, 0xF0, 0x0F, 0b01)
    assert dut.out.value == (0xF0 | 0x0F)


@cocotb.test()
async def test_xor(dut):
    await apply(dut, 0xAA, 0x55, 0b10)
    assert dut.out.value == (0xAA ^ 0x55)


@cocotb.test()
async def test_not(dut):
    # NOT solo depende de IN_A, IN_B se ignora
    await apply(dut, 0x0F, 0xFF, 0b11)
    assert dut.out.value == (~0x0F & 0xFF)


@cocotb.test()
async def test_barrido_aleatorio(dut):
    ops = {0b00: lambda a, b: a & b,
           0b01: lambda a, b: a | b,
           0b10: lambda a, b: a ^ b,
           0b11: lambda a, b: (~a) & 0xFF}
    for _ in range(20):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        op = random.choice(list(ops.keys()))
        await apply(dut, a, b, op)
        assert dut.out.value == ops[op](a, b)
