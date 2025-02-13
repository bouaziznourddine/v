import random


p0=0 ; p1=1 ; p2=2  ;   f0=0 ; f1=0.001 ; f2=0.002  ;  e0=0 ; e1=0.1 ; e2=0.2
lp1=[p0,p1,p2]
lf1=[f0,f1,f2]
le1=[e0,e1,e2]
for i in range(30):
    vp0=random.choice(lp1);vp1=random.choice(lp1);vp2=random.choice(lp1);vp3=random.choice(lp1);vp4=random.choice(lp1);vp5=random.choice(lp1)
    vf0=random.choice(lf1);vf1=random.choice(lf1);vf2=random.choice(lf1);vf3=random.choice(lf1);vf4=random.choice(lf1);vf5=random.choice(lf1)
    ve0=random.choice(le1);ve1=random.choice(le1);ve2=random.choice(le1);ve3=random.choice(le1);ve4=random.choice(le1);ve5=random.choice(le1)
    print('run([',vp0,',',vp1,',',vp2,',',vp3,',',vp4,',',vp5,"],"'[',vf0,',',vf1,',',vf2,',',vf3,',',vf4,',',vf5,"],"'[',ve0,',',ve1,',',ve2,',',ve3,',',ve4,',',ve5,"])")
