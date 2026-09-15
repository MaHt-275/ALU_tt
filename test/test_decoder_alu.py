# test/test_decoder_alu.py
# SPDX-FileCopyrightText: © 2026 Joaquín O'Ryan
# SPDX-License-Identifier: Apache-2.0
"""Test unitario del decodificador serie (src/decoder_alu.v).
   Corre con: make -B MODULE=decoder_alu

Protocolo: cada operacion se carga en 3 flancos de reloj consecutivos
a traves del bus 'in':
  ciclo 0 -> byte de instruccion (select + bits de control)
  ciclo 1 -> operando A
  ciclo 2 -> operando B
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, Timer


def make_instr(select, shift_iz_der=0, shift_arit_right=0, shift_amount=0,
               mod_sub=0, carry_in=0, op=0):
    instr = (select & 0b11) << 6
    if select == 0b00:
        instr |= (shift_iz_der & 1) << 5
        instr |= (shift_arit_right & 1) << 4
        instr |= (shift_amount & 0b111) << 1
    elif select == 0b01:
        instr |= (mod_sub & 1) << 5
        instr |= (carry_in & 1) << 4
    elif select == 0b10:
        instr |= (op & 0b11) << 4
    return instr & 0xFF


def set_in(dut, value):
    getattr(dut, "in").value = value


async def do_reset(dut):
    dut.rst.value = 1
    set_in(dut, 0)
    await ClockCycles(dut.clk, 3)
    dut.rst.value = 0
    await Timer(1, unit="ns")


async def run_operation(dut, instr, a, b):
    set_in(dut, instr)
    await RisingEdge(dut.clk)
    set_in(dut, a)
    await RisingEdge(dut.clk)
    set_in(dut, b)
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


@cocotb.test()
async def test_decoder_arithmetic(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await do_reset(dut)

    instr = make_instr(select=0b01, mod_sub=0, carry_in=0)
    await run_operation(dut, instr, 20, 22)
    assert dut.out.value == 42
    assert dut.carry_flag.value == 0


@cocotb.test()
async def test_decoder_logic(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await do_reset(dut)

    instr = make_instr(select=0b10, op=0b00)  # AND
    await run_operation(dut, instr, 0xFF, 0x3C)
    assert dut.out.value == 0x3C


@cocotb.test()
async def test_decoder_shift(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await do_reset(dut)

    instr = make_instr(select=0b00, shift_iz_der=0, shift_amount=2)
    await run_operation(dut, instr, 0b0000_0011, 0)
    assert dut.out.value == 0b0000_1100


@cocotb.test()
async def test_decoder_reset_limpia_registros(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await do_reset(dut)

    instr = make_instr(select=0b01)
    await run_operation(dut, instr, 0, 0)
    assert dut.out.value == 0
    assert dut.zeros_flag.value == 1
