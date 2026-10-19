#ifndef STUDY_CODEC_H
#define STUDY_CODEC_H
#include <stdint.h>
#include <stddef.h>
#define STUDY_SAMPLES 250
#define STUDY_FULL_BYTES 500
size_t study_encode(const int16_t *samples, unsigned bits, uint8_t *out);
int study_decode(const uint8_t *data, size_t length, unsigned bits, int16_t *out);
uint64_t study_sse(const int16_t *a, const int16_t *b);
uint64_t study_quantization_sse(const int16_t *samples, unsigned bits);
unsigned study_rd_choose(const int16_t *samples, double price);
double study_rd_update(double price, unsigned bits);
uint32_t study_hash(uint32_t value);
void study_signal(unsigned id, unsigned round, unsigned seed, int x, int y,
                  int amplitude, unsigned scenario, int16_t *out);
#endif
