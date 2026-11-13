/*
 * PAPER024501 experimental NullNet payload-fragmentation diagnostic.
 * NOT RE-ETX or TSCH, and NOT a complete implementation of the manuscript.
 * Three motes: node 1 sink, nodes 2/3 source. 16-bit report sequence.
 * Binary header 8 bytes, up to 70 data bytes per fragment.
 */
#include "contiki.h"
#include "net/netstack.h"
#include "net/nullnet/nullnet.h"
#include "net/linkaddr.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define INTERVAL (8 * CLOCK_SECOND)
#define FRAGMENT 70
#define HEADER 8
#define MAX_FRAGS 8
#ifndef PAPER_ROLE
#define PAPER_ROLE 0
#endif
#ifndef PAPER_BROADCAST
#define PAPER_BROADCAST 0
#endif
#ifndef PAPER_STAGGER_SOURCE3
#define PAPER_STAGGER_SOURCE3 0
#endif
static uint8_t logical_role(void)
{
  return PAPER_ROLE ? PAPER_ROLE : linkaddr_node_addr.u8[0];
}
static linkaddr_t sink = {{1,0,0,0,0,0,0,0}};
static uint8_t frame[HEADER+FRAGMENT];
static uint16_t received_seq[4]={0};
static uint8_t received_count[4]={0};
static uint8_t received_total[4]={0};
static uint8_t received_bits[4]={0};

static unsigned short bits_for_relevance(unsigned short value_x100)
{
  /* ratio = .25 + .75*v, with safeguards at v>=.50 and v>=.85 */
  unsigned long bits=1000UL + 30UL*value_x100;
  if(value_x100>=50 && bits<3000UL)bits=3000UL;
  if(value_x100>=85)bits=4000UL;
  return (unsigned short)((bits/8UL)*8UL);
}

static void on_receive(const void *data,uint16_t len,
                       const linkaddr_t *src,const linkaddr_t *dst)
{
  const uint8_t *bytes=(const uint8_t *)data;
  if(logical_role()!=1 || len<HEADER)return;
  unsigned int source=bytes[6];
  unsigned int seq=(unsigned int)bytes[0] + ((unsigned int)bytes[1]<<8);
  unsigned int index=bytes[2], total=bytes[3];
  unsigned int app_bits=(unsigned int)bytes[4] + ((unsigned int)bytes[5]<<8);
  if(source<2 || source>3 || total<1 || total>MAX_FRAGS || index>=total)return;
  if(seq!=received_seq[source]) {
    received_seq[source]=(uint16_t)seq;
    received_count[source]=0;
    received_bits[source]=0;
    received_total[source]=(uint8_t)total;
  }
  if(!(received_bits[source] & (1U<<index))) {
    received_bits[source] |= (uint8_t)(1U<<index);
    received_count[source]++;
  }
  if(received_count[source]==received_total[source]) {
    printf("PAPER024501_RX_COMPLETE source=%u seq=%u bits=%u frags=%u\n",
           source,seq,app_bits,total);
    received_count[source]=0;
    received_bits[source]=0;
    received_seq[source]=0;
  }
}
PROCESS(paper024501_process,"PAPER024501 payload fragmentation reference");
AUTOSTART_PROCESSES(&paper024501_process);
PROCESS_THREAD(paper024501_process,ev,data)
{
  static struct etimer timer;
  static uint16_t seq;
  static unsigned short relevance;
  static unsigned short app_bits;
  static unsigned short bytes_left;
  static unsigned short payload_bytes;
  static unsigned short frag_index,total;
  PROCESS_BEGIN();
  nullnet_set_input_callback(on_receive);
  if(logical_role()==1) {
    printf("PAPER024501_SINK_READY\n");
  } else {
    etimer_set(&timer, INTERVAL + ((PAPER_STAGGER_SOURCE3 && logical_role()==3) ? 3*CLOCK_SECOND : 0));
    seq=1;
    while(1) {
      PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
      relevance=(unsigned short)((seq*23+logical_role()*11)%101);
      app_bits=bits_for_relevance(relevance);
      payload_bytes=app_bits/8;
      total=(payload_bytes+FRAGMENT-1)/FRAGMENT;
      printf("PAPER024501_TX source=%u seq=%u relevance=%u bits=%u frags=%u\n",
             logical_role(),seq,relevance,app_bits,total);
      bytes_left=payload_bytes;
      for(frag_index=0; frag_index<total;frag_index++) {
        unsigned short chunk=bytes_left<FRAGMENT?bytes_left:FRAGMENT;
        frame[0]=(uint8_t)(seq&255);frame[1]=(uint8_t)(seq>>8);
        frame[2]=(uint8_t)frag_index;frame[3]=(uint8_t)total;
        frame[4]=(uint8_t)(app_bits&255);frame[5]=(uint8_t)(app_bits>>8);
        frame[6]=logical_role();frame[7]=0;
        memset(frame+HEADER,(unsigned char)(seq+frag_index),chunk);
        nullnet_buf=frame;
        nullnet_len=HEADER+chunk;
#if PAPER_BROADCAST
        NETSTACK_NETWORK.output(NULL);
#else
        NETSTACK_NETWORK.output(&sink);
#endif
        bytes_left -= chunk;
      }
      seq++;
      etimer_reset(&timer);
    }
  }
  PROCESS_END();
}
