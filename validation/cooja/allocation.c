/* New validation component. SPDX-License-Identifier: MIT
 * Cooja/Contiki-NG implementation of progressive source coding and live context.
 * Native Cooja is a network simulation, not a hardware-energy measurement.
 */
#include "contiki.h"
#include "net/netstack.h"
#include "net/ipv6/simple-udp.h"
#include "net/ipv6/uip-ds6.h"
#include "net/routing/routing.h"
#include "net/linkaddr.h"
#include "net/packetbuf.h"
#include "sys/node-id.h"
#include "sys/energest.h"
#include "lib/random.h"
#include "codec.h"
#include "generated.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <inttypes.h>

#define PORT 1984
#define HEADER 16
#define START_SECONDS 60
#define WARMUP 10
#define DATA_TYPE 0xa1
#define BEACON_TYPE 0xb1
static struct simple_udp_connection connection;
static int16_t block[STUDY_SAMPLES], decoded[STUDY_SAMPLES], truth[STUDY_SAMPLES];
static uint8_t packet[HEADER+STUDY_FULL_BYTES], beacon[12];
static int16_t neighbour_mean[STUDY_NODES+2];
static uint16_t neighbour_round[STUDY_NODES+2], neighbour_energy[STUDY_NODES+2];
static uint8_t neighbour_seen[STUDY_NODES+2];
static linkaddr_t neighbour_address[STUDY_NODES+2];
static unsigned round_index;
static int previous_mean;
static double feature_mean[2], feature_var[2] = {65536,65536};
static double z_temporal, z_spatial, relevance;
static unsigned context_count;
static double rd_price=0.001;

PROCESS(allocation_process, "Progressive allocation validation");
AUTOSTART_PROCESSES(&allocation_process);
static void put16(uint8_t *p, uint16_t v) { p[0]=v>>8; p[1]=v; }
static uint16_t get16(const uint8_t *p) {return ((uint16_t)p[0]<<8)|p[1];}
static void put32(uint8_t *p,uint32_t v){p[0]=v>>24;p[1]=v>>16;p[2]=v>>8;p[3]=v;}
static uint32_t get32(const uint8_t *p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static uint32_t checksum(const uint8_t *p,unsigned n){unsigned i;uint32_t h=2166136261U;for(i=0;i<n;i++)h=(h^p[i])*16777619U;return h;}
static uint16_t remaining_radio_proxy(void) {
  double used;
  energest_flush();
  /* CC2420 nominal 3 V, TX 17.4 mA and RX 18.8 mA.
     120 J virtual radio reserve; sensing and CPU are NOT included. */
  used = 3.0 * (0.0174 * energest_type_time(ENERGEST_TYPE_TRANSMIT)
                 + 0.0188 * energest_type_time(ENERGEST_TYPE_LISTEN)) / ENERGEST_SECOND;
  if(used >= 119.88) return 1;
  return (uint16_t)(1000.0 * (120.0-used)/120.0);
}
uint16_t study_parent_penalty(const linkaddr_t *address, uint16_t etx) {
  unsigned i;uint16_t own, other=1000;double extra;
  if(address == NULL) return 0;
  for(i=1;i<=STUDY_NODES+1;i++) {
    if(neighbour_seen[i] && linkaddr_cmp(address,&neighbour_address[i]) &&
       neighbour_round[i]+1 >= round_index) {other=neighbour_energy[i];break;}
  }
  if(other<1)other=1;
  own=remaining_radio_proxy();
  extra=etx*0.125*(1000.0/own+1000.0/other-2.0);
  if(extra>8192)extra=8192;
  return (uint16_t)extra;
}
static void report_activity(void) {
  energest_flush();
  printf("ACT,%u,%u,%"PRIu64",%"PRIu64",%"PRIu64",%"PRIu64",%lu,%u\n",node_id,round_index,
     (uint64_t)energest_type_time(ENERGEST_TYPE_CPU),(uint64_t)energest_type_time(ENERGEST_TYPE_LPM),
     (uint64_t)energest_type_time(ENERGEST_TYPE_TRANSMIT),(uint64_t)energest_type_time(ENERGEST_TYPE_LISTEN),
     (unsigned long)ENERGEST_SECOND,remaining_radio_proxy());
}
static void receive(struct simple_udp_connection *c,const uip_ipaddr_t *sender,
 uint16_t sender_port,const uip_ipaddr_t *receiver,uint16_t receiver_port,const uint8_t *data,uint16_t len) {
  unsigned id,r,bits,hops;uint32_t sent;uint64_t sse;
  (void)c;(void)sender;(void)sender_port;(void)receiver;(void)receiver_port;
  if(len==12 && data[0]==BEACON_TYPE) {
    id=get16(data+2);if(id<1 || id>STUDY_NODES+1 || id==node_id)return;
    neighbour_seen[id]=1;neighbour_round[id]=get16(data+4);
    neighbour_mean[id]=(int16_t)get16(data+6);neighbour_energy[id]=get16(data+8);
    linkaddr_copy(&neighbour_address[id],packetbuf_addr(PACKETBUF_ADDR_SENDER));
    return;
  }
  if(node_id!=1 || len<HEADER || data[0]!=DATA_TYPE || data[1]!=1)return;
  bits=data[2];id=get16(data+4);r=get16(data+6);sent=get32(data+8);
  if(id<2||id>STUDY_NODES+1||r>=STUDY_ROUNDS||checksum(data+HEADER,len-HEADER)!=get32(data+12)){
    printf("BAD,%u\n",len);return;}
  if(!study_decode(data+HEADER,len-HEADER,bits,decoded)){printf("BAD_CODEC,%u\n",len);return;}
  /* Evaluation-only observer; no feedback is supplied to source control. */
  study_signal(id,r,STUDY_SEED,study_x[id],study_y[id],STUDY_AMPLITUDE,STUDY_SCENARIO,truth);
  sse=study_sse(truth,decoded);
  hops=data[3]>=UIP_IP_BUF->ttl ? data[3]-UIP_IP_BUF->ttl+1 : 0;
  printf("RX,%u,%u,%u,%u,%"PRIu64",%lu,%u\n",id,r,bits,len,sse,(unsigned long)(clock_time()-sent),hops);
}
static int score(int mean) {
  int values[STUDY_NODES+2],n=0,i,j,key,median;double f[2],z[2],delta,clipped,sd;
  for(i=1;i<=STUDY_NODES+1;i++)if(neighbour_seen[i] && neighbour_round[i]+1>=round_index && i!=1)values[n++]=neighbour_mean[i];
  for(i=1;i<n;i++){key=values[i];j=i;while(j>0&&values[j-1]>key){values[j]=values[j-1];j--;}values[j]=key;}
  median=n?values[n/2]:mean;context_count=n;
  f[0]=abs(mean-previous_mean);f[1]=abs(mean-median);previous_mean=mean;
  for(i=0;i<2;i++){
    sd=sqrt(feature_var[i]);z[i]=(f[i]-feature_mean[i])/(sd+1e-9);
    if(z[i]<0)z[i]=0;
    if(z[i]>8)z[i]=8;
    clipped=f[i];if(clipped>feature_mean[i]+3*sd)clipped=feature_mean[i]+3*sd;
    delta=clipped-feature_mean[i];feature_mean[i]+=0.02*delta;
    feature_var[i]=0.98*feature_var[i]+0.02*delta*delta;
    if(feature_var[i]<65536)feature_var[i]=65536;
  }
  z_temporal=z[0];z_spatial=z[1];
  relevance=1-exp(-(STUDY_BEACONS?0.6*z[0]+0.4*z[1]:z[0]));
  if(round_index<WARMUP)return 16;
  if(relevance>=0.85)return 16;
  if(relevance>=0.5)return 12;
  if(relevance>=0.20)return 8;
  return 4;
}
PROCESS_THREAD(allocation_process,ev,data) {
  static struct etimer timer;
  static unsigned bits,n,i;
  static int mean;
  static int failed_node;
  static int32_t sum;
  static uint64_t zero_sse;
  static uip_ipaddr_t dest, multicast;
  PROCESS_BEGIN();
  simple_udp_register(&connection,PORT,NULL,PORT,receive);
  uip_create_linklocal_allnodes_mcast(&multicast);
  if(node_id==1){NETSTACK_ROUTING.root_start();printf("META,%u,%u,%u,%lu\n",STUDY_SEED,STUDY_NODES,STUDY_PERIOD,(unsigned long)CLOCK_SECOND);}
  etimer_set(&timer,START_SECONDS*CLOCK_SECOND + (node_id%7)*CLOCK_SECOND/10);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
  for(round_index=0;round_index<STUDY_ROUNDS;round_index++){
    if(node_id==1){report_activity();etimer_set(&timer,STUDY_PERIOD*CLOCK_SECOND);PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));continue;}
    study_signal(node_id,round_index,STUDY_SEED,study_x[node_id],study_y[node_id],STUDY_AMPLITUDE,STUDY_SCENARIO,block);
    sum=0;zero_sse=0;for(i=0;i<STUDY_SAMPLES;i++){sum+=block[i];zero_sse+=(int64_t)block[i]*block[i];}
    mean=sum/STUDY_SAMPLES;
    failed_node = STUDY_FAILURES && node_id%13==0 && round_index>=35;
    if(failed_node) NETSTACK_MAC.off();
    if(STUDY_BEACONS && !failed_node){memset(beacon,0,sizeof(beacon));beacon[0]=BEACON_TYPE;put16(beacon+2,node_id);put16(beacon+4,round_index);put16(beacon+6,(uint16_t)mean);put16(beacon+8,remaining_radio_proxy());simple_udp_sendto(&connection,beacon,sizeof(beacon),&multicast);}
    etimer_set(&timer,2*CLOCK_SECOND+(node_id%5)*CLOCK_SECOND/20);
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
    bits=score(mean);
    if(STUDY_MODE==1)bits=16;
    if(STUDY_MODE>=2 && STUDY_MODE<=4)bits=study_schedule[round_index][node_id];
    if(STUDY_MODE==5 && round_index>=WARMUP){bits=study_rd_choose(block,rd_price);rd_price=study_rd_update(rd_price,bits);}
    n=study_encode(block,bits,packet+HEADER);
    memset(packet,0,HEADER);packet[0]=DATA_TYPE;packet[1]=1;packet[2]=bits;packet[3]=uip_ds6_if.cur_hop_limit;
    put16(packet+4,node_id);put16(packet+6,round_index);put32(packet+8,clock_time());put32(packet+12,checksum(packet+HEADER,n));
    printf("TX,%u,%u,%u,%u,%d,%lu,%lu,%u,%"PRIu64"\n",node_id,round_index,bits,n+HEADER,mean,(unsigned long)(1000*z_temporal),(unsigned long)(1000*z_spatial),context_count,zero_sse);
    if(!failed_node && NETSTACK_ROUTING.node_is_reachable()&&NETSTACK_ROUTING.get_root_ipaddr(&dest))simple_udp_sendto(&connection,packet,n+HEADER,&dest);
    else printf("NO_ROUTE,%u,%u\n",node_id,round_index);
    report_activity();
    etimer_set(&timer,(STUDY_PERIOD-2)*CLOCK_SECOND-(node_id%5)*CLOCK_SECOND/20);
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
  }
  printf("DONE,%u\n",node_id);report_activity();
  PROCESS_END();
}
