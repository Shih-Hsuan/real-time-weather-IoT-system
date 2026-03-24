#include "sys.h"
#include "delay.h"
#include "usart.h"
#include "led.h"

int main(void) {
    u8 t;
    u16 len;
    
    // System Initialization
    NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);
    delay_init(168);
    uart_init(115200);   // UART1: Communicates with Delta HMI
    uart2_init(9600);    // UART2: Communicates with ESP32
    LED_Init();
    
    while (1) {
        /* ---------------------------------------------------
           Route 1: ESP32 -> STM32 -> Delta HMI
           Receive parsed weather string from ESP32, send to HMI
           --------------------------------------------------- */
        if (USART_RX_STA2 & 0x8000) {
            len = USART_RX_STA2 & 0x3fff;
            for(t = 0; t < len; t++) {
                // Send data to HMI via UART1
                USART_SendData(USART1, USART_RX_BUF2[t]);
                while (USART_GetFlagStatus(USART1, USART_FLAG_TC) != SET);
            }
            USART_RX_STA2 = 0; // Clear receive flag
        }

        /* ---------------------------------------------------
           Route 2: Delta HMI -> STM32 -> ESP32
           Receive city selection from HMI, translate & send to ESP32
           --------------------------------------------------- */
        if (USART_RX_STA == 1) {
            char city_cmd = '\0';
            
            // Translate HMI input to character command
            if      (USART_RX_BUF[0] == 0) city_cmd = 'K'; // Keelung
            else if (USART_RX_BUF[0] == 1) city_cmd = 'M'; // Miaoli
            else if (USART_RX_BUF[0] == 2) city_cmd = 'N'; // Tainan
            else if (USART_RX_BUF[0] == 3) city_cmd = 'O'; // Osaka
            else if (USART_RX_BUF[0] == 4) city_cmd = 'S'; // Seoul
            else if (USART_RX_BUF[0] == 5) city_cmd = 'L'; // London

            // Send command to ESP32 via UART2
            if (city_cmd != '\0') {
                USART_SendData(USART2, city_cmd);
                while (USART_GetFlagStatus(USART2, USART_FLAG_TC) != SET);
                USART_SendData(USART2, '\n');
                while (USART_GetFlagStatus(USART2, USART_FLAG_TC) != SET);
            }
            USART_RX_STA = 0; // Clear receive flag
        }
    }
}
