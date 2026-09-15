# test/test.py
# SPDX-FileCopyrightText: © 2026 Joaquín O'Ryan
# SPDX-License-Identifier: Apache-2.0
"""
Test de integracion del chip Tiny Tapeout completo (src/project.v).

El diseno se maneja SOLO por los pines fisicos (ui_in / uo_out / uio_out),
asi que el mismo test sirve para RTL y para gate level.

Protocolo del decodificador serie (decoder_alu.v). Cada operacion se carga
en 3 flancos de subida consecutivos de clk a traves de ui_in:

    flanco 1  (contador = 0)  ->  byte de instruccion
    flanco 2  (contador = 1)  ->  operando A
    flanco 3  (contador = 2)  ->  operando B, el contador vuelve a 0

IMPORTANTE: el reset asincrono ya deja el contador en 0. NO hay que
"quemar" un flanco extra despues de soltar rst_n: ese flanco cargaria
ui_in como instruccion y dejaria el contador en 1, desalineando todo el
protocolo (los 3 bytes siguientes entrarian corridos en un lugar).

Mapa de uio_out (ver project.v):

    uio_out[0] = carry_flag
    uio_out[1] = negative_flag
    uio_out[2] = overflow_flag
    uio_out[3] = zeros_flag
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer

MASK8 = 0xFF

# Reloj lento a proposito: deja muchisimo margen para la logica
# combinacional, tanto en RTL como en gate level.
CLOCK_PERIOD_US = 10

# Margen despues del tercer flanco antes de leer las salidas.
# 100 ns es el 1% del periodo, asi que nunca se acerca al flanco siguiente.
SETTLE_NS = 100


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def to_int(handle):
    """Lee un puerto como entero sin signo.

    cocotb 2.x devuelve LogicArray (usa to_unsigned); cocotb 1.x devuelve
    BinaryValue (usa integer). Asi el test funciona con las dos versiones
    y no dispara DeprecationWarning.
    """
    value = handle.value
    to_unsigned = getattr(value, "to_unsigned", None)
    return to_unsigned() if to_unsigned is not None else value.integer


def make_instr(select, shift_iz_der=0, shift_arit_right=0,
               shift_amount=0, mod_sub=0, carry_in=0, op=0):
    """Arma el byte de instruccion que espera decoder_alu.v."""

    instr = (select & 0b11) << 6

    if select == 0b00:                       # desplazador
        instr |= (shift_iz_der & 1) << 5
        instr |= (shift_arit_right & 1) << 4
        instr |= (shift_amount & 0b111) << 1

    elif select == 0b01:                     # aritmetica
        instr |= (mod_sub & 1) << 5
        instr |= (carry_in & 1) << 4

    elif select == 0b10:                     # logica
        instr |= (op & 0b11) << 4

    return instr & MASK8


def signed8(value):
    value &= MASK8
    return value - 256 if value & 0x80 else value


def arithmetic_expected(a, b, mod_sub, carry_in):
    """Modelo de src/arithmetic.v."""

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
        "zero": int(result == 0),
    }


def read_flags(dut):
    flags = to_int(dut.uio_out) & 0x0F

    return {
        "carry": (flags >> 0) & 1,
        "negative": (flags >> 1) & 1,
        "overflow": (flags >> 2) & 1,
        "zero": (flags >> 3) & 1,
    }


# ---------------------------------------------------------------------------
# Manejo del protocolo
# ---------------------------------------------------------------------------

async def reset_dut(dut):
    """Deja el chip listo con el contador del decodificador en 0."""

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # El reset de Tiny Tapeout es activo en bajo.
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 10)

    # Se suelta el reset justo despues de un flanco: queda casi un periodo
    # completo de margen hasta el flanco siguiente, que ya sera el que
    # cargue el primer byte de instruccion.
    dut.rst_n.value = 1


async def run_operation(dut, instr, a, b):
    """Envia una operacion completa (instruccion, A, B) por ui_in.

    Consume exactamente 3 flancos, de modo que al terminar el contador
    del decodificador vuelve a 0 y la siguiente llamada queda alineada.
    """

    dut.ui_in.value = instr & MASK8
    await RisingEdge(dut.clk)        # contador 0 -> carga instruccion

    dut.ui_in.value = a & MASK8
    await RisingEdge(dut.clk)        # contador 1 -> carga A

    dut.ui_in.value = b & MASK8
    await RisingEdge(dut.clk)        # contador 2 -> carga B

    # Deja asentar la logica combinacional de la ALU.
    await Timer(SETTLE_NS, unit="ns")


async def check_operation(dut, name, instr, a, b, expected, expected_flags):

    await run_operation(dut, instr, a, b)

    actual = to_int(dut.uo_out)
    actual_flags = read_flags(dut)

    assert actual == expected, (
        f"{name}: resultado incorrecto: "
        f"instr=0x{instr:02X}, "
        f"A=0x{a:02X}, "
        f"B=0x{b:02X}, "
        f"esperado=0x{expected:02X}, "
        f"obtenido=0x{actual:02X}"
    )

    assert actual_flags == expected_flags, (
        f"{name}: banderas incorrectas: "
        f"instr=0x{instr:02X}, "
        f"A=0x{a:02X}, "
        f"B=0x{b:02X}, "
        f"esperado={expected_flags}, "
        f"obtenido={actual_flags}"
    )


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

@cocotb.test()
async def test_project(dut):

    dut._log.info("Inicio del test de integracion de la ALU")

    cocotb.start_soon(Clock(dut.clk, CLOCK_PERIOD_US, unit="us").start())

    await reset_dut(dut)

    # -----------------------------------------------------------------
    # SUMA
    # -----------------------------------------------------------------

    dut._log.info("Suma")

    for a, b, cin in [
        (0x05, 0x03, 0),
        (0xFF, 0x01, 0),
        (0xFF, 0xFF, 1),
        (0x00, 0x00, 0),
        (0x80, 0x80, 0),
    ]:
        expected, carry, overflow = arithmetic_expected(a, b, 0, cin)

        await check_operation(
            dut,
            "ADD",
            make_instr(select=0b01, carry_in=cin),
            a,
            b,
            expected,
            flags_expected(expected, carry, overflow),
        )

    # -----------------------------------------------------------------
    # RESTA (mod_sub invierte B, carry_in=1 completa el complemento a 2)
    # -----------------------------------------------------------------

    dut._log.info("Resta")

    for a, b, cin in [
        (10, 4, 1),
        (0, 1, 1),
        (3, 8, 1),
        (0x7F, 0xFF, 1),
        (0x80, 1, 1),
    ]:
        expected, carry, overflow = arithmetic_expected(a, b, 1, cin)

        await check_operation(
            dut,
            "SUB",
            make_instr(select=0b01, mod_sub=1, carry_in=cin),
            a,
            b,
            expected,
            flags_expected(expected, carry, overflow),
        )

    # -----------------------------------------------------------------
    # LOGICA
    # -----------------------------------------------------------------

    dut._log.info("Logica")

    logic_vectors = [
        (0xF0, 0x3C),
        (0xAA, 0x55),
        (0x00, 0xFF),
        (0xFF, 0xFF),
        (0x00, 0x00),
    ]

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
                dut,
                f"LOGIC op={op:02b}",
                make_instr(select=0b10, op=op),
                a,
                b,
                expected,
                flags_expected(expected),
            )

    # -----------------------------------------------------------------
    # DESPLAZAMIENTOS
    # -----------------------------------------------------------------

    dut._log.info("Desplazamientos")

    shift_vectors = [0x00, 0x01, 0x02, 0x55, 0x80, 0xAA, 0xFF]

    for a in shift_vectors:
        for amount in range(8):

            # Izquierda
            expected = (a << amount) & MASK8
            carry = 0 if amount == 0 else (a >> (8 - amount)) & 1

            await check_operation(
                dut,
                f"SHIFT LEFT {amount}",
                make_instr(select=0b00, shift_iz_der=0,
                           shift_arit_right=0, shift_amount=amount),
                a,
                0,
                expected,
                flags_expected(expected, carry),
            )

            # Derecha logica
            expected = (a >> amount) & MASK8
            carry = 0 if amount == 0 else (a >> (amount - 1)) & 1

            await check_operation(
                dut,
                f"SHIFT RIGHT LOGICAL {amount}",
                make_instr(select=0b00, shift_iz_der=1,
                           shift_arit_right=0, shift_amount=amount),
                a,
                0,
                expected,
                flags_expected(expected, carry),
            )

            # Derecha aritmetica (misma bandera de carry que la logica:
            # el RTL usa IN_A[shift_amount-1] en los dos casos)
            expected = (signed8(a) >> amount) & MASK8

            await check_operation(
                dut,
                f"SHIFT RIGHT ARITHMETIC {amount}",
                make_instr(select=0b00, shift_iz_der=1,
                           shift_arit_right=1, shift_amount=amount),
                a,
                0,
                expected,
                flags_expected(expected, carry),
            )

    # -----------------------------------------------------------------
    # PASO DE DATOS (select = 11 -> out = A)
    # -----------------------------------------------------------------

    dut._log.info("Paso de datos")

    for a in [0x00, 0x01, 0x5A, 0x80, 0xFF]:
        await check_operation(
            dut,
            "PASS THROUGH",
            make_instr(select=0b11),
            a,
            0,
            a,
            flags_expected(a),
        )

    dut._log.info("Todos los casos pasaron")
