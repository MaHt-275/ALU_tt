# test/test.py
# SPDX-FileCopyrightText: © 2026 Joaquín O'Ryan
# SPDX-License-Identifier: Apache-2.0
"""
Test de integracion del chip Tiny Tapeout completo (src/project.v).
Ejercita el diseno a traves de los pines fisicos ui_in / uo_out / uio_out,
tal como quedaria conectado en el silicio: decoder_alu (protocolo serie de
3 bytes: instruccion, A, B) + alu_top.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, Timer


def make_instr(select, shift_iz_der=0, shift_arit_right=0, shift_amount=0,
               mod_sub=0, carry_in=0, op=0):
    """Arma el byte de instruccion que espera decoder_alu.v"""
    instr = (select & 0b11) << 6
    if select == 0b00:      # desplazador
        instr |= (shift_iz_der & 1) << 5
        instr |= (shift_arit_right & 1) << 4
        instr |= (shift_amount & 0b111) << 1
    elif select == 0b01:    # aritmetica
        instr |= (mod_sub & 1) << 5
        instr |= (carry_in & 1) << 4
    elif select == 0b10:    # logica
        instr |= (op & 0b11) << 4
    return instr & 0xFF


async def run_operation(dut, instr, a, b):
    """Envia el protocolo serie completo (instruccion, A, B) por ui_in."""
    dut.ui_in.value = instr
    await RisingEdge(dut.clk)
    dut.ui_in.value = a
    await RisingEdge(dut.clk)
    dut.ui_in.value = b
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")  # deja asentar la logica combinacional


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Suma 5 + 3")
    instr = make_instr(select=0b01, mod_sub=0, carry_in=0)
    await run_operation(dut, instr, 5, 3)
    assert dut.uo_out.value == 8
    assert (dut.uio_out.value.integer & 0b0001) == 0  # sin acarreo

    dut._log.info("Resta 10 - 4 (mod_sub=1, carry_in=1)")
    instr = make_instr(select=0b01, mod_sub=1, carry_in=1)
    await run_operation(dut, instr, 10, 4)
    assert dut.uo_out.value == 6

    dut._log.info("AND logico 0xF0 & 0x3C")
    instr = make_instr(select=0b10, op=0b00)
    await run_operation(dut, instr, 0xF0, 0x3C)
    assert dut.uo_out.value == (0xF0 & 0x3C)

    dut._log.info("Desplazamiento a la izquierda 0x01 << 3")
    instr = make_instr(select=0b00, shift_iz_der=0, shift_amount=3)
    await run_operation(dut, instr, 0x01, 0x00)
    assert dut.uo_out.value == (0x01 << 3)

    dut._log.info("Modo paso de datos (select=11)")
    instr = make_instr(select=0b11)
    await run_operation(dut, instr, 0x5A, 0x00)
    assert dut.uo_out.value == 0x5A
