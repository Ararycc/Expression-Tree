"""Launch with: python main.py (Python 3.10+, standard library only)."""
import tkinter as tk
from tkinter import ttk
import math
import random
import time
from tree_model import build_values, build_expression, traversals, evaluate, number, format_number
from tree_examples import random_example

BG='#F4F6FB'; PANEL='#FFFFFF'; FIELD='#F7F9FC'; BORDER='#E1E7F0'
INK='#182235'; MUTED='#6F7C91'; BLUE='#5267E8'; GREEN='#0F9F86'; GOLD='#D98A24'; CORAL='#D65D75'
CANVAS_BG='#071426'

class TreeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Tree Studio | Expression & Traversal Lab')
        self.geometry('1400x900'); self.minsize(1060,760); self.configure(bg=BG)
        self.root_node=None; self.orders={}; self.positions={}; self.scale=1; self.offset=[0,0]
        self.highlight=None; self.job=None; self.sequence=[]; self.step_index=0
        self.motion=tk.BooleanVar(value=True)
        self.animation_job=None; self.animation_time=0.; self.last_frame=time.perf_counter()
        self.entrance_start=-2.; self.backdrop_size=None
        rng=random.Random()
        self.particles=[(rng.random(),rng.random(),rng.uniform(.008,.025),rng.uniform(1,2.5),rng.uniform(0,math.tau)) for _ in range(28)]
        self.kind=tk.StringVar(value='Numerical'); self.layout=tk.StringVar(value='Binary search tree')
        self.expression=tk.BooleanVar(); self.notation=tk.StringVar(value='Infix'); self.order=tk.StringVar(value='Preorder')
        self.status=tk.StringVar(value='Ready — build a tree to begin.'); self.result=tk.StringVar(value='No result yet')
        self.inputs=tk.StringVar(); self.output_vars={}
        style=ttk.Style(self); style.theme_use('clam')
        style.configure('TCombobox',padding=8,fieldbackground=FIELD,background=FIELD,
                        foreground=INK,arrowcolor=BLUE,bordercolor=BORDER,lightcolor=FIELD,darkcolor=FIELD)
        style.map('TCombobox',fieldbackground=[('readonly',FIELD),('disabled','#EDF0F5')],
                  foreground=[('disabled','#9AA4B5'),('readonly',INK)],
                  selectbackground=[('readonly',FIELD)],selectforeground=[('readonly',INK)])
        self.option_add('*TCombobox*Listbox.background',FIELD)
        self.option_add('*TCombobox*Listbox.foreground',INK)
        self.option_add('*TCombobox*Listbox.selectBackground','#DCE3FF')
        # App shell: compact header, left control rail, spacious canvas, bottom results.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header=tk.Frame(self,bg=BG)
        header.grid(row=0,column=0,sticky='ew',padx=24,pady=(18,14))
        header.columnconfigure(1,weight=1)
        mark=tk.Frame(header,bg=INK,width=42,height=42)
        mark.grid(row=0,column=0,rowspan=2,sticky='w',padx=(0,12)); mark.pack_propagate(False)
        tk.Label(mark,text='T',font=('Segoe UI',22,'bold'),bg=INK,fg='white').place(relx=.5,rely=.5,anchor='center')
        tk.Label(header,text='TREE LAB',font=('Segoe UI',19,'bold'),bg=BG,fg=INK).grid(row=0,column=1,sticky='sw')
        tk.Label(header,text='Build · inspect · traverse · evaluate',font=('Segoe UI',9),bg=BG,fg=MUTED).grid(row=1,column=1,sticky='nw',pady=(1,0))
        head_right=tk.Frame(header,bg=BG); head_right.grid(row=0,column=2,rowspan=2,sticky='e')
        tk.Label(head_right,text='VISUAL ALGORITHM WORKBENCH',font=('Segoe UI',8,'bold'),bg=BG,fg=MUTED).pack(side='left',padx=(0,14))
        tk.Checkbutton(head_right,text='Motion',variable=self.motion,command=self.toggle_motion,bg=BG,fg=INK,
                       activebackground=BG,activeforeground=INK,selectcolor=FIELD,font=('Segoe UI',9),cursor='hand2',bd=0).pack(side='left')

        workspace=tk.Frame(self,bg=BG)
        workspace.grid(row=1,column=0,sticky='nsew',padx=24,pady=(0,14))
        workspace.columnconfigure(1,weight=1); workspace.rowconfigure(0,weight=1)

        # Left rail: all creation controls in a single vertical workflow.
        sidebar=tk.Frame(workspace,bg=PANEL,highlightbackground=BORDER,highlightthickness=1,width=286,padx=17,pady=17)
        sidebar.grid(row=0,column=0,sticky='nsw',padx=(0,16)); sidebar.grid_propagate(False)
        tk.Label(sidebar,text='01  /  CONFIGURE',bg=PANEL,fg=BLUE,font=('Segoe UI',9,'bold')).pack(anchor='w')
        tk.Label(sidebar,text='Create your tree',bg=PANEL,fg=INK,font=('Segoe UI',15,'bold')).pack(anchor='w',pady=(5,3))
        tk.Label(sidebar,text='Choose a structure and provide its input.',bg=PANEL,fg=MUTED,font=('Segoe UI',9),wraplength=240,justify='left').pack(anchor='w',pady=(0,17))

        def section_label(text):
            tk.Label(sidebar,text=text,bg=PANEL,fg=MUTED,font=('Segoe UI',8,'bold')).pack(anchor='w',pady=(0,5))
        section_label('DATA TYPE')
        self.kind_combo=self.combo(sidebar,self.kind,['Numerical','Alphabetical'],self.mode_changed)
        self.kind_combo.pack_configure(pady=(0,13))
        section_label('TREE STRUCTURE')
        self.layout_combo=self.combo(sidebar,self.layout,['Binary search tree','Level-filled tree'])
        self.layout_combo.pack_configure(pady=(0,13))
        section_label('EXPRESSION NOTATION')
        self.notation_combo=self.combo(sidebar,self.notation,['Infix','Prefix','Postfix'])
        self.notation_combo.pack_configure(pady=(0,13))
        self.check=tk.Checkbutton(sidebar,text='Build arithmetic expression',variable=self.expression,command=self.mode_changed,
                                  bg=PANEL,fg=INK,activebackground=PANEL,activeforeground=INK,selectcolor=FIELD,
                                  disabledforeground='#9AA4B5',font=('Segoe UI',9),cursor='hand2',bd=0,wraplength=230,justify='left')
        self.check.pack(anchor='w',pady=(0,15))
        section_label('INPUT')
        self.entry=tk.Entry(sidebar,textvariable=self.inputs,font=('Consolas',11),bg=FIELD,fg=INK,insertbackground=BLUE,
                            selectbackground='#DCE3FF',relief='flat',bd=0,highlightthickness=1,
                            highlightbackground=BORDER,highlightcolor=BLUE)
        self.entry.pack(fill='x',ipady=10,pady=(0,7)); self.entry.bind('<Return>',lambda e:self.build())
        self.hint=tk.Label(sidebar,text='',bg=PANEL,fg=MUTED,anchor='w',justify='left',wraplength=245,font=('Segoe UI',8))
        self.hint.pack(fill='x',pady=(0,13))
        self.button(sidebar,'Build tree  →',self.build,BLUE).pack(fill='x',pady=(0,7))
        action_row=tk.Frame(sidebar,bg=PANEL); action_row.pack(fill='x')
        self.button(action_row,'↻ Example',self.example,FIELD).pack(side='left',fill='x',expand=True,padx=(0,5))
        self.button(action_row,'Clear',self.clear,FIELD).pack(side='left',fill='x',expand=True,padx=(5,0))

        # Canvas stage: primary focus, with tools grouped directly beneath it.
        stage=tk.Frame(workspace,bg=PANEL,highlightbackground=BORDER,highlightthickness=1)
        stage.grid(row=0,column=1,sticky='nsew'); stage.columnconfigure(0,weight=1); stage.rowconfigure(1,weight=1)
        canvas_header=tk.Frame(stage,bg=PANEL,padx=19,pady=14)
        canvas_header.grid(row=0,column=0,sticky='ew'); canvas_header.columnconfigure(0,weight=1)
        tk.Label(canvas_header,text='Tree canvas',bg=PANEL,fg=INK,font=('Segoe UI',14,'bold')).grid(row=0,column=0,sticky='w')
        tk.Label(canvas_header,text='Select a node · drag to pan · scroll to zoom',bg=PANEL,fg=MUTED,font=('Segoe UI',9)).grid(row=1,column=0,sticky='w',pady=(3,0))
        tk.Label(canvas_header,text='02  /  VISUALIZE',bg=PANEL,fg=BLUE,font=('Segoe UI',8,'bold')).grid(row=0,column=1,rowspan=2,sticky='e',padx=(12,0))
        self.canvas=tk.Canvas(stage,bg=CANVAS_BG,highlightthickness=0,width=1,height=300)
        self.canvas.grid(row=1,column=0,sticky='nsew',padx=1)
        self.canvas.bind('<Configure>',lambda e:self.draw())
        self.canvas.bind('<ButtonPress-1>',self.drag_start); self.canvas.bind('<B1-Motion>',self.drag)
        self.canvas.bind('<MouseWheel>',lambda e:self.zoom(1.15 if e.delta>0 else 1/1.15,e.x,e.y))
        self.canvas.bind('<Button-4>',lambda e:self.zoom(1.15,e.x,e.y)); self.canvas.bind('<Button-5>',lambda e:self.zoom(1/1.15,e.x,e.y))

        toolbar=tk.Frame(stage,bg='#FAFBFE',highlightbackground=BORDER,highlightthickness=1,padx=14,pady=11)
        toolbar.grid(row=2,column=0,sticky='ew')
        toolbar.columnconfigure(1,weight=1)
        tk.Label(toolbar,text='TRAVERSAL',bg='#FAFBFE',fg=MUTED,font=('Segoe UI',8,'bold')).grid(row=0,column=0,sticky='w',padx=(0,10))
        playback=tk.Frame(toolbar,bg='#FAFBFE'); playback.grid(row=0,column=1,sticky='w')
        walk=ttk.Combobox(playback,textvariable=self.order,values=['Preorder','Inorder','Postorder','Level order'],state='readonly',width=12)
        walk.pack(side='left',padx=(0,7)); walk.bind('<<ComboboxSelected>>',lambda e:self.reset_walk())
        for name,fn,color in [('▶ Play',self.play,BLUE),('Ⅱ Pause',self.pause,FIELD),('Step →',self.step,FIELD)]:
            self.button(playback,name,fn,color).pack(side='left',padx=3)
        navigation=tk.Frame(toolbar,bg='#FAFBFE'); navigation.grid(row=0,column=2,sticky='e',padx=(10,0))
        for title,fn in [('−',lambda:self.zoom(.8)),('+',lambda:self.zoom(1.25)),('Fit',self.fit),('←',lambda:self.pan(50,0)),('→',lambda:self.pan(-50,0)),('↑',lambda:self.pan(0,50)),('↓',lambda:self.pan(0,-50))]:
            button=self.button(navigation,title,fn,FIELD); button.configure(padx=8,pady=7); button.pack(side='left',padx=2)

        # Bottom results strip: four equal cards are easier to compare than a tall side panel.
        results=tk.Frame(self,bg=BG)
        results.grid(row=2,column=0,sticky='ew',padx=24,pady=(0,10))
        results.columnconfigure(0,weight=1); results.columnconfigure(1,weight=1); results.columnconfigure(2,weight=1); results.columnconfigure(3,weight=1); results.columnconfigure(4,weight=1)
        tk.Label(results,text='03  /  TRAVERSAL OUTPUT',bg=BG,fg=BLUE,font=('Segoe UI',8,'bold')).grid(row=0,column=0,columnspan=4,sticky='w',pady=(0,7))
        for col,(name,color) in enumerate(zip(['Preorder','Inorder','Postorder','Level order'],[BLUE,GREEN,CORAL,GOLD])):
            frame=tk.Frame(results,bg=PANEL,highlightbackground=BORDER,highlightthickness=1,padx=12,pady=10)
            frame.grid(row=1,column=col,sticky='nsew',padx=(0 if col==0 else 6,0 if col==3 else 6))
            top=tk.Frame(frame,bg=PANEL); top.pack(fill='x')
            tk.Label(top,text='●',bg=PANEL,fg=color,font=('Segoe UI',9)).pack(side='left')
            self.button(top,name,lambda n=name:self.select_order(n),PANEL).pack(side='left',padx=(5,0))
            var=tk.StringVar(value='—'); self.output_vars[name]=var
            entry=tk.Entry(frame,textvariable=var,state='readonly',readonlybackground=PANEL,fg=INK,selectbackground='#DCE3FF',
                           relief='flat',font=('Consolas',9),width=1,bd=0)
            entry.pack(fill='x',pady=(8,0))
        summary=tk.Frame(results,bg='#EAF7F3',highlightbackground='#C9E9DF',highlightthickness=1,padx=13,pady=10)
        summary.grid(row=1,column=4,sticky='nsew',padx=(6,0))
        tk.Label(summary,text='TREE SUMMARY',bg='#EAF7F3',fg=GREEN,font=('Segoe UI',8,'bold')).pack(anchor='w')
        tk.Label(summary,textvariable=self.result,bg='#EAF7F3',fg='#126D5E',font=('Segoe UI',10,'bold'),anchor='w',justify='left',wraplength=190).pack(fill='x',pady=(5,0))

        footer=tk.Frame(self,bg=BG); footer.grid(row=3,column=0,sticky='ew',padx=24,pady=(0,12))
        tk.Label(footer,text='●',bg=BG,fg=GREEN,font=('Segoe UI',9)).pack(side='left',padx=(0,8))
        self.status_label=tk.Label(footer,textvariable=self.status,bg=BG,fg=MUTED,anchor='w',justify='left',font=('Segoe UI',9),wraplength=1250)
        self.status_label.pack(side='left',fill='x',expand=True)

        self.mode_changed()
        self.protocol('WM_DELETE_WINDOW',self.close)
        self.animate()

    def button(self,parent,text,command,color):
        primary = color == BLUE
        foreground = '#FFFFFF' if primary else INK
        hover = '#4054D0' if primary else '#E9EEF7'
        button=tk.Button(parent,text=text,command=command,bg=color,fg=foreground,activebackground=hover,
                         activeforeground=foreground,relief='flat',bd=0,cursor='hand2',font=('Segoe UI',9,'bold'),padx=11,pady=8)
        button.bind('<Enter>',lambda e:button.configure(bg=hover))
        button.bind('<Leave>',lambda e:button.configure(bg=color))
        return button
    def combo(self,parent,var,values,callback=None):
        box=ttk.Combobox(parent,textvariable=var,values=values,state='readonly',width=15); box.pack(fill='x')
        if callback: box.bind('<<ComboboxSelected>>',lambda e:callback())
        return box
    def mode_changed(self):
        alpha=self.kind.get()=='Alphabetical'
        if alpha:self.expression.set(False)
        self.check.configure(state='disabled' if alpha else 'normal')
        expr=self.expression.get()
        self.notation_combo.configure(state='readonly' if expr else 'disabled')
        self.layout_combo.configure(state='disabled' if expr else 'readonly')
        self.hint.configure(text=('Use parentheses in infix; separate every token with spaces in prefix and postfix.' if expr
                                 else 'Separate numbers with spaces or commas. Try Load example for a larger tree.' if not alpha
                                 else 'Separate letters or words with spaces. Try Load example for a nature-inspired tree.'))
    def build(self):
        try:
            expr=self.expression.get()
            root=build_expression(self.inputs.get(),self.notation.get()) if expr else build_values(self.inputs.get(),self.kind.get(),self.layout.get())
            orders=traversals(root)
            result=('Expression value  =  '+format_number(evaluate(root)) if expr else 'Sum of all numbers  =  '+format_number(sum(number(n.value) for n in orders['Preorder'])) if self.kind.get()=='Numerical' else 'Alphabetical tree  •  '+str(len(orders['Preorder']))+' nodes')
        except (ValueError,RecursionError) as error:
            self.status.set('Cannot build: '+str(error)); return
        self.reset_walk(); self.root_node=root; self.orders=orders; self.result.set(result)
        for name,nodes in orders.items():self.output_vars[name].set(' → '.join(n.value for n in nodes))
        self.positions={}; index=0
        def place(node,depth):
            nonlocal index
            if not node:return
            place(node.left,depth+1); self.positions[node]=(index*100,depth*110); index+=1; place(node.right,depth+1)
        place(root,0); self.entrance_start=self.animation_time; self.fit()
        self.status.set('Tree built. Traversals visit the same nodes in different orders; the sum stays the same.' if not expr else 'Expression evaluated using the tree structure. Inorder output omits parentheses; it is a traversal, not a new formula.')
    def example(self):
        self.inputs.set(random_example(kind=self.kind.get(),expression=self.expression.get(),
                                       notation=self.notation.get(),previous=self.inputs.get()))
        self.build()
    def clear(self):
        self.reset_walk(); self.root_node=None; self.orders={}; self.positions={}; self.inputs.set(''); self.result.set('Overall value  —')
        for var in self.output_vars.values():var.set('—')
        self.status.set('Workspace cleared.'); self.draw()
    def fit(self):
        if not self.positions:self.draw();return
        self.update_idletasks(); coords=list(self.positions.values()); xs=[p[0] for p in coords]; ys=[p[1] for p in coords]
        w,h=self.canvas.winfo_width(),self.canvas.winfo_height()
        self.scale=max(.08,min(1.3,(w-90)/(max(xs)-min(xs)+80),(h-90)/(max(ys)-min(ys)+80)))
        self.offset=[w/2-(max(xs)+min(xs))/2*self.scale,h/2-(max(ys)+min(ys))/2*self.scale];self.draw()
    def zoom(self,factor,x=None,y=None):
        x=self.canvas.winfo_width()/2 if x is None else x;y=self.canvas.winfo_height()/2 if y is None else y
        new=max(.08,min(3,self.scale*factor));ratio=new/self.scale
        self.offset=[x+(self.offset[0]-x)*ratio,y+(self.offset[1]-y)*ratio];self.scale=new;self.draw()
    def pan(self,x,y):self.offset[0]+=x;self.offset[1]+=y;self.draw()
    def drag_start(self,event):
        self.last=(event.x,event.y)
        for node in self.positions:
            x,y=self.node_point(node)
            if (event.x-x)**2+(event.y-y)**2 <= (28*self.scale)**2:
                self.highlight=node;self.status.set('Selected node: '+node.value);self.draw();break
    def drag(self,event):
        x,y=self.last;self.pan(event.x-x,event.y-y);self.last=(event.x,event.y)
    def toggle_motion(self):
        if self.animation_job is not None:
            self.after_cancel(self.animation_job); self.animation_job=None
        # Resume from the same ambient phase, without replaying the entrance.
        self.entrance_start=self.animation_time-2
        self.last_frame=time.perf_counter()
        if self.motion.get():self.animate()
        else:self.draw()

    def animate(self):
        self.animation_job=None
        now=time.perf_counter()
        self.animation_time+=min(now-self.last_frame,.1); self.last_frame=now
        self.draw()
        if self.motion.get():self.animation_job=self.after(33,self.animate)

    def close(self):
        self.pause()
        if self.animation_job is not None:
            self.after_cancel(self.animation_job); self.animation_job=None
        self.destroy()

    def node_point(self,node):
        x,y=self.positions[node]
        progress=min(1.,max(0.,(self.animation_time-self.entrance_start)/.85)) if self.motion.get() else 1.
        ease=1-(1-progress)**3
        return x*self.scale+self.offset[0],y*self.scale+self.offset[1]+(1-ease)*42

    def draw_backdrop(self,w,h):
        c=self.canvas; t=self.animation_time
        # Deep-space observatory: layered midnight gradient, technical grid and orbit marks.
        if self.backdrop_size!=(w,h):
            c.delete('backdrop'); self.backdrop_size=(w,h)
            top=(7,20,38); bottom=(15,39,63)
            for i in range(48):
                q=i/47
                rgb=tuple(int(top[k]*(1-q)+bottom[k]*q) for k in range(3))
                color='#%02x%02x%02x'%rgb
                c.create_rectangle(0,h*i/48,w,h*(i+1)/48+1,fill=color,outline='',tags='backdrop')
            # Fine drafting grid with every fifth line slightly brighter.
            for x in range(0,w,28):
                major=(x//28)%5==0
                c.create_line(x,0,x,h,fill='#18324A' if major else '#10283E',width=1,tags='backdrop')
            for y in range(0,h,28):
                major=(y//28)%5==0
                c.create_line(0,y,w,y,fill='#18324A' if major else '#10283E',width=1,tags='backdrop')
            # Large, cropped orbital rings give the canvas a unique observatory identity.
            ox,oy=w*.82,h*.18
            for radius in (54,82,112):
                c.create_oval(ox-radius,oy-radius,ox+radius,oy+radius,outline='#173B50',width=1,tags='backdrop')
            for x,y,r in ((.12,.2,2),(.24,.72,1.5),(.68,.12,2),(.91,.66,2),(.77,.84,1.5),(.42,.18,1)):
                px,py=x*w,y*h
                c.create_oval(px-r,py-r,px+r,py+r,fill='#4D8298',outline='',tags='backdrop')
            c.tag_lower('backdrop')
        c.delete('ambient')
        # A slow, understated teal aurora glow along the lower canvas edge.
        points=[0,h]
        for i in range(25):
            x=w*i/24
            y=h*(.82+math.sin(i*.25+t*.18)*.035+math.sin(i*.51-t*.12)*.018)
            points.extend((x,y))
        points.extend((w,h))
        c.create_polygon(*points,fill='#0B2938',outline='',tags='ambient')
        for u,v,speed,r,phase in self.particles:
            x=(u*w+math.sin(t*.3+phase)*18)%max(w,1)
            y=((v-t*speed)%1)*h
            c.create_oval(x-r,y-r,x+r,y+r,fill='#55A6B7' if r<2 else '#39758C',outline='',tags='ambient')

    def draw(self):
        c=self.canvas;c.delete('tree');w,h=c.winfo_width(),c.winfo_height()
        self.draw_backdrop(w,h)
        if not self.positions:
            cx,cy=w/2,h/2-65
            for radius,color in ((32,'#DDE5F5'),(24,'#AFC0F1'),(13,BLUE)):
                c.create_oval(cx-radius,cy-radius,cx+radius,cy+radius,outline=color,width=1.5,tags='tree')
            c.create_text(w/2,h/2-5,text='Curiosity is the root of every discovery.',fill='#EAF5FF',font=('Segoe UI',19,'bold'),tags='tree')
            c.create_text(w/2,h/2+30,text='Build a tree. Follow every connection.',fill='#8EB3C8',font=('Segoe UI',11),tags='tree');return
        point=self.node_point
        for n in self.positions:
            x,y=point(n)
            for child in (n.left,n.right):
                if child:
                    xx,yy=point(child)
                    # Angular connector: diagonal from the parent, a short elbow, then diagonal to child.
                    # No smoothing is used, so the edges stay crisp rather than wavy.
                    mid_y=y+(yy-y)*.52
                    coords=(x,y, x+(xx-x)*.32,mid_y, xx-(xx-x)*.12,mid_y+(yy-y)*.10, xx,yy)
                    c.create_line(*coords,fill='#07101E',width=max(3,7*self.scale),joinstyle='round',tags='tree')
                    c.create_line(*coords,fill='#3B718B',width=max(1,1.8*self.scale),joinstyle='round',tags='tree')
                    if child is self.highlight:
                        c.create_line(*coords,fill=GOLD,width=max(2,2.8*self.scale),joinstyle='round',tags='tree')
        for n in self.positions:
            x,y=point(n);r=27*self.scale;color=GOLD if n is self.highlight else GREEN if n is self.root_node else BLUE
            if n is self.highlight or n is self.root_node:
                pulse=(math.sin(self.animation_time*2.8)+1)*2.5 if self.motion.get() else 2
                halo=r+(7+pulse)*self.scale
                c.create_oval(x-halo,y-halo,x+halo,y+halo,outline='#65577e',width=2,tags='tree')
            c.create_oval(x-r-4,y-r-4,x+r+4,y+r+4,outline='#34516B',width=1,tags='tree')
            c.create_oval(x-r,y-r,x+r,y+r,fill='#FFFFFF',outline=color,width=max(1,2*self.scale),tags='tree')
            c.create_text(x,y,text=n.value,fill=INK,font=('Segoe UI',max(6,int(12*self.scale)),'bold'),tags='tree')
        c.create_text(18,20,text=f'{len(self.positions)} NODES  /  {self.scale:.0%}',anchor='w',fill=MUTED,font=('Segoe UI',9),tags='tree')
        c.create_text(w-18,20,text='TREE STUDIO',anchor='e',fill='#7EA5BC',font=('Segoe UI',9),tags='tree')
    def pause(self):
        if self.job:self.after_cancel(self.job);self.job=None
    def reset_walk(self):
        self.pause();self.step_index=0;self.highlight=None;self.draw() if hasattr(self,'canvas') else None
    def select_order(self,name):self.order.set(name);self.reset_walk();self.step()
    def step(self):
        self.pause();nodes=self.orders.get(self.order.get(),[])
        if not nodes:self.status.set('Build a tree before starting a traversal.');return False
        if self.step_index>=len(nodes):self.step_index=0
        self.highlight=nodes[self.step_index];self.step_index+=1
        self.status.set(f'{self.order.get()} • Step {self.step_index}/{len(nodes)} • '+ ' → '.join(n.value for n in nodes[:self.step_index]));self.draw()
        return self.step_index<len(nodes)
    def play(self):
        if self.step():self.job=self.after(650,self.play)

if __name__=='__main__':TreeApp().mainloop()
