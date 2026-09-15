module decoder_alu 
(
    // entrada
    input wire [7:0] in,
    // secuencial
    input wire clk,
    input wire rst,
    // salida
    output wire [7:0] out,
    // flags
    output wire carry_flag,
    output wire negative_flag,
    output wire overflow_flag,
    output wire zeros_flag
);

// guardar datos
/* verilator lint_off UNUSEDSIGNAL */
reg [7:0] reg_inst;
/* verilator lint_on UNUSEDSIGNAL */
// instruccion
reg [7:0] reg_A;    // dato a
reg [7:0] reg_B;    // dato b
reg [1:0] counter;  // contador

always @(posedge clk or posedge rst) 
begin
    if(rst) // poner los datos a 0
    begin
        counter <= 2'd0;
        reg_inst <= 8'd0;
        reg_A <= 8'd0;
        reg_B <= 8'd0;
    end
    else
    begin
        case (counter) // inicia el contador
            2'd0: begin // si es 0 enviar datos a el registro instruccion y sumar uno al contador
                reg_inst <= in;
                reg_A <=8'd0;//reinicia datos (evita operar con datos anteriores)
                reg_B <=8'd0;
                counter <= 2'd1;
            end
            2'd1: begin // si es 1 enviar datos a el registro de dato A y sumar uno al contador
                reg_A <= in;
                counter <= 2'd2;
            end
            2'd2: begin // si es 2 enviar datos a el registro de dato B y poner contador en 0
                reg_B <= in;
                counter <= 2'd0;
            end
            default: counter <= 2'd0; // caso de inicio es 0
        endcase
    end
end

// separar valores del registro de intruccion
reg [2:0] ctrl_shift_amount;
reg ctrl_shift_iz_der;
reg ctrl_shift_arit_right;
reg ctrl_carry_in;
reg ctrl_mod_sub;
reg [1:0] ctrl_op;
reg [1:0] ctrl_select;

always @(*) 
begin
    // 1. Valores por defecto (evita latches)
    ctrl_shift_amount = 3'b000;
    ctrl_shift_iz_der = 1'b0;
    ctrl_shift_arit_right = 1'b0;
    ctrl_carry_in = 1'b0;
    ctrl_mod_sub = 1'b0;
    ctrl_op = 2'b00;

    // 2. Extracción directa del Opcode principal
    // Los bits [7:6] van directos al selector de la ALU
    ctrl_select = reg_inst[7:6];
    
    case (ctrl_select)
        2'b00: begin
            ctrl_shift_iz_der     = reg_inst[5];   // Dirección 
            ctrl_shift_arit_right = reg_inst[4];   // Lógico/Aritmético
            ctrl_shift_amount     = reg_inst[3:1]; // Cantidad a desplazar
        end
        2'b01: begin
            ctrl_mod_sub          = reg_inst[5];   // modo de operacion
            ctrl_carry_in         = reg_inst[4];   // carry
        end
        2'b10: begin
            ctrl_op               = reg_inst[5:4]; // modo de operacion logica
        end
        default: begin
            // Evita latches para condiciones no definidas explícitamente
        end
    endcase
end

// Instanciación fuera de los bloques procedimentales
alu_top alu_top_i
(
    .in_a(reg_A),
    .in_b(reg_B),
    .shift_amount(ctrl_shift_amount),
    .SHIFT_IZ_DER(ctrl_shift_iz_der),
    .SHIFT_ARIT_RIGHT(ctrl_shift_arit_right), // Corregido
    .carry_in(ctrl_carry_in),
    .mod_sub(ctrl_mod_sub),
    .op(ctrl_op),
    .select(ctrl_select),

    .out(out),
    .carry_out(carry_flag),
    .overflow_flag(overflow_flag),
    .zero_flag(zeros_flag),
    .negative_flag(negative_flag)
);

endmodule
