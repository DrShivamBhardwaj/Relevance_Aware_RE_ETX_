/*
 * PAPER024501: isolated distributed context message transport and cost pilot.
 *
 * Three-node NullNet experiment; 1=sink, 2=context sender+report source,
 * 3=context receiver+report source. Source observations are synthetic.
 * Each mode spans 30 seconds: 0, 13, 25, 50 application bytes of neighbour
 * context. Separate packet and report phases avoid artificial frame bursts.
 *
 * PURPOSE: measure actual context frame reception and whole-board power.
 * NOT an implementation of original 100-node central-context simulator;
 * NOT evidence that overall C3 energy reductions survive physical deployment.
 */
#include "contiki.h"
#include "net/nullnet/nullnet.h"
#include "net/netstack.h"
#include "net/linkaddr.h"
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#ifndef PAPER_ROLE
#define PAPER_ROLE 0
#endif
#ifndef PAPER_BROADCAST
#define PAPER_BROADCAST 0
#endif
#define TICK_SECONDS 1
#define MODE_SECONDS 30
#define CONTEXT_KIND 0x33
#define DATA_KIND 0x34
#define HEADER_BYTES 12
static uint8_t packet[80];
static unsigned context_tx[4],ctx_rx[4],report_tx[4],report_rx[4];
static uint16_t received_sample;
static unsigned role(void) {
 return PAPER_ROLE?PAPER_ROLE:(unsigned)linkaddr_node_addr.u8[0];
}
static unsigned mode_for(unsigned second) {
 return (second/MODE_SECONDS)%4u;
}
static unsigned context_len(unsigned mode) {
 static const unsigned lengths[4]={0u,13u,25u,50u};
 return lengths[mode];
}
static void put16(uint8_t *dest,uint16_t v){
 dest[0]=(uint8_t)v; dest[1]=(uint8_t)(v>>8);
}
static uint16_t get16(const uint8_t *src) {
 return (uint16_t)src[0] | ((uint16_t)src[1]<<8);
}
static void on_recv(const void *d,uint16_t size,const linkaddr_t *src,const linkaddr_t *dst){
 const uint8_t *p=(const uint8_t *)d;
 unsigned m;
 (void)src;(void)dst;
 if(size<HEADER_BYTES)return;
 m=p[2];
 if(m>3)return;
 if(p[0]==CONTEXT_KIND && role()==3 && p[1]==2) {
   if(size!=context_len(m))return;
   received_sample=get16(p+6);
   ctx_rx[m]++;
   printf("CONTEXT_RX role=3 mode=%u second=%u bytes=%u sample=%u count=%u\n",
          m,(unsigned)get16(p+4),size,(unsigned)received_sample,ctx_rx[m]);
 } else if(p[0]==DATA_KIND && role()==1 && p[1]>=2 && p[1]<=3) {
   report_rx[m]++;
   printf("REPORT_RX source=%u mode=%u second=%u bytes=%u count=%u\n",
          (unsigned)p[1],m,(unsigned)get16(p+4),size,report_rx[m]);
 }
}
static void send_pkt(unsigned type,unsigned mode,unsigned second,unsigned len) {
 if(len>sizeof(packet) || len<HEADER_BYTES)return;
 memset(packet,0x5a,len);
 packet[0]=(uint8_t)type;
 packet[1]=(uint8_t)role();
 packet[2]=(uint8_t)mode;
 packet[3]=0;
 put16(packet+4,(uint16_t)second);
 put16(packet+6,(uint16_t)((second*37u+(unsigned)role()*13u)%1024u));
 nullnet_buf=packet;
 nullnet_len=(uint16_t)len;
 /* Broadcast for M3; Cooja topology has all three nodes in radio range.
    Distinguish application reception from PHY ACK events. */
 NETSTACK_NETWORK.output(NULL);
}
PROCESS(context_cost_process,"PAPER024501 real context-packet cost trial");
AUTOSTART_PROCESSES(&context_cost_process);
PROCESS_THREAD(context_cost_process,ev,data){
 static struct etimer timer;
 static unsigned second,m,lastmode;
 PROCESS_BEGIN();
 second=0; lastmode=99u;
 nullnet_set_input_callback(on_recv);
 printf("CONTEXT_PILOT_START role=%u broadcast=%d\n",role(),PAPER_BROADCAST);
 etimer_set(&timer,TICK_SECONDS*CLOCK_SECOND);
 while(1){
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
  m=mode_for(second);
  if(m!=lastmode){
    printf("CONTEXT_PHASE role=%u mode=%u second=%u bytes=%u\n",
           role(),m,second,context_len(m));
    lastmode=m;
  }
  if(role()==2 && second%4==1 && context_len(m)>0){
    send_pkt(CONTEXT_KIND,m,second,context_len(m));
    context_tx[m]++;
    printf("CONTEXT_TX mode=%u second=%u bytes=%u count=%u\n",
      m,second,context_len(m),context_tx[m]);
  }
  if(role()==3 && second%4==2){
    send_pkt(DATA_KIND,m,second,32);
    report_tx[m]++;
    printf("REPORT_TX source=3 mode=%u second=%u count=%u\n",
     m,second,report_tx[m]);
  }
  if(role()==2 && second%4==3){
    send_pkt(DATA_KIND,m,second,32);
    report_tx[m]++;
    printf("REPORT_TX source=2 mode=%u second=%u count=%u\n",
     m,second,report_tx[m]);
  }
  second++;
  etimer_reset(&timer);
 }
 PROCESS_END();
}
