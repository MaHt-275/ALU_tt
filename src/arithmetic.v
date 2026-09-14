module arithmetic
(
//ingreso de los 2 buses de datos//
input wire [7:0] in_a, 
input wire [7:0] in_b, 
//ingreso de señales de control//
input wire carry_in,
input wire mod_sub,//Importante destacar, 1 solo niega entrada B, para restar correctamente aplicar un C_in de 1//
//eso se hace para poder operar numeros mayores a posteriori//
//salida bus//
output reg [7:0] arit_out,
//banderas//
output reg carry_out,
output reg overflow_flag
);
reg [8:0] result; //Se declara un registro de 9 bits para almacenar el resultado de la operación aritmética//
//incluyendo el bit de acarreo//
wire [7:0] b_op; //Se declara un bus de 8 bits para almacenar el valor de entrada B modificado según el modo de operación//
assign b_op = mod_sub ? ~in_b : in_b;//forma corta de un if/else, si esta activo el modo resta asignar este valor//
//b_op//

always @(*)begin
        result = in_a + b_op + carry_in; //Se realiza la operación aritmética sumando los valores de entrada A y B modificados// 
        //junto con el bit de acarreo de entrada//
        arit_out  = result[7:0];
        carry_out = result[8];
        overflow_flag = (in_a[7] == b_op[7]) && (arit_out[7] != in_a[7]); //Se calcula la bandera de desbordamiento comparando// 
        //los bits de signo de las entradas y el resultado//
    end
endmodule