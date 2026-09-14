module barrel_shifter (
    input [7:0] IN_A_BUS_8bits,   
    input [2:0] shift_amount,
    input SHIFT_IZ_DER, SHIFT_ARIT_RIGHT,    
             
    output reg [7:0] OUT_BUS_8bits, 
    output reg       Carry_flag     
);

    

    always @(*) begin

        // Caso 1: Sin desplazamiento
        if (shift_amount == 3'd0) begin
            OUT_BUS_8bits = IN_A_BUS_8bits;
            Carry_flag    = 1'b0;
        end

	// Caso 2: Desplazamiento a la Izquierda
        else if (SHIFT_IZ_DER == 1'b0) begin
            OUT_BUS_8bits = IN_A_BUS_8bits << shift_amount;
            Carry_flag    = IN_A_BUS_8bits[8 - shift_amount];
        end

        // Caso 3: Desplazamiento a la Derecha (Lógico o Aritmético)
	else begin

            
        if (SHIFT_ARIT_RIGHT)
            OUT_BUS_8bits = $signed(IN_A_BUS_8bits) >>> shift_amount;
            else
            OUT_BUS_8bits = IN_A_BUS_8bits >> shift_amount;
            Carry_flag = IN_A_BUS_8bits[shift_amount - 1];
        end

    end

endmodule