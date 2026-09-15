# test/test_arithmetic.py
# SPDX-FileCopyrightText: © 2026 Joaquín O'Ryan
# SPDX-License-Identifier: Apache-2.0
"""Test unitario de la unidad aritmetica (src/arithmetic.v). Corre con:
   make -B MODULE=arithmetic"""

import cocotb
from cocotb.triggers import Timer


async def apply(dut, a, b, carry_in=0, mod_sub=0):
    dut.in_a.value = a
    dut.in_b.value = b
    dut.carry_in.value = carry_in
    dut.mod_sub.value = mod_sub
    await Timer(1, unit="ns")


@cocotb.test()
async def test_suma_simple(dut):
    await apply(dut, 5, 3)
    assert dut.arit_out.value == 8
    assert dut.carry_out.value == 0
    assert dut.overflow_flag.value == 0


@cocotb.test()
async def test_suma_con_acarreo(dut):
    # 200 + 100 = 300 -> desborda los 8 bits (carry_out=1)
    await apply(dut, 200, 100)
    assert dut.arit_out.value == (300 & 0xFF)
    assert dut.carry_out.value == 1


@cocotb.test()
async def test_resta_mod_sub(dut):
    # 10 - 4 = 6 (mod_sub=1 invierte B, carry_in=1 completa el complemento a 2)
    await apply(dut, 10, 4, carry_in=1, mod_sub=1)
    assert dut.arit_out.value == 6
    assert dut.carry_out.value == 1  # no hay "borrow": 10 >= 4


@cocotb.test()
async def test_resta_con_borrow(dut):
    # 4 - 10 = -6 -> complemento a 2 de 8 bits: 250 (0xFA), sin acarreo de salida
    await apply(dut, 4, 10, carry_in=1, mod_sub=1)
    assert dut.arit_out.value == (256 - 6) & 0xFF
    assert dut.carry_out.value == 0  # indica "borrow"


@cocotb.test()
async def test_overflow_signed(dut):
    # 100 + 50 = 150 -> como numero con signo de 8 bits se interpreta negativo: overflow
    await apply(dut, 100, 50)
    assert dut.arit_out.value == 150
    assert dut.overflow_flag.value == 1


@cocotb.test()
async def test_sin_overflow_signos_distintos(dut):
    # Sumar operandos de signo distinto jamas produce overflow
    await apply(dut, 200, 100)
    assert dut.overflow_flag.value == 0
