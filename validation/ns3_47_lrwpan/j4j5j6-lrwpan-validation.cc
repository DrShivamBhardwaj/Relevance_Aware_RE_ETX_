#include "ns3/core-module.h"
#include "ns3/lr-wpan-module.h"
#include "ns3/mobility-module.h"
#include "ns3/propagation-delay-model.h"
#include "ns3/propagation-loss-model.h"
#include "ns3/single-model-spectrum-channel.h"

#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using namespace ns3;
using namespace ns3::lrwpan;

struct NodeStats
{
    bool active{false};
    bool reportOk{true};
    uint32_t frameIndex{0};
    uint32_t framesTotal{0};
    Time reportStart{Seconds(0)};
    uint64_t generatedReports{0};
    uint64_t deliveredReports{0};
    uint64_t overlapDrops{0};
    uint64_t frameConfirms{0};
    uint64_t frameSuccess{0};
    uint64_t channelAccessFailures{0};
    uint64_t noAck{0};
    uint64_t otherFailures{0};
    uint64_t sentTraceFrames{0};
    uint64_t retries{0};
    uint64_t csmaCycles{0};
    double deliveredDelayMs{0.0};
};

static std::vector<Ptr<LrWpanNetDevice>> g_devs;
static std::vector<NodeStats> g_stats;
static double g_payloadBits = 4000.0;
static const uint32_t kPayloadBitsPerFrame = 800;
static const uint32_t kSyntheticNonMacHeaderBytes = 16;
static Mac16Address g_sink("00:00");

static void SendNextFrame(uint32_t nodeIndex);

static Mac16Address
ShortAddress(uint32_t value)
{
    std::ostringstream os;
    os << std::hex << std::setfill('0') << std::setw(2) << ((value >> 8) & 0xff) << ":"
       << std::setw(2) << (value & 0xff);
    return Mac16Address(os.str().c_str());
}

static Mac64Address
ExtendedAddress(uint32_t value)
{
    std::ostringstream os;
    os << "00:00:00:00:00:00:" << std::hex << std::setfill('0') << std::setw(2)
       << ((value >> 8) & 0xff) << ":" << std::setw(2) << (value & 0xff);
    return Mac64Address(os.str().c_str());
}

static void
SentPacketTrace(uint32_t nodeIndex, Ptr<const Packet>, uint8_t attempts, uint8_t csmaCycles)
{
    auto& s = g_stats[nodeIndex];
    s.sentTraceFrames++;
    if (attempts > 0)
    {
        s.retries += (attempts - 1);
    }
    s.csmaCycles += csmaCycles;
}

static void
DataConfirm(uint32_t nodeIndex, McpsDataConfirmParams params)
{
    auto& s = g_stats[nodeIndex];
    s.frameConfirms++;
    if (params.m_status == MacStatus::SUCCESS)
    {
        s.frameSuccess++;
    }
    else
    {
        s.reportOk = false;
        if (params.m_status == MacStatus::CHANNEL_ACCESS_FAILURE)
        {
            s.channelAccessFailures++;
        }
        else if (params.m_status == MacStatus::NO_ACK)
        {
            s.noAck++;
        }
        else
        {
            s.otherFailures++;
        }
    }

    s.frameIndex++;
    if (s.frameIndex < s.framesTotal)
    {
        Simulator::Schedule(MicroSeconds(10), &SendNextFrame, nodeIndex);
        return;
    }

    s.active = false;
    if (s.reportOk)
    {
        s.deliveredReports++;
        s.deliveredDelayMs += (Simulator::Now() - s.reportStart).GetMilliSeconds();
    }
}

static void
SendNextFrame(uint32_t nodeIndex)
{
    auto& s = g_stats[nodeIndex];
    if (!s.active || s.frameIndex >= s.framesTotal)
    {
        return;
    }

    const double usedBits = static_cast<double>(s.frameIndex) * kPayloadBitsPerFrame;
    const double remainingBits = std::max(1.0, g_payloadBits - usedBits);
    const uint32_t framePayloadBits = static_cast<uint32_t>(std::ceil(std::min<double>(kPayloadBitsPerFrame, remainingBits)));
    const uint32_t payloadBytes = static_cast<uint32_t>(std::ceil(framePayloadBits / 8.0));
    const uint32_t msduBytes = payloadBytes + kSyntheticNonMacHeaderBytes;

    Ptr<Packet> packet = Create<Packet>(msduBytes);
    McpsDataRequestParams params;
    params.m_dstPanId = 0;
    params.m_srcAddrMode = SHORT_ADDR;
    params.m_dstAddrMode = SHORT_ADDR;
    params.m_dstAddr = g_sink;
    params.m_msduHandle = static_cast<uint8_t>(s.frameIndex & 0xff);
    params.m_txOptions = TX_OPTION_ACK;
    g_devs[nodeIndex]->GetMac()->McpsDataRequest(params, packet);
}

static void
StartReport(uint32_t nodeIndex)
{
    auto& s = g_stats[nodeIndex];
    s.generatedReports++;
    if (s.active)
    {
        s.overlapDrops++;
        return;
    }
    s.active = true;
    s.reportOk = true;
    s.frameIndex = 0;
    s.framesTotal = static_cast<uint32_t>(std::ceil(g_payloadBits / kPayloadBitsPerFrame));
    s.reportStart = Simulator::Now();
    SendNextFrame(nodeIndex);
}

int
main(int argc, char* argv[])
{
    std::string mode = "J4";
    uint32_t seed = 42;
    uint32_t nSensors = 100;
    double reportPeriod = 5.0;
    double simTime = 40.0;
    bool header = false;

    CommandLine cmd(__FILE__);
    cmd.AddValue("mode", "J4, J5, or J6", mode);
    cmd.AddValue("seed", "paired experiment seed", seed);
    cmd.AddValue("payloadBits", "mean report payload in bits", g_payloadBits);
    cmd.AddValue("reportPeriod", "seconds per generated report per node", reportPeriod);
    cmd.AddValue("simTime", "report-generation duration in seconds", simTime);
    cmd.AddValue("nSensors", "number of contending sensor nodes", nSensors);
    cmd.AddValue("header", "print CSV header", header);
    cmd.Parse(argc, argv);

    RngSeedManager::SetSeed(seed);
    RngSeedManager::SetRun(1);

    NodeContainer nodes;
    nodes.Create(nSensors + 1);
    g_devs.resize(nSensors);
    g_stats.resize(nSensors);

    Ptr<SingleModelSpectrumChannel> channel = CreateObject<SingleModelSpectrumChannel>();
    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetPathLossExponent(2.0);
    Ptr<ConstantSpeedPropagationDelayModel> delay = CreateObject<ConstantSpeedPropagationDelayModel>();
    channel->AddPropagationLossModel(loss);
    channel->SetPropagationDelayModel(delay);

    Ptr<LrWpanNetDevice> sinkDev = CreateObject<LrWpanNetDevice>();
    sinkDev->SetChannel(channel);
    nodes.Get(0)->AddDevice(sinkDev);
    sinkDev->GetMac()->SetPanId(0);
    sinkDev->GetMac()->SetShortAddress(g_sink);
    sinkDev->GetMac()->SetExtendedAddress(ExtendedAddress(0));

    Ptr<ConstantPositionMobilityModel> sinkMob = CreateObject<ConstantPositionMobilityModel>();
    sinkMob->SetPosition(Vector(0.0, 0.0, 0.0));
    nodes.Get(0)->AggregateObject(sinkMob);

    for (uint32_t i = 0; i < nSensors; ++i)
    {
        Ptr<LrWpanNetDevice> dev = CreateObject<LrWpanNetDevice>();
        dev->SetChannel(channel);
        nodes.Get(i + 1)->AddDevice(dev);
        dev->GetMac()->SetPanId(0);
        dev->GetMac()->SetShortAddress(ShortAddress(i + 1));
        dev->GetMac()->SetExtendedAddress(ExtendedAddress(i + 1));
        dev->GetMac()->SetMacMaxFrameRetries(3);
        dev->GetCsmaCa()->SetMacMinBE(3);
        dev->GetCsmaCa()->SetMacMaxBE(5);
        dev->GetCsmaCa()->SetMacMaxCSMABackoffs(4);
        dev->GetMac()->SetMcpsDataConfirmCallback(MakeBoundCallback(&DataConfirm, i));
        dev->GetMac()->TraceConnectWithoutContext("MacSentPkt", MakeBoundCallback(&SentPacketTrace, i));
        g_devs[i] = dev;

        const double angle = 2.0 * M_PI * static_cast<double>(i) / static_cast<double>(nSensors);
        const double radius = 3.0 + 0.5 * static_cast<double>(i % 5);
        Ptr<ConstantPositionMobilityModel> mob = CreateObject<ConstantPositionMobilityModel>();
        mob->SetPosition(Vector(radius * std::cos(angle), radius * std::sin(angle), 0.0));
        nodes.Get(i + 1)->AggregateObject(mob);
    }

    Ptr<UniformRandomVariable> phaseRv = CreateObject<UniformRandomVariable>();
    phaseRv->SetStream(9001);
    for (uint32_t i = 0; i < nSensors; ++i)
    {
        const double phase = phaseRv->GetValue(0.0, reportPeriod);
        for (double t = 1.0 + phase; t < simTime; t += reportPeriod)
        {
            Simulator::Schedule(Seconds(t), &StartReport, i);
        }
    }

    Simulator::Stop(Seconds(simTime + 5.0));
    Simulator::Run();

    uint64_t generated = 0, delivered = 0, overlaps = 0;
    uint64_t frameConfirms = 0, frameSuccess = 0, accessFail = 0, noAck = 0, otherFail = 0;
    uint64_t sentTraceFrames = 0, retries = 0, csmaCycles = 0;
    double delayMs = 0.0;
    for (const auto& s : g_stats)
    {
        generated += s.generatedReports;
        delivered += s.deliveredReports;
        overlaps += s.overlapDrops;
        frameConfirms += s.frameConfirms;
        frameSuccess += s.frameSuccess;
        accessFail += s.channelAccessFailures;
        noAck += s.noAck;
        otherFail += s.otherFailures;
        sentTraceFrames += s.sentTraceFrames;
        retries += s.retries;
        csmaCycles += s.csmaCycles;
        delayMs += s.deliveredDelayMs;
    }

    if (header)
    {
        std::cout << "mode,seed,report_period_s,payload_bits,frames_per_report,generated_reports,delivered_reports,report_rdr_pct,frame_confirms,frame_success,frame_rdr_pct,mean_delivered_report_delay_ms,mean_retries_per_frame,mean_csma_cycles_per_frame,channel_access_failures,no_ack,other_failures,overlap_drops,sim_time_s\n";
    }
    const double reportRdr = generated ? 100.0 * static_cast<double>(delivered) / generated : 0.0;
    const double frameRdr = frameConfirms ? 100.0 * static_cast<double>(frameSuccess) / frameConfirms : 0.0;
    const double meanDelay = delivered ? delayMs / delivered : 0.0;
    const double meanRetries = sentTraceFrames ? static_cast<double>(retries) / sentTraceFrames : 0.0;
    const double meanCsma = sentTraceFrames ? static_cast<double>(csmaCycles) / sentTraceFrames : 0.0;

    std::cout << mode << ',' << seed << ',' << reportPeriod << ',' << g_payloadBits << ','
              << static_cast<uint32_t>(std::ceil(g_payloadBits / kPayloadBitsPerFrame)) << ','
              << generated << ',' << delivered << ',' << reportRdr << ',' << frameConfirms << ','
              << frameSuccess << ',' << frameRdr << ',' << meanDelay << ',' << meanRetries << ','
              << meanCsma << ',' << accessFail << ',' << noAck << ',' << otherFail << ',' << overlaps
              << ',' << simTime << '\n';

    Simulator::Destroy();
    return 0;
}
