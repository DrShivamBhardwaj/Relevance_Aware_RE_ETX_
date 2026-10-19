/* Smoke configuration; run_suite.py generates an isolated per-run copy. */
#define STUDY_NODES 4
#define STUDY_ROUNDS 12
#define STUDY_SEED 1001
#define STUDY_PERIOD 10
#define STUDY_SCENARIO 0
#define STUDY_AMPLITUDE 4096
#define STUDY_MODE 0
#define STUDY_BEACONS 1
#define STUDY_FAILURES 0
static const int study_x[STUDY_NODES+2] = {0,20,0,20,40};
static const int study_y[STUDY_NODES+2] = {0,60,0,0,0};
static const unsigned char study_schedule[STUDY_ROUNDS][STUDY_NODES+2] = {{0}};
