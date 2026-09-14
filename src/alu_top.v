module alu_top 
(
    //entrada de datos
    input wire [7:0] in_a,
    input wire [7:0] in_b,
    //señales de control
    //para la unidad desplazadora
    input wire [2:0] shift_amount,
    input wire SHIFT_IZ_DER,
    input wire SHIFT_ARIT_RIGHT,
    //para la unidad aritmética
    input wire carry_in,
    input wire mod_sub,
    //para la unidad lógica
    input  wire [1:0] op,
    //para la unidad de control
    input wire [1:0] select,
    //salida de datos
    output wire [7:0] out,
    output wire carry_out,
    output wire overflow_flag,
    output wire zero_flag,
    output wire negative_flag
);

//etapa media de los datos
 wire [7:0] arit_out;
 wire [7:0] logic_out; 
 wire [7:0] shift_out;
 wire       arit_carry; 
 wire       arit_overflow; 
 wire       shift_carry;

//Llamar los modulos de la ALU
arithmetic arithmetic_i
(
    .in_a(in_a),
    .in_b(in_b),
    .carry_in(carry_in),
    .mod_sub(mod_sub),
    .arit_out(arit_out),
    .carry_out(arit_carry),
    .overflow_flag(arit_overflow)
);
Logico_8bits logic_i
(
    .IN_A(in_a),
    .IN_B(in_b),
    .op(op),
    .out(logic_out)
);
barrel_shifter  shift_i
(
    .IN_A_BUS_8bits(in_a),
    .shift_amount(shift_amount),
    .SHIFT_IZ_DER(SHIFT_IZ_DER),
    .SHIFT_ARIT_RIGHT(SHIFT_ARIT_RIGHT),
    .OUT_BUS_8bits(shift_out),
    .Carry_flag(shift_carry)
);

//variables intermedias para el case
reg [7:0] out_r;
reg       carry_out_r;
reg       overflow_flag_r;

//Logica de la Salida y la entrada
    always @(*)
        case(select)
            2'b00:begin 
                out_r=shift_out;//modo desplazador
                carry_out_r=shift_carry;
                overflow_flag_r=1'b0;
                end    
            2'b01:begin 
                out_r=arit_out;//modo aritmético
                carry_out_r=arit_carry;
                overflow_flag_r=arit_overflow;
                end
            2'b10:begin
                out_r=logic_out;//modo lógico
                carry_out_r=1'b0;
                overflow_flag_r=1'b0;
                end
            2'b11:begin
                out_r=in_a;//modo de paso de datos
                carry_out_r=1'b0;
                overflow_flag_r=1'b0;
                end
        endcase
    //preparar la salida de la ALU
assign out           = out_r;
assign carry_out     = carry_out_r;
assign overflow_flag = overflow_flag_r;
assign zero_flag     = (out == 8'b0);
assign negative_flag = out[7];

endmodule