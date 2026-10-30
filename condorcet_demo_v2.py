"""Condorcet ABM high-fidelity GUI prototype. No scientific simulation is performed.
Run: python condorcet_demo_v2.py  (standard-library Tkinter only)
"""
import tkinter as tk
from tkinter import ttk
import math
import random

BG='#f4f6fb'; WHITE='#ffffff'; INK='#17243b'; MUTED='#64748b'
BLUE='#4263db'; GREEN='#159879'; ORANGE='#e78b45'; LINE='#e1e7f0'

class Prototype(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Condorcet Jury Theorem | Interactive ABM Prototype')
        self.geometry('1190x830'); self.minsize(990,700); self.configure(bg=BG)
        self.rng=random.Random(12)
        self.population=tk.IntVar(value=51); self.accuracy=tk.DoubleVar(value=.65)
        self.rounds=tk.IntVar(value=8); self.network=tk.StringVar(value='Small-world')
        self.mode=tk.StringVar(value='Source-aware sharing')
        self.step=0; self.nodes=[]; self.edges=[]; self.history=[]; self.play_job=None
        self.build(); self.reset()

    def build(self):
        s=ttk.Style(self); s.theme_use('clam')
        s.configure('TFrame',background=BG); s.configure('TLabel',background=BG,foreground=INK,font=('Arial',10))
        s.configure('Title.TLabel',font=('Arial',21,'bold'))
        s.configure('Muted.TLabel',foreground=MUTED,font=('Arial',10))
        s.configure('TButton',padding=9,font=('Arial',10))
        s.configure('TNotebook',background=BG,borderwidth=0)
        s.configure('TNotebook.Tab',padding=(18,10),font=('Arial',10,'bold'))
        root=ttk.Frame(self,padding=20); root.pack(fill='both',expand=True)
        ttk.Label(root,text="Condorcet's Jury Theorem",style='Title.TLabel').pack(anchor='w')
        ttk.Label(root,text='Interactive research interface prototype  |  Illustrative values, not computed CJT outcomes',style='Muted.TLabel').pack(anchor='w',pady=(4,14))
        self.tabs=ttk.Notebook(root); self.tabs.pack(fill='both',expand=True)
        self.sim=ttk.Frame(self.tabs,padding=12); self.data=ttk.Frame(self.tabs,padding=16)
        self.tabs.add(self.sim,text='  Model Explorer  '); self.tabs.add(self.data,text='  Demo Data & Assumptions  ')
        body=ttk.Frame(self.sim); body.pack(fill='both',expand=True)
        left=ttk.Frame(body,width=270); left.pack(side='left',fill='y',padx=(0,20)); left.pack_propagate(False)
        ttk.Label(left,text='Experiment settings',font=('Arial',13,'bold')).pack(anchor='w',pady=(0,12))
        self.slider(left,'Voters (network shows up to 51)',self.population,11,101,2,integer=True)
        self.slider(left,'Private signal accuracy',self.accuracy,.5,.95,.05)
        self.slider(left,'Communication rounds',self.rounds,0,20,1,integer=True)
        ttk.Label(left,text='Network topology').pack(anchor='w',pady=(13,4))
        ttk.Combobox(left,textvariable=self.network,state='readonly',values=['Small-world','Random','Hub-and-spoke','Fully connected']).pack(fill='x')
        ttk.Label(left,text='Information-sharing rule').pack(anchor='w',pady=(13,4))
        ttk.Combobox(left,textvariable=self.mode,state='readonly',values=['Independent voting','Naive sharing','Source-aware sharing']).pack(fill='x')
        ttk.Button(left,text='Generate new population',command=self.reset).pack(fill='x',pady=(22,5))
        ttk.Button(left,text='Advance one round',command=self.advance).pack(fill='x',pady=5)
        ttk.Button(left,text='Play / Pause',command=self.toggle_play).pack(fill='x',pady=5)
        ttk.Label(left,text='Adjust settings, then generate a new population. All probabilities are scripted illustrations.',style='Muted.TLabel',wraplength=245).pack(anchor='w',pady=(20,0))
        right=ttk.Frame(body); right.pack(side='left',fill='both',expand=True)
        heading=ttk.Frame(right); heading.pack(fill='x')
        ttk.Label(heading,text='Information flow across the voter network',font=('Arial',13,'bold')).pack(side='left')
        self.round_label=ttk.Label(heading,text='Round 0 / 8',foreground=BLUE,font=('Arial',11,'bold')); self.round_label.pack(side='right')
        self.network_canvas=tk.Canvas(right,bg=WHITE,highlightthickness=1,highlightbackground=LINE,height=330)
        self.network_canvas.pack(fill='both',expand=True,pady=(10,8))
        self.network_canvas.bind('<Configure>',lambda e:self.draw_network())
        legend=ttk.Frame(right); legend.pack(fill='x')
        ttk.Label(legend,text='●',foreground=GREEN).pack(side='left')
        ttk.Label(legend,text='Favors A   ').pack(side='left')
        ttk.Label(legend,text='●',foreground=ORANGE).pack(side='left')
        ttk.Label(legend,text='Favors B   ').pack(side='left')
        ttk.Label(legend,text='Click a voter to see its illustrative credence',style='Muted.TLabel').pack(side='right')
        cards=ttk.Frame(right); cards.pack(fill='x',pady=(12,10))
        self.metrics={}
        for i,(key,title) in enumerate([('majority','Illustrative majority confidence'),('mean','Mean belief P(A)'),('support','Agents favoring A')]):
            box=tk.Frame(cards,bg=WHITE,highlightbackground=LINE,highlightthickness=1,padx=13,pady=10)
            box.grid(row=0,column=i,sticky='nsew',padx=(0 if i==0 else 6,0))
            cards.columnconfigure(i,weight=1)
            tk.Label(box,text=title,bg=WHITE,fg=MUTED,font=('Arial',9)).pack(anchor='w')
            val=tk.Label(box,text='—',bg=WHITE,fg=INK,font=('Arial',18,'bold')); val.pack(anchor='w',pady=(5,0))
            self.metrics[key]=val
        ttk.Label(right,text='Round-by-round illustrative probabilities',font=('Arial',12,'bold')).pack(anchor='w')
        self.chart=tk.Canvas(right,bg=WHITE,highlightthickness=1,highlightbackground=LINE,height=180)
        self.chart.pack(fill='x',pady=(7,4)); self.chart.bind('<Configure>',lambda e:self.draw_chart())
        self.note=ttk.Label(right,text='',style='Muted.TLabel',wraplength=740)
        self.note.pack(anchor='w',pady=(4,0))
        self.build_data_tab()

    def slider(self,parent,title,var,low,high,step,integer=False):
        ttk.Label(parent,text=title).pack(anchor='w',pady=(10,2))
        label=ttk.Label(parent,text=''); label.pack(anchor='e')
        def changed(value):
            v=float(value)
            if integer: var.set(int(round(v))); label.config(text=str(var.get()))
            else: var.set(round(v,2)); label.config(text=f'{var.get():.2f}')
        scale=tk.Scale(parent,from_=low,to=high,resolution=step,orient='horizontal',showvalue=False,
                       bg=BG,highlightthickness=0,troughcolor='#dce5f5',activebackground=BLUE,command=changed)
        scale.set(var.get()); scale.pack(fill='x')

    def build_data_tab(self):
        ttk.Label(self.data,text='Demo data and modelling assumptions',font=('Arial',17,'bold')).pack(anchor='w',pady=(0,8))
        ttk.Label(self.data,text='This tab separates presentation-only numbers from the model explorer.',style='Muted.TLabel').pack(anchor='w',pady=(0,15))
        text=(
            'WHAT IS ILLUSTRATED\n'
            '• Each dot is a voter. Its displayed probability P(A) is an invented credence for UI demonstration.\n'
            '• At round 0, beliefs are sampled around the chosen private-signal accuracy.\n'
            '• Later rounds apply a simple visual interpolation toward a neighbour average.\n'
            '• Independent voting leaves beliefs unchanged. Naive and source-aware sharing use different\n'
            '  illustrative influence strengths. These are NOT Bayesian update rules.\n'
            '• The “majority confidence” is a display-only score based on the fraction of voters favoring A;\n'
            '  it is NOT the probability that the majority is objectively correct.\n\n'
            
            'READING THE GRAPH\n'
            '• Blue: illustrative majority confidence (display-only score).\n'
            '• Green: mean displayed credence in alternative A.\n'
            '• Horizontal axis: communication round. Vertical axis: probability / proportion (0–100%).\n'
            '• All series are generated from the prototype’s visible toy state, not from empirical data.'
        )
        panel=tk.Text(self.data,wrap='word',font=('Arial',11),bg=WHITE,fg=INK,relief='flat',padx=18,pady=16,spacing2=5)
        panel.insert('1.0',text); panel.config(state='disabled'); panel.pack(fill='both',expand=True)

    def reset(self):
        self.stop_play(); self.step=0
        n=min(self.population.get(),51)
        self.nodes=[min(.95,max(.05,self.accuracy.get()+self.rng.uniform(-.33,.33))) for _ in range(n)]
        self.make_edges(); self.history=[]; self.record(); self.refresh()

    def make_edges(self):
        n=len(self.nodes); mode=self.network.get()
        if mode=='Hub-and-spoke': self.edges=[(0,i) for i in range(1,n)]
        elif mode=='Fully connected': self.edges=[(i,j) for i in range(n) for j in range(i+1,n)]
        elif mode=='Random': self.edges=[(i,j) for i in range(n) for j in range(i+1,n) if self.rng.random()<min(.14,5/n)]
        else:
            edges={tuple(sorted((i,(i+d)%n))) for i in range(n) for d in (1,2)}
            for _ in range(max(1,n//10)):
                i,j=self.rng.sample(range(n),2); edges.add(tuple(sorted((i,j))))
            self.edges=sorted(edges)

    def record(self):
        mean=sum(self.nodes)/len(self.nodes)
        support=sum(v>=.5 for v in self.nodes)/len(self.nodes)
        # UI-only confidence score; not P(majority correct).
        confidence=max(support,1-support)
        self.history.append((self.step,confidence,mean,support))

    def advance(self):
        if self.step>=self.rounds.get(): self.stop_play(); return
        self.step+=1
        if self.mode.get()!='Independent voting':
            neighbors=[[] for _ in self.nodes]
            for a,b in self.edges: neighbors[a].append(b); neighbors[b].append(a)
            alpha=.34 if self.mode.get()=='Naive sharing' else .16
            old=self.nodes[:]
            for i,adj in enumerate(neighbors):
                if adj:
                    avg=sum(old[j] for j in adj)/len(adj)
                    self.nodes[i]=max(.01,min(.99,(1-alpha)*old[i]+alpha*avg))
        self.record(); self.refresh()

    def toggle_play(self):
        if self.play_job is not None: self.stop_play()
        else: self.play_tick()

    def play_tick(self):
        if self.step>=self.rounds.get(): self.stop_play(); return
        self.advance()
        if self.step<self.rounds.get(): self.play_job=self.after(650,self.play_tick)
        else: self.play_job=None

    def stop_play(self):
        if self.play_job is not None:
            self.after_cancel(self.play_job); self.play_job=None

    def refresh(self):
        self.round_label.config(text=f'Round {self.step} / {self.rounds.get()}')
        _,conf,mean,support=self.history[-1]
        self.metrics['majority'].config(text=f'{conf:.1%}')
        self.metrics['mean'].config(text=f'{mean:.1%}')
        self.metrics['support'].config(text=f'{support:.1%}')
        self.note.config(text=f'Round {self.step}: display-only values. “Majority confidence” is not P(correct majority).  '
                         f'Showing {len(self.nodes)} of {self.population.get()} configured voters.')
        self.draw_network(); self.draw_chart()

    def draw_network(self):
        c=self.network_canvas; c.delete('all')
        if not self.nodes:return
        w=max(c.winfo_width(),550); h=max(c.winfo_height(),280); n=len(self.nodes)
        cx=w/2; cy=h/2; radius=min(w*.36,h*.40)
        points=[(cx+radius*math.cos(2*math.pi*i/n),cy+radius*math.sin(2*math.pi*i/n)) for i in range(n)]
        for a,b in self.edges:
            x1,y1=points[a]; x2,y2=points[b]
            c.create_line(x1,y1,x2,y2,fill='#dbe3ef',width=1)
        for i,(x,y) in enumerate(points):
            color=GREEN if self.nodes[i]>=.5 else ORANGE
            tag=f'node_{i}'
            c.create_oval(x-7,y-7,x+7,y+7,fill=color,outline='white',width=1,tags=(tag,'node'))
            c.tag_bind(tag,'<Button-1>',lambda e,idx=i:self.show_agent(idx))
        c.create_text(cx,cy-8,text=f'{self.network.get()} network',font=('Arial',12,'bold'),fill=INK)
        c.create_text(cx,cy+13,text='Select any node for P(A)',font=('Arial',10),fill=MUTED)

    def show_agent(self,index):
        self.note.config(text=f'Voter {index+1}: illustrative P(A) = {self.nodes[index]:.1%} at round {self.step}. '
                         'This is a display value, not a Bayesian posterior.')

    def draw_chart(self):
        c=self.chart; c.delete('all')
        w=max(c.winfo_width(),530); h=max(c.winfo_height(),170)
        left=52; right=w-18; top=16; bottom=h-31
        for value in (0,.25,.5,.75,1):
            y=bottom-(bottom-top)*value
            c.create_line(left,y,right,y,fill='#edf0f6')
            c.create_text(left-7,y,text=f'{value:.0%}',anchor='e',fill=MUTED,font=('Arial',8))
        c.create_line(left,top,left,bottom,right,bottom,fill='#9caabd')
        total=max(1,self.rounds.get())
        for tick in sorted(set([0,total//2,total])):
            x=left+(right-left)*tick/total
            c.create_text(x,bottom+14,text=str(tick),fill=MUTED,font=('Arial',9))
        series=[(1,BLUE),(2,GREEN)]
        for column,color in series:
            pts=[]
            for row in self.history:
                x=left+(right-left)*row[0]/total
                y=bottom-(bottom-top)*row[column]
                pts.extend((x,y))
            if len(pts)>=4:c.create_line(*pts,fill=color,width=2.5)
            if pts:c.create_oval(pts[-2]-4,pts[-1]-4,pts[-2]+4,pts[-1]+4,fill=color,outline='white')
        c.create_text(right-8,top+2,text='● Majority confidence    ● Mean P(A)',anchor='ne',fill=INK,font=('Arial',9))

if __name__=='__main__':
    Prototype().mainloop()
