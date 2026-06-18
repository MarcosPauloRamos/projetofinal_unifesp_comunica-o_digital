/*
Novo UART_Manager

Protocolo FPGA -> Python:

LCD:
byte 0 = 0
byte 1 = codigo da mensagem LCD

DISPLAY:
byte 0 = 1
byte 1 = parte alta do valor
byte 2 = parte baixa do valor

Python -> FPGA:
recebe 1 byte e entrega em data_receive
*/

module UART_Manager
#(
    parameter DATA_WIDTH = 16
)
(
    input send,
    input lcd_send,
    input clk_auto,

    input [15:0] output_data,
    input [7:0] lcd_code,

    input UART_RX,
    output UART_TX,

    output wire [15:0] data_receive
);

    wire rx_data;
    wire tx_data;

    wire rdempty;

    reg read;
    reg write;

    wire [7:0] uart_data_read;
    reg  [7:0] uart_data_write;

    reg [15:0] UART_reg;

    reg count;

    reg send_d;
    reg lcd_send_d;

    wire send_pulse;
    wire lcd_send_pulse;

    reg [2:0] state;

    localparam IDLE          = 3'd0;
    localparam LCD_TYPE      = 3'd1;
    localparam LCD_VALUE     = 3'd2;
    localparam DISPLAY_TYPE  = 3'd3;
    localparam DISPLAY_HIGH  = 3'd4;
    localparam DISPLAY_LOW   = 3'd5;

    assign UART_TX = tx_data;

    assign rx_data = UART_RX;

    assign data_receive = UART_reg;

    assign send_pulse = send & ~send_d;

    assign lcd_send_pulse = lcd_send & ~lcd_send_d;

    uart_control UART0(
        .clk(clk_auto),
        .reset_n(1'b1),

        .write(write),
        .writedata(uart_data_write),

        .read(read),
        .readdata(uart_data_read),
        .rdempty(rdempty),

        .uart_clk_25m(count),
        .uart_tx(tx_data),
        .uart_rx(rx_data)
    );

    /*
    Divisor simples usado pelo uart_control original
    */
    always @(posedge clk_auto)
    begin
        count <= count + 1'b1;
    end

    /*
    Detectores de borda
    */
    always @(posedge clk_auto)
    begin
        send_d <= send;
        lcd_send_d <= lcd_send;
    end

    /*
    Recepcao Python -> FPGA
    */
    always @(posedge clk_auto)
    begin
        if (!rdempty)
        begin
            read <= 1'b1;
            UART_reg <= {8'b0, uart_data_read};
        end
        else
        begin
            read <= 1'b0;
        end
    end

    /*
    Transmissao FPGA -> Python
    */
    always @(posedge clk_auto)
    begin
        write <= 1'b0;

        case (state)

            IDLE:
            begin
                if (lcd_send_pulse)
                begin
                    state <= LCD_TYPE;
                end
                else if (send_pulse)
                begin
                    state <= DISPLAY_TYPE;
                end
                else
                begin
                    state <= IDLE;
                end
            end

            /*
            Pacote LCD:
            [0][codigo]
            */

            LCD_TYPE:
            begin
                uart_data_write <= 8'd0;
                write <= 1'b1;
                state <= LCD_VALUE;
            end

            LCD_VALUE:
            begin
                uart_data_write <= lcd_code;
                write <= 1'b1;
                state <= IDLE;
            end

            /*
            Pacote DISPLAY:
            [1][high][low]
            */

            DISPLAY_TYPE:
            begin
                uart_data_write <= 8'd1;
                write <= 1'b1;
                state <= DISPLAY_HIGH;
            end

            DISPLAY_HIGH:
            begin
                uart_data_write <= output_data[15:8];
                write <= 1'b1;
                state <= DISPLAY_LOW;
            end

            DISPLAY_LOW:
            begin
                uart_data_write <= output_data[7:0];
                write <= 1'b1;
                state <= IDLE;
            end

            default:
            begin
                state <= IDLE;
            end

        endcase
    end

endmodule
