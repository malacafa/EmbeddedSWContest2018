from ev3dev.ev3 import *
from time import *
import random, itertools
######map_info################################################################################
s = {'A1':'GB','B1':'YR','C1':'YY','D1':'YB','E1':'RY','F1':'BB','G1':'YR', \
     'A2':'BY','G2':'BY', \
     'A3':'BB','G3':'RB', \
     'A4':'BY','B4':'GR','C4':'YB','D4':'GY','E4':'BR','F4':'GB','G4':'RR', \
     'A5':'GY','B5':'RY','C5':'BR','D5':'YY','E5':'GR','F5':'RR','G5':'RB'}

t = [('ST','00'),('F','A5'),('F','B5'),('V','00'),('F','C5'),('F','D5'),('F','E5'),('V','00'),('F','F5'),('F','G5'), \
     ('L','G4'),('L','F4'),('V','00'),('F','E4'),('F','D4'),('V','00'),('F','C4'),('F','B4'),('V','00'),('F','A4'), \
	 ('R','A3'),('V','00'),('F','A2'), \
	 ('F','A1'),('R','B1'),('F','C1'),('V','00'),('F','D1'),('F','E1'),('V','00'),('F','F1'),('F','G1'), \
	 ('R','G2'),('F','G3'),('V','00'),('F','00'),('F','00'),\
	 ('R','00'),('F','00'),('F','00'),('V','00'),('F','00'),('F','00'),('F','00')]
#####var_set###########################################################################################
colors =('U','K','B','G','Y','R','W','N') #color define 
fwspeed = 250
TH = 30
col = {}
cmd = []
outline='' # global var. for vertical_align
################################################################################################
sel=' ';loc=[];path=[];colperlist=[];store={'R':[],'G':[],'B':[],'Y':[]}
################################################################################################
lm = LargeMotor('outB')
rm = LargeMotor('outC')
dm = MediumMotor('outD')
#motor define
lc = ColorSensor('in1')
lc.mode = 'COL-REFLECT'
rc = ColorSensor('in2')
rc.mode = 'COL-REFLECT'
mc = ColorSensor('in3')
mc.mode = 'COL-COLOR'
#sensor define
lm.stop(stop_action="hold")
rm.stop(stop_action="hold")
#start set

def wait(tt):#pre-define for sm
	current_time = time()
	while True:
		if time() - current_time > tt:
			break

def Beep():
    Sound.beep()

def led_on():
    Leds.set_color(Leds.LEFT,Leds.RED)
    Leds.set_color(Leds.RIGHT,Leds.RED)

def led_off():
    Leds.all_off()

def sm(t):
    lm.stop(stop_action='hold')
    rm.stop(stop_action='hold')
    wait(t)

def sm_for_dm(t):
    dm.stop(stop_action='hold')
    wait(t)

def mv(l,r,spd=200):#mv method
    lm.run_to_rel_pos(position_sp=l,speed_sp=spd,stop_action='hold')
    rm.run_to_rel_pos(position_sp=r,speed_sp=spd,stop_action='hold')
    lm.wait_while('running')
    rm.wait_while('running')
    sm(0.5)

def reset_pos() :
	lm.position = 0
	rm.position = 0

sL = 0; sR = 0
def print_pos(op=1) :
	global sL, sR
	if op == 1 :
		print('%5d %5d' % (lm.position, rm.position), end='\t')
    sL += lm.position; sR += rm.position
	return (lm.position, rm.position)
#####align_func###########################################################################################
def align(op='R') :
	while True :
		if lc.value() < TH:
			if rc.value() < TH:
				lm.run_forever(speed_sp=0)
				rm.run_forever(speed_sp=0)
				break
			else:
				lm.run_forever(speed_sp=0)
				rm.run_forever(speed_sp=-100)
		else:
			if rc.value() < TH:
				lm.run_forever(speed_sp=-100)
				rm.run_forever(speed_sp=0)
			else:
				lm.run_forever(speed_sp=-100)
				rm.run_forever(speed_sp=-100)
	sm(1)
	reset_pos()
	mv(30,30,100)


def vertical_align() :
	mv(60,60,100)
	lcVal=lc.value(); rcVal=rc.value(); mcVal=mc.value()
	print('lcVal ',lcVal,', rcVal ', rcVal, ', mcVal ', mcVal)
	reset_pos()
	if mc.value() != 1 :
		current_time = time()
		print('out of line')
		while time()-current_time<=1:
			if mc.value() == 1:
				outline = 'left'
				break
			lm.run_forever(speed_sp=100)
			rm.run_forever(speed_sp=-100)
		(a, x) = print_pos()
		while lm.position >= 0 :
			lm.run_forever(speed_sp=-100)
			rm.run_forever(speed_sp=100)
		sm(1)
		reset_pos()
		current_time = time()
		while time()-current_time<=1:
			if mc.value() == 1:
				outline = 'right'
				break
			lm.run_forever(speed_sp=-100)
			rm.run_forever(speed_sp=100)
		(x, b) = print_pos()
		while rm.position >= 0 :
			lm.run_forever(speed_sp=100)
			rm.run_forever(speed_sp=-100)
		sm(1)
		diff = a - b
		if diff > 10 :
			print('# shift right, To the left ')
			print(abs(diff))
			mv(0,140)
			reset_pos()
			mv(140,0)
			
		elif diff <= 10 :
			print('# shift left, To the right ')
			mv(140,0)
			reset_pos()
			mv(0,140)
		align()
		return
   
	while mc.value() != 6 :
		lm.run_forever(speed_sp=100)
		rm.run_forever(speed_sp=-100)
	(a, x) = print_pos()
	while lm.position >= 0 :
		lm.run_forever(speed_sp=-100)
		rm.run_forever(speed_sp=100)
	sm(1)

	reset_pos()
	while mc.value() != 6 :
		lm.run_forever(speed_sp=-100)
		rm.run_forever(speed_sp=100)
	(x, b) = print_pos()
	while rm.position >= 0 :
		lm.run_forever(speed_sp=100)
		rm.run_forever(speed_sp=-100)
	sm(1)

	diff = a - b
	if diff > -10 and diff <= 10 :
		print('OK')
	elif diff <= -10 :
		print('# shift right, To the left ')
		print(abs(diff))
		if diff < -80 :
			mv(0,160)
			reset_pos()
			mv(160,0)
		else :
			mv(0,80)
			reset_pos()
			mv(80,0)
	elif diff > 10 :
		print('# shift left, To the right ')
		if diff > 80 :
			mv(80,0)
			reset_pos()
			mv(0,80)
		else :
			mv(80,0)
			reset_pos()
			mv(0,80)
	align()
#####func_to_run###########################################################################################
def fw(d) :
	lm.position = 0
	rm.position = 0
	while True :
		diff = (lm.position - rm.position) * 10
		lm.run_forever(speed_sp=fwspeed-diff)
		rm.run_forever(speed_sp=fwspeed+diff)
		if lm.position >= d:	# 540
			break
	sm(1)


def until_kline() :
	while True :
		if lc.value() < TH:
			if rc.value() < TH:
				lm.run_forever(speed_sp=0)
				rm.run_forever(speed_sp=0)
				break
			else:
				lm.run_forever(speed_sp=0)
				rm.run_forever(speed_sp=fwspeed)
		else:
			if rc.value() < TH:
				lm.run_forever(speed_sp=fwspeed)
				rm.run_forever(speed_sp=0)
			else:
				lm.run_forever(speed_sp=fwspeed)
				rm.run_forever(speed_sp=fwspeed)
	sm(0.2)


def until_wline() :
	while True :
		if lc.value() > TH:
			if rc.value() > TH:
				lm.run_forever(speed_sp=0)
				rm.run_forever(speed_sp=0)
				break
			else:
				lm.run_forever(speed_sp=0)
				rm.run_forever(speed_sp=100)
		else:
			if rc.value() > TH:
				lm.run_forever(speed_sp=110)
				rm.run_forever(speed_sp=0)
			else:
				lm.run_forever(speed_sp=100)
				rm.run_forever(speed_sp=100)
	sm(0.2)

def forward():
	until_kline()
	print_pos()
	reset_pos()
	sm(0.5)
	i1 = colors[mc.value()]
	until_wline()	
	sm(1)
	i2 = colors[mc.value()]
	mv(48,48,100)
	o1 = colors[mc.value()]
	if o1 == 'R' or o1 == 'Y':
		mc.mode = 'COL-REFLECT'
		o2 = mc.value()
		sm(0.5)
		if o2 < 70 :
			o1 = 'R'
			print(str(o2))
		else :
			o1 = 'Y'
		mc.mode = 'COL-COLOR'
	if p != '00' :
		print(o1, i2, end='')
		col[p] = str(o1 + i2)
		if s[p] == col[p] :
			print(' succ')
		else :
			print(' fail')
	else :
		print()

def drop(d,spd=200):
    mv(400,400)
    print("drop")
    dm.run_to_rel_pos(position_sp=d,speed_sp=spd,stop_action='hold')
    dm.wait_while('running')
    sm_for_dm(0.5)
    mv(-200,-200)
    align()
  
def run(c, p) :
	if c == 'F' :
		forward()
	elif c == 'V' :
		vertical_align()
	elif c == 'L' :
		mv(35,35)
		mv(-180,180)
		align()
		mv(45,45)
		vertical_align()
		forward()
	elif c == 'R' :
		mv(35,35)
		mv(180,-180)
		align()
		mv(45,45)
		vertical_align()
		forward()
	elif c == 'ST' :
		fw(500)
	elif c == 'RT' :
		mv(850, 850)
	elif c == 'RR' :
		mv(80,80)
		mv(200,-200)
	elif c == 'GI' :
		mv(1795, 1795)
	elif c == 'A' :
		align()
	elif c == 'LST' :
		mv(80,80)
		mv(179,-179)
	elif c == 'RCT' :
		lc.mode = 'COL-COLOR'
		mv(0,165)
		getImColor()
	elif c == 'RCB' :
		mv(0,-165)
		lc.mode = 'COL-REFLECT'

def run_lv2():
    Beep()
    sm(3)
    rcol='R'
    input('press enter to go')
  
    while lc.value() > 50:
        lm.run_forever(speed_sp=200)
        rm.run_forever(speed_sp=200)
    
    reset_pos()
    Sound.speak('do chak').wait()
    sm(0.5)
    mv(50,50)  
    mv(0,210)
    reset_pos()
    lc.mode='COL-REFLECT'
    if lc.value()>10 and lc.value()<40:
        rcol='B'
    elif lc.value()>90 and lc.value()<110:
        rcol='Y'
    elif lc.value()>60 and lc.value()<80:
        rcol='R'
    sm(1.0)
    reset_pos()
    mv(-300,-300)
    mv(650,0)  

def run_lv3(c,i=99) :
    blank=['B2','B3','C2','C3','D2','D3','E2','E3','F2','F3']
    if c == 'D':
        drop(74)
    else:
    if path[cnt]==path[-1]:
        print('end')
    else:
        if path[cnt+1] not in blank:
            run(c,path[cnt])
        else:
            if c == 'F':
                mv(300,300)
          
        if c == 'L':
            mv(35,35)
            mv(-180,180)
            mv(300,300)
            sm(1.0)
      		
        if c == 'R':
            mv(35,35)
            mv(-180,180)
            mv(300,300)
            sm(1.0)
#####calcul_path###########################################################################################
def colpermutation():
    per = itertools.permutations(['R','G','B','Y'])
    for i in per:
        colperlist.append(i)

def storeinfo(sel):
    for key in col.keys():
        if sel == col[key][1]:
            store[col[key][0]].append(str(key))

def calcDis(w,x,y,z):
    a=[w,x,y,z]
    b=[]
    for k in a:
        k=list(k)
        k[0]=ord(k[0])-ord('A')+1
        k[1]=int(k[1])
        b.append(k)
    ways = itertools.permutations([0,1,2,3])
    dist=99

    for way in ways:
        temp=0
        temp+= abs(b[way[0]][0]-1) + abs(b[way[0]][1]-1)

        for t in range(1,4):
            temp+= abs(b[way[t]][0]-b[way[t-1]][0]) + abs(b[way[t]][1]-b[way[t-1]][1])

        temp+= abs(7-b[way[3]][0]) + abs(5-b[way[3]][1])
        if temp<dist:
            dist = temp
            sway = way
    f=[]
    for w in sway:
        f.append(a[w])

    return [dist,f]

def calcLoc(sel):
    storeinfo(sel)
    minlist=[100,[]]
    for i in colperlist:
        for w in store[i[0]]:
            for x in store[i[1]]:
                for y in store[i[2]]:
                    for z in store[i[3]]:
                        tlist=calcDis(w,x,y,z)
                        if tlist[0]<minlist[0]:
                            minlist=tlist.copy()
    return minlist

def calcPath(loc):
    node=loc[1]
    path=[]
    tx='A'
    ty='1'
    i=0
    while True:
        path.append(tx+ty)
        if tx+ty==node[-1]:
            if 'G' == tx:
                while True:
                    if 5 == int(ty):
                        break
                    else:
                        ty = chr(ord(ty)+1)
                    path.append(tx+ty)
            else:
                tx=chr(ord(tx)+1)
            break
        elif node[i][0] == tx:
            while True:
                if int(node[i][1]) == int(ty):
                    i+=1
                    break
                else:
                    ty = chr(ord(ty)+1)
                path.append(tx+ty)
        else:
            tx=chr(ord(tx)+1)

    return sorted(list(set(path)))

def pathToOrder(path,loc):
    order=[]
    heading = 'r'
    head
    for x in range(len(path)):
        head.append(heading)
        if path[x] in loc:
          order.append('D')
        if path[x]==path[-1]:
            if heading == 'r':
              order.append('F')
            if heading =='d':
              order.append('L')
        elif path[x][1] == path[x+1][1]:
            if heading =='r':
                order.append('F')
            if heading =='d':
                order.append('L')
                heading ='r'
        elif path[x][0] == path[x+1][0]:
            if heading =='d':
                order.append('F')
            if heading =='r':
                order.append('R')
                heading ='d'

    return order,head
#####run_the_program################################################################################
Sound.speak('si jak').wait()
for c, p in t :
	run(c, p)
run_lv2()
print(order)
cnt=0
for i in range(len(order)):
  p='00'
  if order[i]=='D':
    run_lv3(order[i])
    continue
  run_lv3(order[i],cnt)
  cnt+=1
colpermutation()
lcd=Screen()
sel=rcol
print(sel)
loc = calcLoc(sel)
print(loc)
path = calcPath(loc)
print(path)
order,head = pathToOrder(path,loc[1])
print(order)
################################################################################################