/*
 * Portable RE-ETX + payload mapping core extracted from simulator's model.
 * Direct sink cost: ETX * [1 + lambda*(1/f_i-1)/2]
 * Sensor relay cost: ETX * [1 + lambda*((1/f_i-1)+(1/f_j-1))/2]
 * f_i = clipped normalized residual energy in (0,1].
 * Payload map uses original piecewise 0.5/0.85 safeguards.
 * This header alone does not constitute a deployed multihop protocol.
 */
#ifndef PAPER024501_POLICY_CORE_H
#define PAPER024501_POLICY_CORE_H
#include <stdint.h>
#include <math.h>
static float paper_clip(float x,float lo,float hi) {
 if(x<lo)return lo;
 if(x>hi)return hi;
 return x;
}
static float paper_scarcity(float energy_fraction) {
 float f=paper_clip(energy_fraction,0.01f,1.0f);
 return 1.0f/f-1.0f;
}
static float paper_sink_cost(float etx,float frac_i,float lambda) {
 return etx*(1.0f+lambda*paper_scarcity(frac_i)*0.5f);
}
static float paper_sensor_cost(float etx,float frac_i,float frac_j,float lambda) {
 return etx*(1.0f+lambda*(paper_scarcity(frac_i)+paper_scarcity(frac_j))*0.5f);
}
static unsigned short paper_payload_bits(float relevance) {
 float v=paper_clip(relevance,0.0f,1.0f);
 float ratio=0.25f + 0.75f*v;
 if(v>=0.50f && ratio<0.75f)ratio=0.75f;
 if(v>=0.85f)ratio=1.0f;
 /* Original ceiling and byte alignment; small arithmetic epsilon prevents
    binary float issues for exact round-tenths comparison fixtures. */
 unsigned int bits=(unsigned int)ceilf(4000.0f*ratio-1e-5f);
 bits=((bits+7u)/8u)*8u;
 if(bits>4000u)bits=4000u;
 return (unsigned short)bits;
}
static float paper_relevance_from_z(float z_temporal,float z_spatial) {
 float t=paper_clip(z_temporal,0.0f,8.0f);
 float s=paper_clip(z_spatial,0.0f,8.0f);
 return paper_clip(1.0f-expf(-(0.60f*t+0.40f*s)),0.0f,1.0f);
}
#endif
