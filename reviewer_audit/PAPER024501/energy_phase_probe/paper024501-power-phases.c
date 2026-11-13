/* PAPER024501 phase-resolved M3 diagnostic: controlled board-level power.
 * This is NOT the original application's sensor, and NOT RE-ETX firmware.
 * Each 20-second block alternates: base idle / CPU fixed work / radio TX.
 * All roles run the same schedule; serial phase tags support OML alignment.
 */
#include "contiki.h"
#include "net/netstack.h"
#include "net/nullnet/nullnet.h"
#include "net/linkaddr.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define PHASE_SECONDS 20
#define RADIO_CHUNK 64
static uint8_t msg[RADIO_CHUNK];
static volatile uint32_t checksum;
static void on_receive(const void *data, uint16_t len,
                        const linkaddr_t *src,const linkaddr_t *dest) {
  (void)data;(void)len;(void)src;(void)dest;
}
PROCESS(power_phase_process,"M3 phase power diagnostic");
AUTOSTART_PROCESSES(&power_phase_process);
PROCESS_THREAD(power_phase_process, ev, data) {
  static struct etimer timer;
  static uint16_t round;
  static uint8_t phase;
  static uint32_t i;
  PROCESS_BEGIN();
  nullnet_set_input_callback(on_receive);
  memset(msg,0xA7,sizeof(msg));
  printf("PHASE_PROBE_START node=%u\n",(unsigned)linkaddr_node_addr.u8[0]);
  round=0;
  while(1) {
    phase=(uint8_t)(round%3);
    printf("PHASE_START node=%u phase=%u round=%u\n",
           (unsigned)linkaddr_node_addr.u8[0],(unsigned)phase,(unsigned)round);
    etimer_set(&timer,PHASE_SECONDS*CLOCK_SECOND);
    while(!etimer_expired(&timer)) {
      if(phase==1) {
        /* Pure CPU busy work: only volatile accumulator observable */
        for(i=0;i<30000UL;i++) checksum=(checksum*1664525UL + 1013904223UL);
      } else if(phase==2) {
        /* Broadcast application frame; PHY/MAC output asynchronous */
        nullnet_buf=msg;nullnet_len=sizeof(msg);
        NETSTACK_NETWORK.output(NULL);
      }
      PROCESS_PAUSE();
    }
    printf("PHASE_END node=%u phase=%u round=%u checksum=%lu\n",
           (unsigned)linkaddr_node_addr.u8[0],(unsigned)phase,(unsigned)round,
           (unsigned long)checksum);
    round++;
  }
  PROCESS_END();
}
