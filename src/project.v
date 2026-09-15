// src/project.v
/*
 * Copyright (c) 2026 Joaquín O'Ryan
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_oryan01_alu (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // Señales internas hacia el decodificador serie + ALU
  wire       rst;
  wire [7:0] alu_out;
  wire       carry_flag;
  wire       negative_flag;
  wire       overflow_flag;
  wire       zeros_flag;

  // Tiny Tapeout entrega rst_n activo en bajo; decoder_alu espera rst activo en alto
  assign rst = ~rst_n;

  // Instancia del decodificador serie + ALU (arquitectura original, sin modificar)
  decoder_alu decoder_alu_i (
      .in(ui_in),
      .clk(clk),
      .rst(rst),
      .out(alu_out),
      .carry_flag(carry_flag),
      .negative_flag(negative_flag),
      .overflow_flag(overflow_flag),
      .zeros_flag(zeros_flag)
  );

  // Enrutamiento de pines segun el estandar Tiny Tapeout
  assign uo_out  = alu_out;                                              // resultado de 8 bits
  assign uio_out = {4'b0000, zeros_flag, overflow_flag, negative_flag, carry_flag};
  assign uio_oe  = 8'b0000_1111;  // uio[3:0]=salidas (flags), uio[7:4]=sin usar (entrada)

  // Evitar warnings de señales no usadas
  wire _unused = &{ena, uio_in, 1'b0};

endmodule
