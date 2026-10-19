/* New validation component. SPDX-License-Identifier: MIT */
#include "codec.h"
#include <string.h>
#include <limits.h>

size_t study_encode(const int16_t *samples, unsigned bits, uint8_t *out) {
  size_t n, k, offset = 0, bytes;
  uint16_t q;
  if(bits < 1 || bits > 16) return 0;
  bytes = (STUDY_SAMPLES * bits + 7) / 8;
  memset(out, 0, bytes);
  for(n = 0; n < STUDY_SAMPLES; n++) {
    q = (uint16_t)((int32_t)samples[n] + 32768);
    for(k = 0; k < bits; k++, offset++) {
      out[offset / 8] |= ((q >> (15 - k)) & 1) << (7 - offset % 8);
    }
  }
  return bytes;
}
int study_decode(const uint8_t *data, size_t length, unsigned bits, int16_t *out) {
  size_t n, k, offset = 0;
  uint32_t q;
  if(bits < 1 || bits > 16 || length != (STUDY_SAMPLES * bits + 7) / 8) return 0;
  for(n = 0; n < STUDY_SAMPLES; n++) {
    q = 0;
    for(k = 0; k < bits; k++, offset++) q = (q << 1) | ((data[offset/8] >> (7-offset%8)) & 1);
    q <<= 16 - bits;
    if(bits < 16) q += 1U << (15 - bits);
    out[n] = (int16_t)((int32_t)q - 32768);
  }
  return 1;
}
uint64_t study_sse(const int16_t *a, const int16_t *b) {
  unsigned i; uint64_t result = 0;
  for(i = 0; i < STUDY_SAMPLES; i++) {
    int64_t delta = (int32_t)a[i] - b[i]; result += delta * delta;
  }
  return result;
}
uint64_t study_quantization_sse(const int16_t *samples, unsigned bits) {
  unsigned i; uint64_t sse=0;
  if(bits<1 || bits>16)return UINT64_MAX;
  for(i=0;i<STUDY_SAMPLES;i++){
    uint32_t q=(uint32_t)((int32_t)samples[i]+32768);
    int64_t delta;
    q=(q>>(16-bits))<<(16-bits);
    if(bits<16)q+=1U<<(15-bits);
    delta=(int32_t)samples[i]-((int32_t)q-32768);
    sse+=delta*delta;
  }
  return sse;
}
unsigned study_rd_choose(const int16_t *samples,double price) {
  unsigned bits,best=4;double best_cost=1e100;
  /* Conventional causal rate-distortion baseline, not a new optimality theorem.
     MSE is in signal units squared; data-byte cost is normalised by 250. */
  for(bits=4;bits<=16;bits+=4){
    double cost=(double)study_quantization_sse(samples,bits)/(STUDY_SAMPLES*4096.0*4096.0)+price*bits/8.0;
    if(cost<best_cost){best_cost=cost;best=bits;}
  }
  return best;
}
double study_rd_update(double price,unsigned bits) {
  /* Projected dual update: target 250 application bytes/report, step .01.
     This is a long-run target, not a hard per-round or network energy cap. */
  price+=0.01*(bits/8.0-1.0);
  return price<0?0:price;
}
uint32_t study_hash(uint32_t v) {
  v ^= v >> 16; v *= 0x7feb352dU; v ^= v >> 15; v *= 0x846ca68bU; return v ^ (v >> 16);
}
static int noise(unsigned seed, unsigned id, unsigned round, unsigned sample) {
  uint32_t h = study_hash(seed ^ (id * 0x9e3779b9U) ^ (round * 104729U) ^ (sample * 65537U));
  /* Sum of uniforms: bounded, approximately bell-shaped. */
  return (int)(h & 255) + (int)((h >> 8)&255) + (int)((h >> 16)&255) + (int)(h >> 24) - 510;
}
void study_signal(unsigned id, unsigned round, unsigned seed, int x, int y,
                  int amplitude, unsigned scenario, int16_t *out) {
  unsigned i; int base, event = 0, cx, cy, d2, phase;
  /* Physical workload generation is separate from controller feature scoring.
     Integers represent 1/4096 signal units. No label enters the controller. */
  phase = (int)(round % 40); if(phase > 20) phase = 40 - phase;
  base = (phase - 10) * 64 + noise(seed, 0, round, 0) * 2 + noise(seed, id, round, 0);
  cx = 20 + (int)(study_hash(seed) % 4) * 20;
  cy = 20 + (int)(study_hash(seed+1) % 4) * 20;
  d2 = (x-cx)*(x-cx) + (y-cy)*(y-cy);
  if(round >= 18 && round < (scenario == 1 ? 42U : 25U) && d2 < 1600)
    event = amplitude * (1600-d2) / 1600;
  if(scenario == 2 && round >= 30) base += ((int)round - 30) * 24;
  if(scenario == 3 && id % 11 == 0 && round >= 28) base += 4096; /* sensor bias */
  for(i=0; i<STUDY_SAMPLES; i++) {
    int value = base + event + noise(seed+97, id, round, i+1) * 2;
    if(value > INT16_MAX) value = INT16_MAX;
    if(value < INT16_MIN) value = INT16_MIN;
    out[i] = (int16_t)value;
  }
}
