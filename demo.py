from math import *
from Tkinter import *
DELAY = 20
import the3,evaluator,os

SCALE = 1.0

demos = {
    'Unstable star system': [10,1.0,[2000.,400,400,0.,0.],[60.,50,400,0.,5.],[100.,150,400,0.,5.]],
    'Rotating circles': [10,1.0,[640.,300,400,0.,-4.],[640.,500,400,0.,4.]],
    'Rotating circles with one in middle': [10,1.0,[640.,300,400,0.,-4.],[640.,500,400,0.,4.],[100,400,400,0,0]] ,
    'Eliptically Rotating Circles': [20,1.0,[400.,340,300,4,0],[400.,460,500,-4,0]] ,
    'Stable Star System' : [40,1.0,[1000.,400,400,0,0],[10.,500,400,0,20],[10,100,400,0,-11.547]],
    'BOOM' : [500,.025,[100, 250, 250, -10, -10], [100, 400, 150, 0, -10], [100, 550, 250, 10, -10], [100, 650, 400, 10, 0], [100, 550, 550, 10, 10], [100, 400, 650, 0, 10], [100, 250, 550, -10, 10], [100, 150, 400, -10, 0]],
    'Solar system with moon' : [3.,.25,[1500.,200.,500,0.,0.],[150.,200.,100.,3.,0.],[10.,200.,50.,6.,0.]],
    'Two Lithiums': [100, 0.025, [1.0, 250.0, 135.0, 17.0, 0.0], [1.0, 141.74682452694518, 322.5, -1.0, 10.392304845413264], [1.0, 358.25317547305485, 322.5, -1.0, -10.392304845413264], [250.0, 250.0, 260.0, 5.0, 0.0], [1.0, 750.0, 455.0, 12.0, 0.0], [1.0, 641.7468245269451, 642.5, -6.0, 10.392304845413264], [1.0, 858.2531754730549, 642.5, -6.0, -10.392304845413264], [250.0, 750.0, 580.0, 0.0, 0.0]]
}

def drawcircle(canv,x,y,rad):
	return canv.create_oval(SCALE*(x-rad),SCALE*(y-rad),SCALE*(x+rad),SCALE*(y+rad),width=0,fill='red')

def drawcircles():    
    global My_canvas, My_circles, DELAY
    My_circles=[]
    circlelist = [] # will hold a list of [x,y,r]
    data = evaluator.get_data()[2:] #drop G value and Delta t	
    max_mass = max([m for [m,x,y,vx,vy] in data])
    for [m,x,y,vx,vy] in data:
       circlelist.append([x,y,1+sqrt(m/max_mass)*20])  
    for [center_x,center_y,radius] in circlelist:
        My_circles.append(drawcircle(My_canvas,center_x,center_y,radius))
    My_canvas.after(DELAY,callback)

def movecircles():
    global My_circles, My_canvas,My_circles2
    deltalist = the3.new_move() # user provides new_move(): list of [dx,dy]
    for i,[dx,dy] in enumerate(deltalist):
        My_canvas.move(My_circles[i],SCALE*dx,SCALE*dy)
        
def callback():
    global My_canvas,DELAY
    movecircles()
    My_canvas.after(DELAY,callback)

def selectDemo(name):
    with open('evaluator.py','w') as f:
        f.write('def get_data(): return '+str(demos[name]))

def reset():
    global SCALE
    os.remove(getattr(the3, '__cached__', 'the3.pyc'))
    os.remove(getattr(evaluator, '__cached__', 'evaluator.pyc'))
    SCALE = 1.0
    reload(evaluator);
    reload(the3);

def createSelectDialog():
    dialog = Tk()
    dialog.configure(bg='black')
    
    Label(dialog,text='evaluator.py will be overwritten if it exists',bg='black',fg='white').pack()
    
    l = Listbox(dialog,bg='black',fg='white',selectbackground='gray50')
    for i in demos.keys(): l.insert(END,i)
    l.pack(fill=X)
    
    def startMain():
        selected = l.get(ACTIVE)
        dialog.destroy()
        selectDemo(selected)
        reset()
        createMain(selected)
        
    Button(dialog,text='Start',command=startMain,bg='black',fg='white',activebackground='gray30',activeforeground='white').pack()
    
    dialog.mainloop()
    
def updateDelay(d):
    global DELAY
    DELAY = d
    
def createMain(name):
    global My_canvas,info,My_circles
    Master = Tk()
    Master.configure(background='black')
    My_canvas = Canvas(Master, width=800, height=800, bg ='black',highlightthickness=0)
    My_canvas.pack()
    drawcircles()
    
    def moveFrom(event):
        My_canvas.scan_mark(event.x, event.y)
    def moveTo(event):
        My_canvas.scan_dragto(event.x, event.y, gain=1)
    def zoomIn(event):
        global SCALE
        mx = My_canvas.canvasx(event.x)
        my = My_canvas.canvasy(event.y)
        My_canvas.scale('all', mx, my, 1.2, 1.2)
        SCALE *= 1.2
    def zoomOut(event):
        global SCALE
        mx = My_canvas.canvasx(event.x)
        my = My_canvas.canvasy(event.y)
        My_canvas.scale('all', mx, my, 0.8, 0.8)
        SCALE *= 0.8
    def wheel(event):
        if event.delta>0: zoomOut(event)
        else: zoomIn(event)
    
    My_canvas.bind('<ButtonPress-1>', moveFrom)
    My_canvas.bind('<B1-Motion>',     moveTo)
    My_canvas.bind('<Button-5>',   zoomOut) 
    My_canvas.bind('<Button-4>',   zoomIn)
    My_canvas.bind('<MouseWheel>', wheel) 
    
    lbl = Label(Master, text=name, background='black',fg = 'white')
    lbl.pack()
    def change():
        Master.destroy()
        createSelectDialog()
    Button(Master,text ='Select Demo',command=change,bg='black',fg='white',activebackground='gray30',activeforeground='white').pack();
    
    Label(Master, text='Delay: ', bg='black',fg='white').pack(side=LEFT);
    w2 = Scale(Master, from_=5, to=200, orient=HORIZONTAL, bg='black',fg='white',troughcolor='gray20',length=750,highlightthickness=0,command=updateDelay)
    w2.set(20)
    w2.pack(side=LEFT,fill=X)
    
    Master.mainloop()
    
createMain("Use mouse to pan, scrollwheel to zoom in/out")
