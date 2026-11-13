/* Phase-resolved M3 hardware power experiment, 4 × 20s phases:
 * 0 ambient baseline with radio stack active
 * 1 real ISL29020 light sensor turned on and sampled 16x per second
 * 2 calibrated busy-work CPU operations per second
 * 3 NullNet 4 × 64B broadcast frames per second
 * Logs tagged at phase boundaries for OML power timestamp matching.
 * NOT original RE-ETX algorithm, no independent RF-only measurement.
 */
#include "contiki.h"
#include "dev/light-sensor.h"
#include "lib/sensors.h"
#include "net/nullnet/nullnet.h"
#include "net/netstack.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>
static uint8_t packet[64];
static volatile uint32_t checksum;
static int sensor_on;
static void on_recv(const void *data,uint16_t len,
                    const linkaddr_t *src,const linkaddr_t *dst) {
  (void)data; (void)len;(void)src;(void)dst;
}
PROCESS(phase_power_v2_process,"PAPER024501 M3 real sensing and radio phases");
AUTOSTART_PROCESSES(&phase_power_v2_process);
PROCESS_THREAD(phase_power_v2_process, ev, data) {
 static struct etimer tick;
 static unsigned second,phase,last_phase;
 static unsigned i;
 static int sample;
 PROCESS_BEGIN();
 memset(packet,0xA5,sizeof(packet));
 nullnet_set_input_callback(on_recv);
 sensor_on=0;
 second=0;
 last_phase=255;
 printf("PHASE_V2_INIT\n");
 etimer_set(&tick,CLOCK_SECOND);
 while(1) {
   PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&tick));
   phase=(second/20)%4;
   if(phase != last_phase) {
      if(sensor_on) {
         SENSORS_DEACTIVATE(light_sensor);
         sensor_on=0;
      }
      if(phase==1) {
         SENSORS_ACTIVATE(light_sensor);
         sensor_on=1;
      }
      printf("PHASE_V2_START phase=%u tick=%u\n",phase,second);
      last_phase=phase;
   }
   if(phase==1) {
      for(i=0;i<16;i++) {
         sample=light_sensor.value(LIGHT_SENSOR_SOURCE);
         checksum+=(unsigned)sample;
      }
   } else if(phase==2) {
      for(i=0;i<2000000UL;i++) {
         checksum=checksum*1664525UL + 1013904223UL;
      }
   } else if(phase==3) {
      for(i=0;i<4;i++) {
         nullnet_buf=packet;
         nullnet_len=sizeof(packet);
         NETSTACK_NETWORK.output(NULL);
      }
   }
   second++;
   etimer_reset(&tick);
 }
 PROCESS_END();
}
