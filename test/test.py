# test/test.py
# SPDX-FileCopyrightText: © 2026 Joaquín O'Ryan
# SPDX-License-Identifier: Apache-2.0
"""Integration tests for the complete Tiny Tapeout wrapper.

Protocol: three bytes are sent through ui_in:
    1) instruction
    2) operand A
    3) operand B

Flags are exposed on uio_out:
    bit 0 = carry
    bit 1 = negative
    bit 2 = overflow
    bit 3 = zero
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, Timer

MASK8 = 0xFF


def make_instr(select, shift_iz_der=0, shift_arit_right=0, shift_amount=0,
               mod_sub=0, carry_in=0, op=0):
    """Build the instruction byte expected by decoder_alu.v."""
    instr = (select & 0b11) << 6

    if select == 0b00:  # barrel shifter
        instr |= (shift_iz_der & 1) << 5
        instr |= (shift_arit_right & 1) << 4
        instr |= (shift_amount & 0b111) << 1
    elif select == 0b01:  # arithmetic
        instr |= (mod_sub & 1) << 5
        instr |= (carry_in & 1) << 4
    elif select == 0b10:  # logic
        instr |= (op & 0b11) << 4

    return instr & 0xFF


def signed8(value):
    value &= MASK8
    return value - 256 if value & 0x80 else value


def arithmetic_expected(a, b, mod_sub, carry_in):
    """Independent reference model for the arithmetic block."""
    b_op = (~b if mod_sub else b) & MASK8
    full = a + b_op + carry_in
    result = full & MASK8
    carry = (full >> 8) & 1
    overflow = int(((a ^ result) & (b_op ^ result) & 0x80) != 0)
    return result, carry, overflow


def flags_expected(result, carry=0, overflow=0):
    return {
        "carry": carry & 1,
        "negative": (result >> 7) & 1,
        "overflow": overflow & 1,
        "zero": int((result & MASK8) == 0),
    }


def read_flags(dut):
    flags = dut.uio_out.value.integer & 0x0F
    return {
        "carry": (flags >> 0) & 1,
        "negative": (flags >> 1) & 1,
        "overflow": (flags >> 2) & 1,
        "zero": (flags >> 3) & 1,
    }


async def run_operation(dut, instr, a, b):
    """Send instruction, A and B, then allow combinational logic to settle."""
    dut.ui_in.value = instr & MASK8
    await RisingEdge(dut.clk)
    dut.ui_in.value = a & MASK8
    await RisingEdge(dut.clk)
    dut.ui_in.value = b & MASK8
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


async def check_operation(dut, name, instr, a, b, expected, expected_flags):
    await run_operation(dut, instr, a, b)
    actual = dut.uo_out.value.integer
    actual_flags = read_flags(dut)

    assert actual == expected, (
        f"{name}: result mismatch: A=0x{a:02X}, B=0x{b:02X}, "
        f"expected=0x{expected:02X}, got=0x{actual:02X}"
    )
    assert actual_flags == expected_flags, (
        f"{name}: flags mismatch: A=0x{a:02X}, B=0x{b:02X}, "
        f"expected={expected_flags}, got={actual_flags}"
    )


@cocotb.test()
async def test_project(dut):
    dut._log.info("Starting complete ALU integration test")

    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Active-low Tiny Tapeout reset.
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # Arithmetic: addition and carry.
    for a, b, cin in [(5, 3, 0), (0xFF, 1, 0), (0xFF, 0xFF, 1),
                      (0, 0, 0), (0x80, 0x80, 0)]:
        expected, carry, overflow = arithmetic_expected(a, b, 0, cin)
        await check_operation(
            dut, "ADD", make_instr(1, carry_in=cin), a, b,
            expected, flags_expected(expected, carry, overflow)
        )

    # Arithmetic: two's-complement subtraction A + ~B + carry_in.
    for a, b, cin in [(10, 4, 1), (0, 1, 1), (3, 8, 1),
                      (0x7F, 0xFF, 1), (0x80, 1, 1)]:
        expected, carry, overflow = arithmetic_expected(a, b, 1, cin)
        await check_operation(
            dut, "SUB", make_instr(1, mod_sub=1, carry_in=cin), a, b,
            expected, flags_expected(expected, carry, overflow)
        )

    # Logic: AND, OR, XOR and NOT.
    logic_vectors = [(0xF0, 0x3C), (0xAA, 0x55), (0x00, 0xFF),
                     (0xFF, 0xFF), (0x00, 0x00)]
    logic_functions = {
        0b00: lambda a, b: a & b,
        0b01: lambda a, b: a | b,
        0b10: lambda a, b: a ^ b,
        0b11: lambda a, b: (~a) & MASK8,
    }
    for op, function in logic_functions.items():
        for a, b in logic_vectors:
            expected = function(a, b) & MASK8
            await check_operation(
                dut, f"LOGIC op={op:02b}", make_instr(2, op=op), a, b,
                expected, flags_expected(expected)
            )

    # Shifts: left, logical right and arithmetic right, all amounts 0..7.
    shift_vectors = [0x00, 0x01, 0x02, 0x55, 0x80, 0xAA, 0xFF]
    for a in shift_vectors:
        for amount in range(8):
            # Left shift. Carry is the last bit shifted out.
            expected = (a << amount) & MASK8
            carry = 0 if amount == 0 else (a >> (8 - amount)) & 1
            await check_operation(
                dut, "SHIFT LEFT", make_instr(0, shift_amount=amount), a, 0,
                expected, flags_expected(expected, carry)
            )

            # Logical right shift.
            expected = (a >> amount) & MASK8
            carry = 0 if amount == 0 else (a >> (amount - 1)) & 1
            await check_operation(
                dut, "SHIFT RIGHT LOGICAL",
                make_instr(0, shift_iz_der=1, shift_arit_right=0,
                            shift_amount=amount), a, 0,
                expected, flags_expected(expected, carry)
            )

            # Arithmetic right shift.
            expected = (signed8(a) >> amount) & MASK8
            await check_operation(
                dut, "SHIFT RIGHT ARITHMETIC",
                make_instr(0, shift_iz_der=1, shift_arit_right=1,
                            shift_amount=amount), a, 0,
                expected, flags_expected(expected, carry)
            )

    # Pass-through mode (select=11).
    for a in [0x00, 0x01, 0x5A, 0x80, 0xFF]:
        await check_operation(
            dut, "PASS THROUGH", make_instr(3), a, 0,
            a, flags_expected(a)
        )

    dut._log.info("All integration tests passed")
