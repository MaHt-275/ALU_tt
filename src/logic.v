// ==============================================================================
// SUBMÓDULO: Logico_8bits
// ==============================================================================
// Unidad combinacional que realiza operaciones logicas basicas AND, OR, XOR, NOT.
// ==============================================================================

module Logico_8bits (
    input  wire [7:0] IN_A,
    input  wire [7:0] IN_B,
    input  wire [1:0] op,       // Control LL
    output reg  [7:0] out
);

    always @(*) begin
        case (op)
            2'b00:   out = IN_A & IN_B;
            2'b01:   out = IN_A | IN_B;
            2'b10:   out = IN_A ^ IN_B;
            2'b11:   out = ~IN_A;
            default: out = 8'h00;
        endcase
    end

endmodule