---
title:  "ALU CASS PUCV"
author: "CASS PUCV"
---
# ALU CASS PUCV

Este proyecto implementa una ALU de 8 bits. Debido a la restricción de 24 pines del formato Tiny Tapeout, la ALU utiliza una arquitectura de carga serial multiplexada en el tiempo, controlada por una máquina de estados finitos (FSM) de 3 estados, que permite cargar operandos y opcode de forma secuencial antes de ejecutar la operación.

## How it works
La ALU decodifica un opcode de 8 bits según un esquema tipo ISA, donde los dos bits más significativos determinan el modo de operación:

- `00`: desplazamiento (barrel shifter) — izquierda, derecha lógico o derecha aritmético, con magnitud de 0 a 7 bits.
- `01`: aritmética — suma o resta en complemento a dos, con soporte de carry_in.
- `10`: lógica — AND, OR, XOR o NOT.
- `11`: bypass — pasa `in_a` directamente a la salida.

Internamente, `alu_top.v` instancia tres módulos combinacionales en paralelo (`arithmetic.v`, `Logico_8bits.v` y `barrel_shifter.v`); sus resultados y banderas (carry, overflow) llegan a un multiplexor que selecciona la salida final según `select[1:0]`. Las banderas `zero_flag` y `negative_flag` se calculan directamente sobre la salida `out`, independientemente del modo activo (en modo lógico, `negative_flag` no tiene significado de signo).

Nota de diseño relevante: en modo resta con `carry_in = 0`, el resultado es `A − B − 1` y no `A − B`, ya que `arithmetic.v` opera en complemento a uno para la resta.

## How to test
Para probar este diseño, se deben asignar los valores de entrada a través de los pines correspondientes y observar los resultados en los pines de salida. (Agreguen un par de líneas sobre qué estímulos aplican en los testbench).
