/*
 * PAPER024501 Cooja/M3 limited RE-ETX prototype.
 *
 * Implements real network messages, application fragmentation/reassembly,
 * app-level beacon-derived PRR surrogate, dynamic direct/relay parent choice,
 * source-local temporal and neighbour-observation spatial features,
 * guarded relevance payload and loggable forwarding decisions.
 *
 * IMPORTANT NON-EQUIVALENCES WITH SUBMITTED MANUSCRIPT:
 *   - 3-node direct-or-one-relay graph, not 100-node sink-rooted Dijkstra
 *   - modeled node energy fraction by radio-use counter, not physical SoC
 *   - PRR from beacons, not calibrated 4000-bit message-level ETX/ACK
 *   - observations synthetic, not original correlated sensing process
 *   - simplified warm-up normalization, no full per-node EWMA state
 * This is implementation progress / transport smoke, NOT full validation.
 */
#include "contiki.h"
#include "net/netstack.h"
#include "net/nullnet/nullnet.h"
#include "net/linkaddr.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "paper024501_policy_core.h"

#ifndef PAPER_ROLE
#define PAPER_ROLE 0
#endif
#ifndef PAPER_FIXED
#define PAPER_FIXED 0
#endif
#ifndef PAPER_DIRECT_ONLY
#define PAPER_DIRECT_ONLY 0
#endif
#ifndef PAPER_PHY_BROADCAST
#define PAPER_PHY_BROADCAST 0
#endif
#ifndef PAPER_AB
#define PAPER_AB 0
#endif
#define PAPER_AB_ROUNDS 12
static uint16_t current_round;
static unsigned trialmode(void) {
 return PAPER_AB ? ((current_round / PAPER_AB_ROUNDS) % 4u) : 0u;
}
static int fixed_payload_now(void) {
 return PAPER_AB ? ((trialmode()==1u)||(trialmode()==3u)) : PAPER_FIXED;
}
static int direct_only_now(void) {
 return PAPER_AB ? ((trialmode()==2u)||(trialmode()==3u)) : PAPER_DIRECT_ONLY;
}
#define TYPE_BEACON 0x21
#define TYPE_DATA 0x22
#define HEADER 12
#define FRAG 65
#define MAX_FRAGS 8
#define INTERVAL (5*CLOCK_SECOND)
static uint8_t buf[HEADER+FRAG];
static uint8_t relay_buffer[HEADER+FRAG];
static linkaddr_t sink={{1,0,0,0,0,0,0,0}};
static linkaddr_t relay={{2,0,0,0,0,0,0,0}};
static float neighbour_sample=0.0f;
static float advertised_rank=1.0f,relay_energy=1.0f;
static float my_energy=1.0f;
static uint16_t last_sink_seq=0,last_relay_seq=0;
static uint16_t expected_sink=0,expected_relay=0;
static uint16_t count_sink=0,count_relay=0;
static unsigned int complete_reports;
static unsigned tx_total,tx_index,tx_parent,tx_bits,tx_seq,tx_bytes;
static uint16_t rx_seq[4];
static uint8_t rx_seen[4],rx_total[4];
static uint16_t rx_bits[4];
static float last_obs,mean_t,mean_s,var_t=0.01f,var_s=0.01f;
static unsigned int warm_count;
static uint8_t role(void) {
 return PAPER_ROLE?PAPER_ROLE:linkaddr_node_addr.u8[0];
}
static uint16_t read16(const uint8_t *p) {
 return (uint16_t)p[0] | ((uint16_t)p[1]<<8);
}
static void put16(uint8_t *p,uint16_t v) {
 p[0]=(uint8_t)(v&255); p[1]=(uint8_t)(v>>8);
}
static float prr(uint16_t heard,uint16_t expected) {
 if(expected==0)return 0.25f;
 return paper_clip((float)(heard+1)/(float)(expected+2),0.05f,1.0f);
}
static void consume_proxy(unsigned count) {
 float e = 0.00005f*(float)count;
 my_energy = paper_clip(my_energy-e,0.10f,1.0f);
}
static void send_frame(const uint8_t *msg,uint16_t len,const linkaddr_t *dest) {
 if(len>sizeof(buf))return;
 memcpy(buf,msg,len);
 nullnet_buf=buf;nullnet_len=len;
 NETSTACK_NETWORK.output(PAPER_PHY_BROADCAST?NULL:dest);
 consume_proxy(1);
}
static void hello_seq_update(uint16_t seq,uint16_t *last,uint16_t *expected,
                             uint16_t *heard) {
 if(*last && seq<=*last)return;
 if(*last && seq>*last) *expected += (seq-*last);
 else *expected+=1;
 *heard+=1;*last=seq;
}
static void receive(const void *data,uint16_t len,
                    const linkaddr_t *from,const linkaddr_t *dest) {
 const uint8_t *p=(const uint8_t *)data;
 unsigned int id=role(),src,hop,seq,idx,total,bits;
 (void)from;(void)dest;
 if(len<HEADER)return;
 if(p[0]==TYPE_BEACON) {
   src=p[1];
   if(src==1 && id!=1) {
      hello_seq_update(read16(p+4),&last_sink_seq,&expected_sink,&count_sink);
   }
   if(src==2 && id==3) {
      hello_seq_update(read16(p+4),&last_relay_seq,&expected_relay,&count_relay);
      /* Beacon's Q7 fixed-point advertised observation, energy and rank */
      neighbour_sample=(float)read16(p+6)/1000.0f;
      relay_energy=paper_clip((float)read16(p+8)/1000.0f,0.01f,1.0f);
      advertised_rank=(float)read16(p+10)/1000.0f;
   }
   return;
 }
 if(p[0]!=TYPE_DATA)return;
 src=p[1]; hop=p[2]; seq=read16(p+4);
 idx=p[6];total=p[7];bits=read16(p+8);
 if(src<2 || src>3 || !total || total>MAX_FRAGS || idx>=total)return;
 if(id==2 && hop==2 && src==3) {
    memcpy(relay_buffer,p,len);
    relay_buffer[2]=1;
    send_frame(relay_buffer,len,&sink);
    printf("PAPER_RELAY src=%u seq=%u frag=%u\n",src,seq,idx);
    return;
 }
 if(id!=1 || hop!=1)return;
 if(rx_seq[src]!=seq) {
    rx_seq[src]=seq;
    rx_seen[src]=0;
    rx_total[src]=total;
    rx_bits[src]=bits;
 }
 rx_seen[src] |= (uint8_t)(1u<<idx);
 if(rx_seen[src]==((1u<<total)-1u)) {
    complete_reports++;
    printf("PAPER_RX_COMPLETE src=%u seq=%u bits=%u frags=%u trialmode=%u count=%u\n",
           src,seq,bits,total,(unsigned)p[3],complete_reports);
    rx_seen[src]=0;
 }
}
static float score_relevance(float cur) {
 float tmp=fabsf(cur-last_obs);
 float spa=fabsf(cur-neighbour_sample);
 float zt,zs,r;
 last_obs=cur;
 if(warm_count<50) {
   warm_count++;
   mean_t+=tmp/50.0f;
   mean_s+=spa/50.0f;
   var_t+=tmp*tmp/50.0f;
   var_s+=spa*spa/50.0f;
   return 0.0f;
 }
 zt=tmp-mean_t; if(zt<0)zt=0;
 zs=spa-mean_s; if(zs<0)zs=0;
 zt/=sqrtf(fmaxf(var_t-mean_t*mean_t,0.0001f));
 zs/=sqrtf(fmaxf(var_s-mean_s*mean_s,0.0001f));
 r=paper_relevance_from_z(zt,zs);
 mean_t=0.98f*mean_t+0.02f*tmp;
 mean_s=0.98f*mean_s+0.02f*spa;
 return r;
}
static uint8_t select_parent(void) {
 float d,r;
 if(role()==2)return 1;
 if(direct_only_now())return 1;
 d=paper_sink_cost(1.0f/prr(count_sink,expected_sink),my_energy,1.0f);
 r=paper_sensor_cost(1.0f/prr(count_relay,expected_relay),
                     my_energy,relay_energy,1.0f)+advertised_rank;
 if(count_relay<2)return 1;
 return r<d?2:1;
}
static void send_beacon(uint16_t seq) {
 float observed=(float)(((seq*37u)+(unsigned)role()*13u)%101u)/100.0f;
 float rank = paper_sink_cost(1.0f/prr(count_sink,expected_sink),my_energy,1.0f);
 uint8_t pkt[HEADER]={TYPE_BEACON,0,0,0,0,0,0,0,0,0,0,0};
 pkt[1]=role();
 put16(pkt+4,seq);
 put16(pkt+6,(uint16_t)(observed*1000.0f));
 put16(pkt+8,(uint16_t)(my_energy*1000.0f));
 put16(pkt+10,(uint16_t)(paper_clip(rank,0,65)*1000.0f));
 send_frame(pkt,HEADER,NULL);
}
static void start_report(uint16_t seq) {
 float observed=(float)(((seq*37u)+(unsigned)role()*13u)%101u)/100.0f;
 float r=score_relevance(observed);
 tx_bits=fixed_payload_now()?4000:paper_payload_bits(r);
 tx_bytes=tx_bits/8u;
 tx_total=(tx_bytes+FRAG-1u)/FRAG;
 tx_index=0;
 tx_seq=seq;
 tx_parent=select_parent();
 printf("PAPER_PARENT source=%u seq=%u mode=%u parent=%u relevance_x100=%u payload_bits=%u etx_sink_x100=%u etx_relay_x100=%u energy_x100=%u\n",
     role(),seq,fixed_payload_now(),tx_parent,(unsigned)(r*100),tx_bits,
     (unsigned)(100.0f/prr(count_sink,expected_sink)),
     (unsigned)(100.0f/prr(count_relay,expected_relay)),
     (unsigned)(100*my_energy));
}
static void send_next_fragment(void) {
 unsigned n;
 uint8_t pkt[HEADER+FRAG]={0};
 if(tx_index>=tx_total)return;
 n=tx_bytes-tx_index*FRAG;
 if(n>FRAG)n=FRAG;
 pkt[0]=TYPE_DATA;pkt[1]=role();pkt[2]=(uint8_t)tx_parent;pkt[3]=(uint8_t)trialmode();
 put16(pkt+4,(uint16_t)tx_seq);pkt[6]=(uint8_t)tx_index;
 pkt[7]=(uint8_t)tx_total;
 put16(pkt+8,(uint16_t)tx_bits);
 memset(pkt+HEADER,(int)((tx_seq+tx_index)&255),n);
 send_frame(pkt,(uint16_t)(HEADER+n),tx_parent==2?&relay:&sink);
 tx_index++;
}
PROCESS(paper_reetx_probe,"PAPER024501 network policy probe");
AUTOSTART_PROCESSES(&paper_reetx_probe);
PROCESS_THREAD(paper_reetx_probe,ev,data) {
 static struct etimer beacon_timer;
 static struct etimer fragment_timer;
 static uint16_t seq;
 PROCESS_BEGIN();
 nullnet_set_input_callback(receive);
 seq=0;
 printf("PAPER_PROBE_START role=%u payload_fixed=%u direct_only=%u physical_broadcast=%u AB=%u\n",
        role(),PAPER_FIXED,PAPER_DIRECT_ONLY,PAPER_PHY_BROADCAST,PAPER_AB);
 etimer_set(&beacon_timer,INTERVAL);
 while(1) {
  PROCESS_WAIT_EVENT();
  if(ev!=PROCESS_EVENT_TIMER)continue;
  if(data==&beacon_timer) {
    seq++;
    current_round=seq;
    send_beacon(seq);
    if(role()>1 && seq%2==0) {
      start_report(seq);
      send_next_fragment();
      if(tx_index<tx_total)
        etimer_set(&fragment_timer,CLOCK_SECOND/8);
    }
    etimer_reset(&beacon_timer);
  } else if(data==&fragment_timer) {
    send_next_fragment();
    if(tx_index<tx_total)etimer_reset(&fragment_timer);
  }
 }
 PROCESS_END();
}
