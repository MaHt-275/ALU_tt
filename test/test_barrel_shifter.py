# test/test_barrel_shifter.py
# SPDX-FileCopyrightText: © 2026 Joaquín O'Ryan
# SPDX-License-Identifier: Apache-2.0
"""Test unitario de la unidad desplazadora (src/barrel_shifter.v).
   Corre con: make -B MODULE=barrel_shifter"""

import cocotb
from cocotb.triggers import Timer


async def apply(dut, a, amount, iz_der=0, arit_right=0):
    dut.IN_A_BUS_8bits.value = a
    dut.shift_amount.value = amount
    dut.SHIFT_IZ_DER.value = iz_der
    dut.SHIFT_ARIT_RIGHT.value = arit_right
    await Timer(1, unit="ns")


@cocotb.test()
async def test_sin_desplazamiento(dut):
    await apply(dut, 0xAA, 0)
    assert dut.OUT_BUS_8bits.value == 0xAA
    assert dut.Carry_flag.value == 0


@cocotb.test()
async def test_shift_izquierda(dut):
    await apply(dut, 0b0000_0001, 3, iz_der=0)
    assert dut.OUT_BUS_8bits.value == 0b0000_1000
    assert dut.Carry_flag.value == 0  # el bit que sale es 0 en este caso


@cocotb.test()
async def test_shift_izquierda_con_carry(dut):
    await apply(dut, 0b1100_0000, 2, iz_der=0)
    assert dut.OUT_BUS_8bits.value == 0x00
    assert dut.Carry_flag.value == 1  # bit6 original sale por la izquierda


@cocotb.test()
async def test_shift_derecha_logico(dut):
    await apply(dut, 0b1000_0000, 3, iz_der=1, arit_right=0)
    assert dut.OUT_BUS_8bits.value == 0b0001_0000
    assert dut.Carry_flag.value == 0  # bit[2] del valor original es 0


@cocotb.test()
async def test_shift_derecha_aritmetico_negativo(dut):
    # 0x80 = -128 en complemento a 2; al desplazar aritmeticamente a la
    # derecha debe extender el signo (rellenar con 1s)
    await apply(dut, 0x80, 4, iz_der=1, arit_right=1)
    assert dut.OUT_BUS_8bits.value == 0xF8


@cocotb.test()
async def test_shift_derecha_aritmetico_positivo(dut):
    await apply(dut, 0b0100_0000, 2, iz_der=1, arit_right=1)
    assert dut.OUT_BUS_8bits.value == 0b0001_0000
