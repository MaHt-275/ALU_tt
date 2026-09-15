# test/test_alu_top.py
# SPDX-FileCopyrightText: © 2026 Joaquín O'Ryan
# SPDX-License-Identifier: Apache-2.0
"""Test unitario de la ALU completa (src/alu_top.v): multiplexa entre
desplazador, aritmetica, logica y paso de datos segun 'select'.
Corre con: make -B MODULE=alu_top"""

import cocotb
from cocotb.triggers import Timer


async def apply(dut, a=0, b=0, select=0, shift_amount=0, shift_iz_der=0,
                 shift_arit_right=0, carry_in=0, mod_sub=0, op=0):
    dut.in_a.value = a
    dut.in_b.value = b
    dut.select.value = select
    dut.shift_amount.value = shift_amount
    dut.SHIFT_IZ_DER.value = shift_iz_der
    dut.SHIFT_ARIT_RIGHT.value = shift_arit_right
    dut.carry_in.value = carry_in
    dut.mod_sub.value = mod_sub
    dut.op.value = op
    await Timer(1, unit="ns")


@cocotb.test()
async def test_modo_desplazador(dut):
    await apply(dut, a=0x01, select=0b00, shift_amount=3, shift_iz_der=0)
    assert dut.out.value == 0x08
    assert dut.overflow_flag.value == 0


@cocotb.test()
async def test_modo_aritmetico(dut):
    await apply(dut, a=5, b=3, select=0b01)
    assert dut.out.value == 8
    assert dut.carry_out.value == 0


@cocotb.test()
async def test_modo_logico(dut):
    await apply(dut, a=0xF0, b=0x0F, select=0b10, op=0b01)  # OR
    assert dut.out.value == 0xFF


@cocotb.test()
async def test_modo_pasada(dut):
    await apply(dut, a=0x5A, b=0xFF, select=0b11)
    assert dut.out.value == 0x5A
    assert dut.carry_out.value == 0
    assert dut.overflow_flag.value == 0


@cocotb.test()
async def test_bandera_cero(dut):
    await apply(dut, a=0x0F, b=0x0F, select=0b10, op=0b10)  # XOR -> 0
    assert dut.out.value == 0
    assert dut.zero_flag.value == 1
    assert dut.negative_flag.value == 0


@cocotb.test()
async def test_bandera_negativo(dut):
    await apply(dut, a=0x80, b=0x00, select=0b01)  # 0x80 + 0 = 0x80
    assert dut.out.value == 0x80
    assert dut.negative_flag.value == 1
    assert dut.zero_flag.value == 0
