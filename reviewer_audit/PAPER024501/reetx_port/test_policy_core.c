#include <stdio.h>
#include <math.h>
#include "paper024501_policy_core.h"
int main(void) {
 if(paper_payload_bits(0.0f)!=1000)return 1;
 if(paper_payload_bits(0.5f)!=3000)return 2;
 if(paper_payload_bits(0.6f)!=3000)return 3;
 if(paper_payload_bits(0.85f)!=4000)return 4;
 if(paper_payload_bits(1.0f)!=4000)return 5;
 if(fabsf(paper_scarcity(0.5f)-1.0f)>1e-5f)return 6;
 if(fabsf(paper_sink_cost(2,0.5f,1)-3.0f)>1e-5f)return 7;
 if(fabsf(paper_sensor_cost(2,1,0.5f,1)-3.0f)>1e-5f)return 8;
 if(!(paper_relevance_from_z(1,2)>paper_relevance_from_z(1,1)))return 9;
 puts("POLICY_CORE_9_ASSERTIONS_PASS");
 return 0;
}
