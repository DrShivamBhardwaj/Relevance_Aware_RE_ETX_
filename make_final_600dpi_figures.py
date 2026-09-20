import csv, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
from matplotlib.lines import Line2D
from PIL import Image

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"figures"/"final_600dpi"
OUT.mkdir(parents=True,exist_ok=True)

plt.rcParams.update({
    "font.family":"serif",
    "font.serif":["Times New Roman","Times","DejaVu Serif"],
    "font.size":10,
    "axes.titlesize":12,
    "axes.labelsize":11,
    "xtick.labelsize":9,
    "ytick.labelsize":9,
    "legend.fontsize":9,
    "figure.facecolor":"white",
    "axes.facecolor":"white",
    "savefig.facecolor":"white",
})

METHODS=["Random","Resource-only","Utility-only","Proposed"]
COLORS={"Random":"#6f7378","Resource-only":"#0645ff","Utility-only":"#ff5a00","Proposed":"#0b8b1a"}
MARKERS={"Random":"o","Resource-only":"s","Utility-only":"D","Proposed":"^"}

def read_csv(path):
    with open(path,newline="") as f:
        return list(csv.DictReader(f))

def save(fig,name):
    for ax in fig.axes:
        for sp in ax.spines.values():
            sp.set_linewidth(0.9); sp.set_color("black")
    fig.add_artist(Rectangle((0.003,0.003),0.994,0.994,transform=fig.transFigure,
                             fill=False,edgecolor="black",linewidth=1.2))
    fig.savefig(OUT/name,dpi=600,bbox_inches="tight",pad_inches=0.05)
    plt.close(fig)

def grid(ax):
    ax.grid(axis="y",linestyle="--",alpha=.30,linewidth=.7)
    ax.set_axisbelow(True)

def add_table(ax, rows, cols, bbox, fontsize=8):
    tbl=ax.table(cellText=rows,colLabels=cols,cellLoc="center",loc="bottom",bbox=bbox)
    tbl.auto_set_font_size(False); tbl.set_fontsize(fontsize)
    for c in range(len(cols)):
        cell=tbl[0,c]; cell.set_facecolor("#062d73")
        cell.get_text().set_color("white"); cell.get_text().set_weight("bold")
    for r in range(1,len(rows)+1):
        for c in range(len(cols)):
            tbl[r,c].set_edgecolor("#555"); tbl[r,c].set_linewidth(.5)
        m=rows[r-1][0]
        if m in COLORS:
            tbl[r,0].get_text().set_color(COLORS[m]); tbl[r,0].get_text().set_weight("bold")
    return tbl

def key_method(m):
    return m.lower().replace("-only","")

def at(data,method,corr=.9):
    return next(r for r in data if r["method"]==key_method(method) and abs(float(r["correlation"])-corr)<1e-9)

# 01: simple architecture
fig,ax=plt.subplots(figsize=(11.5,7.2)); ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis("off")
bands=[(7.65,2.0,"Cloud Layer","#dcecff"),(5.25,2.0,"Edge Layer","#e2f2df"),
       (2.85,2.0,"Relay Layer","#fff0d8"),(0.45,2.0,"Sensor / Client Layer","#eee6ff")]
for y,h,label,fc in bands:
    ax.add_patch(Rectangle((.2,y),9.6,h,facecolor=fc,edgecolor="#777",linewidth=.8))
    ax.add_patch(Rectangle((.2,y),1.75,h,facecolor=fc,edgecolor="#777",linewidth=.8))
    ax.text(1.075,y+h/2,label,ha="center",va="center",fontsize=14,fontweight="bold")
ax.add_patch(Rectangle((4.45,8.15),1.4,.75,facecolor="#f7f7f7",edgecolor="#0b4f9e",linewidth=1.2))
ax.text(5.15,8.52,"Cloud Server",ha="center",va="center",fontweight="bold",fontsize=12)
edge_x=[3.0,4.4,5.8,7.2]
for i,x in enumerate(edge_x,1):
    ax.add_patch(Rectangle((x-.35,5.85),.7,.55,facecolor="#e9eef4",edgecolor="#0b4f9e",linewidth=1.0))
    ax.text(x,5.62,f"E{i}",ha="center",fontsize=10,fontweight="bold")
    ax.add_patch(Rectangle((x-.28,3.45),.56,.45,facecolor="#f7f7f7",edgecolor="#b35b00",linewidth=1.0))
    ax.text(x,3.22,f"R{i}",ha="center",fontsize=10,fontweight="bold")
client_x=[2.45,3.25,4.05,4.85,5.65,6.45,7.25,8.05]
for j,x in enumerate(client_x,1):
    ax.add_patch(Circle((x,1.25),.16,facecolor="#77aaff",edgecolor="#003d99",linewidth=.9))
    ax.text(x,0.88,f"C{j}",ha="center",fontsize=8)
for x in edge_x:
    ax.plot([x,5.15],[6.4,8.15],color="#222",linewidth=.9)
    ax.plot([x,x],[3.9,5.85],color="#555",linewidth=.9,linestyle="--")
for x in client_x:
    nearest=min(edge_x,key=lambda e:abs(e-x))
    ax.plot([x,nearest],[1.41,3.45],color="#777",linewidth=.7,linestyle="--")
ax.add_patch(FancyArrowPatch((5.45,7.95),(5.45,6.65),arrowstyle="-|>",mutation_scale=13,color="red",linewidth=1.1))
ax.add_patch(FancyArrowPatch((4.85,6.65),(4.85,7.95),arrowstyle="-|>",mutation_scale=13,color="#0645ff",linewidth=1.1))
ax.text(5.7,7.35,"updates",color="red",fontsize=9); ax.text(4.1,7.35,"model",color="#0645ff",fontsize=9)
save(fig,"01_system_architecture.png")

# 02: abstract deployment topology
fig,ax=plt.subplots(figsize=(11.5,7.2)); ax.set_xlim(0,12); ax.set_ylim(0,8); ax.axis("off")
zones=[(.5,4.35,5.2,2.8,"Sensing Zone A"),(6.3,4.35,5.2,2.8,"Sensing Zone B"),
       (.5,.65,5.2,2.8,"Sensing Zone C"),(6.3,.65,5.2,2.8,"Sensing Zone D")]
sensor_sets=[[(1.2,6.4),(2.0,6.8),(3.0,6.1),(4.3,6.6),(5.0,5.5),(2.2,5.25),(3.6,5.0)],
             [(7.1,6.5),(8.0,6.9),(9.2,6.2),(10.5,6.7),(11.0,5.4),(8.1,5.3),(9.7,5.0)],
             [(1.2,2.7),(2.2,3.0),(3.2,2.4),(4.6,2.9),(5.0,1.6),(2.1,1.5),(3.7,1.3)],
             [(7.0,2.7),(8.2,3.0),(9.4,2.4),(10.6,2.9),(11.0,1.6),(8.0,1.5),(9.7,1.3)]]
gateways=[(3.0,5.75),(9.0,5.75),(3.0,2.0),(9.0,2.0)]
for zi,(x,y,w,h,label) in enumerate(zones):
    ax.add_patch(Rectangle((x,y),w,h,facecolor="#fbfbfb",edgecolor="#888",linewidth=1.0))
    ax.text(x+w/2,y+h-.28,label,ha="center",va="center",fontweight="bold",fontsize=13)
    pts=sensor_sets[zi]; gx,gy=gateways[zi]
    for px,py in pts:
        ax.add_patch(Circle((px,py),.11,facecolor="#77aaff",edgecolor="#003d99",linewidth=.9))
    ax.add_patch(Rectangle((gx-.13,gy-.13),.26,.26,facecolor="red",edgecolor="#7f0000",linewidth=.9))
    ax.text(gx,gy-.34,f"G{zi+1}",ha="center",color="red",fontweight="bold",fontsize=9)
    for px,py in pts:
        if math.hypot(px-gx,py-gy)<1.65:
            ax.plot([px,gx],[py,gy],color="#777",linestyle="--",linewidth=.7)
    for a,b in zip(pts[:-1],pts[1:]):
        if math.hypot(a[0]-b[0],a[1]-b[1])<1.6:
            ax.plot([a[0],b[0]],[a[1],b[1]],color="#999",linestyle="--",linewidth=.55)
for a,b in [((3,5.75),(9,5.75)),((3,2),(9,2)),((3,5.75),(3,2)),((9,5.75),(9,2))]:
    ax.plot([a[0],b[0]],[a[1],b[1]],color="#333",linestyle="-.",linewidth=1.0)
legend=[Line2D([0],[0],marker='o',color='w',markerfacecolor="#77aaff",markeredgecolor="#003d99",label="Sensor mote",markersize=7),
        Line2D([0],[0],marker='s',color='w',markerfacecolor="red",markeredgecolor="#7f0000",label="Gateway mote",markersize=7),
        Line2D([0],[0],color="#777",linestyle="--",label="Connectivity")]
ax.legend(handles=legend,loc="upper center",ncol=3,frameon=True,edgecolor="black")
save(fig,"02_network_topology.png")

intel=read_csv(ROOT/"results/intel_lab/aggregate_summary.csv")
har=read_csv(ROOT/"results/uci_har/aggregate_summary.csv")
syn=read_csv(ROOT/"results/final_synthetic_10seed/aggregate_summary.csv")

# 03 Intel
fig=plt.figure(figsize=(12.3,8.0)); ax=fig.add_axes([.08,.34,.89,.56])
raw={}
for m in METHODS:
    r=at(intel,m); raw[m]=[float(r["rmse_c_mean"]),float(r["effective_bits_mean"])/1e6,float(r["energy_j_mean"]),
                            float(r["max_relay_energy_j_mean"]),float(r["representation_js_mean"])]
arr=np.array(list(raw.values())); norm=100*arr/arr.max(axis=0); x=np.arange(5)
for i,m in enumerate(METHODS):
    ax.plot(x,norm[i],marker=MARKERS[m],markersize=7,linewidth=1.5,color=COLORS[m],label=m)
    for j,v in enumerate(raw[m]):
        ax.annotate(f"{v:.4f}" if j in (0,3,4) else f"{v:.3f}",(x[j],norm[i,j]),textcoords="offset points",
                    xytext=(0,7 if i%2==0 else -14),ha="center",fontsize=8,color=COLORS[m],fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(["RMSE (°C)","Effective Traffic\n(Mbit)","Energy (J)","Max Relay Energy (J)","Representation JS"],fontweight="bold")
ax.set_ylabel("Normalized value (% of metric maximum)",fontweight="bold"); ax.set_ylim(0,118); grid(ax)
ax.set_title("Intel Berkeley Lab Results at c = 0.9",fontweight="bold",fontsize=15,pad=15)
ax.legend(loc="upper center",bbox_to_anchor=(.5,1.08),ncol=4,frameon=True,edgecolor="black")
rows=[[m,f"{raw[m][0]:.4f}",f"{raw[m][1]:.3f}",f"{raw[m][2]:.3f}",f"{raw[m][3]:.4f}",f"{raw[m][4]:.4f}"] for m in METHODS]
add_table(ax,rows,["Method","RMSE (°C)","Effective Traffic (Mbit)","Energy (J)","Max Relay Energy (J)","Representation JS"],[0,-.52,1,.40],8)
save(fig,"03_intel_results.png")

# 04 HAR
fig=plt.figure(figsize=(12.5,8.1)); ax=fig.add_axes([.075,.34,.895,.56]); raw={}
for m in METHODS:
    r=at(har,m); raw[m]=[float(r["accuracy_mean"]),float(r["macro_f1_mean"]),float(r["worst_client_accuracy_mean"]),
                          float(r["effective_bits_mean"])/1e6,float(r["energy_j_mean"]),float(r["max_relay_energy_j_mean"]),float(r["representation_js_mean"])]
arr=np.array(list(raw.values())); norm=100*arr/arr.max(axis=0); x=np.arange(7)
for i,m in enumerate(METHODS):
    ax.plot(x,norm[i],marker=MARKERS[m],markersize=7,linewidth=1.45,color=COLORS[m],label=m)
    for j,v in enumerate(raw[m]):
        txt=f"{v:.4f}" if j in (0,1,2,6) else f"{v:.3f}" if j in (3,5) else f"{v:.2f}"
        ax.annotate(txt,(x[j],norm[i,j]),textcoords="offset points",xytext=(0,7 if i%2==0 else -14),ha="center",fontsize=7.5,color=COLORS[m],fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(["Accuracy","Macro-F1","Worst-client\nAccuracy","Effective\nTraffic (Mbit)","Energy (J)","Max Relay\nEnergy (J)","Representation\nJS"],fontweight="bold")
ax.set_ylabel("Normalized value (% of metric maximum)",fontweight="bold"); ax.set_ylim(0,118); grid(ax)
ax.set_title("UCI HAR Results at c = 0.9",fontweight="bold",fontsize=15,pad=15)
ax.legend(loc="upper center",bbox_to_anchor=(.5,1.08),ncol=4,frameon=True,edgecolor="black")
rows=[[m,f"{raw[m][0]:.4f}",f"{raw[m][1]:.4f}",f"{raw[m][2]:.4f}",f"{raw[m][3]:.3f}",f"{raw[m][4]:.2f}",f"{raw[m][5]:.3f}",f"{raw[m][6]:.4f}"] for m in METHODS]
add_table(ax,rows,["Method","Accuracy","Macro-F1","Worst-client Acc.","Traffic (Mbit)","Energy (J)","Max Relay (J)","Rep. JS"],[0,-.52,1,.40],7.5)
save(fig,"04_har_results.png")

# 05 tradeoff
fig,axes=plt.subplots(1,2,figsize=(11.8,6.1))
for ax,title,data,ykey,ylabel in [(axes[0],"Intel Berkeley Lab",intel,"rmse_c_mean","RMSE (°C)"),(axes[1],"UCI HAR",har,"accuracy_mean","Accuracy")]:
    for m in METHODS:
        r=at(data,m); xx=float(r["effective_bits_mean"])/1e6; yy=float(r[ykey]); ss=float(r["max_relay_energy_j_mean"])
        ax.scatter(xx,yy,s=min(1400,220+260*ss),color=COLORS[m],marker=MARKERS[m],alpha=.78,edgecolor="black",linewidth=.6)
        ax.annotate(m,(xx,yy),xytext=(6,6),textcoords="offset points",fontsize=9,fontweight="bold")
    ax.set_xlabel("Effective Traffic (Mbit)",fontweight="bold"); ax.set_ylabel(ylabel,fontweight="bold"); grid(ax); ax.set_title(title,fontweight="bold",fontsize=13)
handles=[Line2D([0],[0],marker=MARKERS[m],color="w",markerfacecolor=COLORS[m],markeredgecolor="black",label=m,markersize=8) for m in METHODS]
fig.legend(handles=handles,loc="lower center",ncol=4,frameon=True,edgecolor="black",bbox_to_anchor=(.5,.015)); fig.subplots_adjust(bottom=.18,wspace=.25)
save(fig,"05_learning_communication_tradeoff.png")

# 06 ablation
ia=read_csv(ROOT/"results/intel_lab/ablation_summary.csv"); ha=read_csv(ROOT/"results/uci_har/ablation_summary.csv")
labels=["Proposed","No rep.","Fixed comp.","Age only","No relay"]; variants=["proposed","proposed_no_rep","proposed_fixed_comp","proposed_age_only","proposed_no_relay"]
vcols=["#ff6b00","#1a8f1a","#7a00cc","#0645ff","#e51b1b"]; vmarks=["o","s","D","^","*"]
fig=plt.figure(figsize=(12.4,9.2)); gs=fig.add_gridspec(2,3,left=.07,right=.98,top=.93,bottom=.14,hspace=.46,wspace=.28)
specs=[("Intel RMSE (°C)",ia,"rmse_c_mean"),("Intel Traffic (Mbit)",ia,"effective_bits_mean"),("Intel Max Relay Energy (J)",ia,"max_relay_energy_j_mean"),
       ("HAR Accuracy",ha,"accuracy_mean"),("HAR Traffic (Mbit)",ha,"effective_bits_mean"),("HAR Max Relay Energy (J)",ha,"max_relay_energy_j_mean")]
for k,(title,data,key) in enumerate(specs):
    ax=fig.add_subplot(gs[k//3,k%3]); vals=[]
    for v in variants:
        r=next(x for x in data if x["variant"]==v); val=float(r[key]); val=val/1e6 if "effective_bits" in key else val; vals.append(val)
    ax.plot(range(5),vals,color="#333",linewidth=1.0)
    for i,val in enumerate(vals):
        ax.plot(i,val,marker=vmarks[i],markersize=7,color=vcols[i])
        ax.annotate(f"{val:.4f}" if val<2 else f"{val:.3f}",(i,val),xytext=(0,7),textcoords="offset points",ha="center",fontsize=7.5,color=vcols[i],fontweight="bold")
    ax.set_xticks(range(5)); ax.set_xticklabels(labels,rotation=25,ha="right",fontsize=8); ax.set_title(title,fontweight="bold"); grid(ax)
fig.legend(handles=[Line2D([0],[0],marker=vmarks[i],color=vcols[i],label=labels[i],markersize=7) for i in range(5)],loc="upper center",ncol=5,frameon=True,edgecolor="black")
save(fig,"06_ablation.png")

# 07 ns3
ns=read_csv(ROOT/"validation/ns3_47_hfl/results/ns3_group_summary.csv"); conds=["dense_nominal","scale_nominal"]; condlabels=["Dense nominal","24-sensor nominal"]
fig=plt.figure(figsize=(12.2,8.2)); gs=fig.add_gridspec(1,3,left=.07,right=.98,top=.88,bottom=.30,wspace=.28)
metrics=[("report_rdr_pct_mean","Report RDR (%)"),("mean_delivered_report_delay_ms_mean","Delay (ms)"),("channel_access_failures_mean","Channel-access failures")]
for j,(key,title) in enumerate(metrics):
    ax=fig.add_subplot(gs[0,j]); x=np.arange(2)
    for m in METHODS:
        vals=[]
        for c in conds:
            r=next(z for z in ns if z["mapping"]=="hop" and z["condition"]==c and z["method"]==key_method(m))
            vals.append(float(r[key]))
        ax.plot(x,vals,marker=MARKERS[m],color=COLORS[m],linewidth=1.35,markersize=7,label=m)
        for xi,v in zip(x,vals):
            ax.annotate(f"{v:.2f}" if key!="channel_access_failures_mean" else f"{v:.1f}",(xi,v),xytext=(0,7),textcoords="offset points",ha="center",fontsize=7.5,color=COLORS[m],fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(condlabels,fontsize=8); ax.set_title(title,fontweight="bold"); grid(ax)
fig.legend(handles=[Line2D([0],[0],marker=MARKERS[m],color=COLORS[m],label=m) for m in METHODS],loc="upper center",ncol=4,frameon=True,edgecolor="black")
table_rows=[]
for m in METHODS:
    vals=[]
    for c in conds:
        r=next(z for z in ns if z["mapping"]=="hop" and z["condition"]==c and z["method"]==key_method(m))
        vals += [f"{float(r['report_rdr_pct_mean']):.2f}",f"{float(r['mean_delivered_report_delay_ms_mean']):.2f}",f"{float(r['channel_access_failures_mean']):.1f}"]
    table_rows.append([m]+vals)
add_table(fig.axes[0],table_rows,["Method","RDR Dense","Delay Dense","Fail Dense","RDR 24-sensor","Delay 24-sensor","Fail 24-sensor"],[-.02,-.44,3.15,.34],7.2)
save(fig,"07_ns3_validation.png")

# 08 sensitivity
ig=read_csv(ROOT/"results/intel_lab/joint_grid.csv"); hg=read_csv(ROOT/"results/uci_har/joint_grid.csv")
fig,axes=plt.subplots(2,2,figsize=(11.5,7.8))
for row,(data,title,learn_key) in enumerate([(ig,"Intel Berkeley Lab","rmse_c_mean"),(hg,"UCI HAR","accuracy_mean")]):
    for beta in sorted({float(r["compression_distortion_weight"]) for r in data}):
        subset=sorted([r for r in data if float(r["compression_distortion_weight"])==beta],key=lambda r:float(r["relay_pressure_weight"]))
        xs=[float(r["relay_pressure_weight"]) for r in subset]
        axes[row,0].plot(xs,[float(r[learn_key]) for r in subset],marker="o",label=f"β={beta:g}")
        axes[row,1].plot(xs,[float(r["effective_bits_mean"])/1e6 for r in subset],marker="o",label=f"β={beta:g}")
    axes[row,0].set_title(f"{title}: {'RMSE' if row==0 else 'Accuracy'}",fontweight="bold"); axes[row,1].set_title(f"{title}: Effective Traffic",fontweight="bold")
    axes[row,0].set_xlabel("Relay-pressure weight"); axes[row,1].set_xlabel("Relay-pressure weight")
    axes[row,0].set_ylabel("RMSE (°C)" if row==0 else "Accuracy"); axes[row,1].set_ylabel("Mbit")
    grid(axes[row,0]); grid(axes[row,1]); axes[row,1].legend(frameon=True,edgecolor="black",fontsize=7)
save(fig,"08_sensitivity.png")

# 09 representation evolution
fig,axes=plt.subplots(1,2,figsize=(11.5,4.8))
for ax,p,title in [(axes[0],ROOT/"results/intel_lab/round_history.csv","Intel Berkeley Lab"),(axes[1],ROOT/"results/uci_har/round_history.csv","UCI HAR")]:
    data=read_csv(p)
    for m in METHODS:
        by={}
        for r in data:
            if r["method"]==key_method(m) and abs(float(r["correlation"])-.9)<1e-9:
                by.setdefault(int(r["round"]),[]).append(float(r["representation_js"]))
        xs=sorted(by); ys=[np.mean(by[x]) for x in xs]
        ax.plot(xs,ys,color=COLORS[m],marker=MARKERS[m],markevery=max(1,len(xs)//7),linewidth=1.4,label=m)
    ax.set_xlabel("Round",fontweight="bold"); ax.set_ylabel("Representation JS",fontweight="bold"); ax.set_title(title,fontweight="bold"); grid(ax)
axes[0].legend(frameon=True,edgecolor="black",fontsize=8)
save(fig,"09_representation_evolution.png")

# 10 participation evolution
fig,axes=plt.subplots(1,2,figsize=(11.5,4.8))
for ax,p,title in [(axes[0],ROOT/"results/intel_lab/round_history.csv","Intel Berkeley Lab"),(axes[1],ROOT/"results/uci_har/round_history.csv","UCI HAR")]:
    data=read_csv(p)
    for m in METHODS:
        by={}
        for r in data:
            if r["method"]==key_method(m) and abs(float(r["correlation"])-.9)<1e-9:
                by.setdefault(int(r["round"]),[]).append(float(r["participation_jain"]))
        xs=sorted(by); ys=[np.mean(by[x]) for x in xs]
        ax.plot(xs,ys,color=COLORS[m],marker=MARKERS[m],markevery=max(1,len(xs)//7),linewidth=1.4,label=m)
    ax.set_xlabel("Round",fontweight="bold"); ax.set_ylabel("Jain participation index",fontweight="bold"); ax.set_ylim(0,1.02); ax.set_title(title,fontweight="bold"); grid(ax)
axes[0].legend(frameon=True,edgecolor="black",fontsize=8)
save(fig,"10_participation_evolution.png")

# 11 synthetic
fig=plt.figure(figsize=(11.8,7.7)); ax=fig.add_axes([.08,.34,.89,.56]); raw={}
for m in METHODS:
    r=at(syn,m); raw[m]=[float(r["accuracy_mean"]),float(r["effective_bits_mean"])/1e6,float(r["energy_j_mean"]),float(r["max_relay_energy_j_mean"]),float(r["representation_js_mean"])]
arr=np.array(list(raw.values())); norm=100*arr/arr.max(axis=0); x=np.arange(5)
for i,m in enumerate(METHODS):
    ax.plot(x,norm[i],marker=MARKERS[m],markersize=7,linewidth=1.4,color=COLORS[m],label=m)
    for j,v in enumerate(raw[m]):
        ax.annotate(f"{v:.4f}" if j in (0,4) else f"{v:.3f}",(x[j],norm[i,j]),xytext=(0,7 if i%2==0 else -14),textcoords="offset points",ha="center",fontsize=7.5,color=COLORS[m],fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(["Accuracy","Effective Traffic\n(Mbit)","Energy (J)","Max Relay Energy (J)","Representation JS"],fontweight="bold")
ax.set_ylabel("Normalized value (% of metric maximum)",fontweight="bold"); ax.set_ylim(0,118); grid(ax)
ax.set_title("Synthetic Correlated-Heterogeneity Stress Test at c = 0.9",fontweight="bold",fontsize=14,pad=15)
ax.legend(loc="upper center",bbox_to_anchor=(.5,1.08),ncol=4,frameon=True,edgecolor="black")
rows=[[m,f"{raw[m][0]:.4f}",f"{raw[m][1]:.3f}",f"{raw[m][2]:.3f}",f"{raw[m][3]:.4f}",f"{raw[m][4]:.4f}"] for m in METHODS]
add_table(ax,rows,["Method","Accuracy","Traffic (Mbit)","Energy (J)","Max Relay Energy (J)","Rep. JS"],[0,-.52,1,.40],8)
save(fig,"11_synthetic_stress_test.png")

# Manifest and dpi verification
with open(OUT/"FIGURE_MANIFEST.txt","w") as f:
    f.write("Final 600 dpi PNG figure package\n")
    f.write("Captions intentionally excluded from images; manuscript captions remain separate.\n\n")
    for p in sorted(OUT.glob("*.png")):
        im=Image.open(p)
        f.write(f"{p.name}\t{im.size[0]}x{im.size[1]} px\tdpi={im.info.get('dpi')}\n")
        print(p.name,im.size,im.info.get("dpi"))
