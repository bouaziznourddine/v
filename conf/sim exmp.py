import time,os,random
from netlogopy2.netlogopy import *
from conf.func import *
from conf.profiles import *
os.system('cls')

if __name__ == "__main__" :
    dest = os.path.dirname(__file__)
    netlogo_home="C:/Program Files/NetLogo 6.2.2"
    model = os.path.dirname(__file__)+"\\netlogopy.nlogo"
    # n=run_netlogo(netlogo_home,model)
    n=run_netlogo(netlogo_home)

    # Resize world
    resize_world(n,0,70,0,55)
    # Change path fo image
    # path_image= os.path.dirname(__file__)+"/netlogopy.png"

    path_image = "D:/cphs2024/netlogopy.png"
    
    set_background(n,path_image)
    
    # Zn0=pyturtle(n,x=5,y=30,shape="infirmary",size_shape=4,color=15,name="Zn0",labelcolor=15,fields={"worker_encour":None,"libre":True})
    Zn1=pyturtle(n,x=15,y=35,shape="calling",size_shape=4,color=15,name="Zn1",labelcolor=15,fields={"worker_encour":None,"free":True})
    Zn2=pyturtle(n,x=25,y=35,shape="food",size_shape=4,color=15,name="Zn2",labelcolor=15,fields={"worker_encour":None,"free":True})
    Zn3=pyturtle(n,x=35,y=35,shape="house",size_shape=4,color=15,name="Zn3",labelcolor=15,fields={"worker_encour":None,"free":True})
    lzone = [ Zn1,Zn2,Zn3 ]

    stock0=pyturtle(n,x=5,y=10,shape="house",size_shape=4,color=15,name="stock0",fields={}) ; stock1=pyturtle(n,x=15,y=5,shape="house",size_shape=4,color=55,name="stock1",fields={}) ; stock2=pyturtle(n,x=25,y=5,shape="house",size_shape=4,color=55,name="stock2",fields={}) ; stock3=pyturtle(n,x=35,y=5,shape="house",size_shape=4,color=55,name="stock3",fields={}) ; stock4=pyturtle(n,x=45,y=5,shape="house",size_shape=4,color=55,name="stock4",fields={}) ; stock5=pyturtle(n,x=55,y=5,shape="house",size_shape=4,color=55,name="stock5",fields={}) ; 
    stockfinal=pyturtle(n,x=60,y=10,shape="house",size_shape=4,color=15,name="stockfinal",fields={}) 
   
    Ws5=pyturtle(n,x=55,y=15,shape="machineinsp",size_shape=4,color=55,name="Ws4",labelcolor=55,fields={"pt":1,"prd_encour":None,"stock":[],"stock_tr":stock5,"nextws":None,"worker_encour":None,"libre":True})
    Ws4=pyturtle(n,x=45,y=20,shape="machineinsp",size_shape=4,color=55,name="Ws4",labelcolor=55,fields={"pt":1,"prd_encour":None,"stock":[],"stock_tr":stock4,"nextws":Ws5,"worker_encour":None,"libre":True})
    Ws3=pyturtle(n,x=35,y=15,shape="machine4",size_shape=4,color=55,name="Ws3",labelcolor=55,fields={"pt":4,"prd_encour":None,"stock":[],"stock_tr":stock3,"nextws":Ws4,"worker_encour":None,"libre":True})
    Ws2=pyturtle(n,x=25,y=20,shape="machine3",size_shape=4,color=55,name="Ws2",labelcolor=55,fields={"pt":2,"prd_encour":None,"stock":[],"stock_tr":stock2,"nextws":Ws3,"worker_encour":None,"libre":True})
    Ws1=pyturtle(n,x=15,y=15,shape="machine2",size_shape=4,color=55,name="Ws1",labelcolor=55,fields={"pt":4,"prd_encour":None,"stock":[],"stock_tr":stock1,"nextws":Ws2,"worker_encour":None,"libre":True})
    Ws0=pyturtle(n,x=5,y=20,shape="machine",size_shape=4,color=15,name="Ws0",labelcolor=15,fields={"pt":3,"prd_encour":None,"stock":[],"stock_tr":stock0,"nextws":Ws1,"worker_encour":None,"libre":True})

    street( n,fromm=Ws0,too=Ws1,label=" ",labelcolor=35,color=35,shape="aa",thickness=0.5),street( n,fromm=Ws0,too=Ws1,label=" ",labelcolor=35,color=35,shape="aa",thickness=0.5),street( n,fromm=Ws1,too=Ws2,label=" ",labelcolor=35,color=35,shape="aa",thickness=0.5),street( n,fromm=Ws2,too=Ws3,label=" ",labelcolor=35,color=35,shape="aa",thickness=0.5),street( n,fromm=Ws3,too=Ws4,label=" ",labelcolor=35,color=35,shape="aa",thickness=0.5),street( n,fromm=Ws4,too=Ws5,label=" ",labelcolor=35,color=35,shape="aa",thickness=0.5)

    wrk0=pyturtle(n,x=5,y=5,shape="person_0",size_shape=4,color=55,name="person_0",labelcolor=55,fields={"assignment":Ws0 ,"nht":0,"fatigue":1,"experience":1,"profile":profile_0,"zon_now":Ws0,"numprd":0,"def_vit":lambda wrk=None,tem=0,numprd=0 :vit_Wkr0(wrk,tem,numprd)})
    wrk1=pyturtle(n,x=5,y=5,shape="person_1",size_shape=4,color=55,name="person_1",labelcolor=55,fields={"assignment":Ws1 ,"nht":0,"fatigue":1,"experience":1,"profile":profile_1,"zon_now":Ws1,"numprd":0,"def_vit":lambda wrk=None,tem=0,numprd=0 :vit_Wkr1(wrk,tem,numprd)})
    wrk2=pyturtle(n,x=5,y=5,shape="person_2",size_shape=4,color=55,name="person_2",labelcolor=55,fields={"assignment":Ws2 ,"nht":0,"fatigue":1,"experience":1,"profile":profile_2,"zon_now":Ws2,"numprd":0,"def_vit":lambda wrk=None,tem=0,numprd=0 :vit_Wkr2(wrk,tem,numprd)})
    wrk3=pyturtle(n,x=5,y=5,shape="person_3",size_shape=4,color=55,name="person_3",labelcolor=55,fields={"assignment":Ws3 ,"nht":0,"fatigue":1,"experience":1,"profile":profile_0,"zon_now":Ws3,"numprd":0,"def_vit":lambda wrk=None,tem=0,numprd=0 :vit_Wkr3(wrk,tem,numprd)})
    wrk4=pyturtle(n,x=5,y=5,shape="person_4",size_shape=4,color=55,name="person_4",labelcolor=55,fields={"assignment":Ws4 ,"nht":0,"fatigue":1,"experience":1,"profile":profile_1,"zon_now":Ws4,"numprd":0,"def_vit":lambda wrk=None,tem=0,numprd=0 :vit_Wkr4(wrk,tem,numprd)})
    wrk5=pyturtle(n,x=5,y=5,shape="person_4",size_shape=4,color=55,name="person_4",labelcolor=55,fields={"assignment":Ws5 ,"nht":0,"fatigue":1,"experience":1,"profile":profile_2,"zon_now":Ws5,"numprd":0,"def_vit":lambda wrk=None,tem=0,numprd=0 :vit_Wkr5(wrk,tem,numprd)})

    pr01=pyturtle(n,x=5,y=8,shape="p_robot00",size_shape=4,color=55,name="",labelcolor=55,fields={"Sj":0,"pt":0,"ws_now":None,"ws_last":None,"ws_next":None,"active":True})


    pas_tick = 1
    speed = 0
    EOS = 2400

    
    lsprod = [pr01]
    Ws0.stock=lsprod
    lsWs=[Ws0,Ws1,Ws2,Ws3,Ws4,Ws5]
    lsWkr=[wrk0,wrk1,wrk2,wrk3,wrk4,wrk5]
    lprofile=[profile_0,profile_1,profile_2]



    v= int(EOS/pas_tick)
    def run (lp=[],lf=[],le=[],lv=[]):
        cmax = 0
        NPF=0

        i=0
        for wr in lsWkr :
            profile=lprofile[lp[i]]
            if lv != []:
                profile.vitesse = lv[i]
            if le != []:
                profile.alf_exp = le[i]
            if lf != []:
                profile.alf_ftig = lf[i]
            wr.profile = profile
            wr.move_to(wr.assignment)
            wr.assignment.worker_encour=wr
            wr.fd(5)
            i+=1
        def update_prd(prd):
            
            return  prd
        for i in range(1,v):
            # print("tick  = ",i*pas_tick )
            time.sleep(speed)
            random.shuffle(lsWs)
            for ws in lsWs :
                temp=i*pas_tick ;  pr=False
                for prd in lsprod :
                    update_prd(prd)
                    pass
                if ws.prd_encour == None :
                    if ws.stock :
                        ws.prd_encour = random.choice(ws.stock) 
                        ws.stock.remove(ws.prd_encour)
                        ws.prd_encour.move_to(ws)
                        ws.prd_encour.Sj=( (i-1) * pas_tick )
                        ws.prd_encour.pt=( (i-1) * pas_tick )
                if ws.prd_encour and ws.worker_encour :
                    wrkr=ws.worker_encour
                    numprd=wrkr.numprd

                    rest=  pas_tick * wrkr.def_vit(wrkr,temp,numprd) 
                    ws.prd_encour.pt += rest
                    wrkr.nht+=1
            for ws in lsWs :
                if ws.prd_encour and ws.worker_encour :
                    if ( ws.prd_encour.pt - ws.prd_encour.Sj ) >= ws.pt :
                        ws.worker_encour.numprd += 1
                        if ws.nextws :
                            ws.prd_encour.move_to(ws.nextws.stock_tr)
                            ws.prd_encour.fd(3)
                            ws.nextws.stock.append(ws.prd_encour)
                            ws.prd_encour= None
                            pass
                        else :
                            NPF+=1
                            ws.prd_encour.move_to(stockfinal)
                            ws.prd_encour.fd(3)
                            ws.prd_encour = None
            if Ws0.prd_encour == None:
                lsprod.append(pyturtle(n,x=5,y=8,shape="p_robot00",size_shape=4,color=55,name="",labelcolor=55,fields={"Sj":0,"pt":0,"ws_now":None,"ws_last":None,"ws_next":None,"active":True}))
            
            for wrk in lsWkr :
                nextzon = update_wk(wrk,lzone)
                if nextzon == 0 :
                    if wrk.zon_now != wrk.assignment :
                        wrk.move_to(wrk.assignment)
                        wrk.fd(5)
                        wrk.zon_now = wrk.assignment
                        wrk.assignment.worker_encour =  wrk
                else :
                    nextzon-=1
                    wrk.assignment.worker_encour =  None
                    wrk.zon_now = lzone[nextzon]
                    wrk.move_to(lzone[nextzon]) 
                    wrk.fd(5)
                pass
            l=[]
            for wr in lsWkr :
                l.append(wr.nht)   
            # print(l)
        # print("***********************************************")
        # print("***********  ","cmax = " ,int(cmax),"  ********")
        # print("***********  ","NPF = " ,int(NPF),"  ********")
        wrdntlgo="NPF :" + str(NPF)
        netlogoshow(n,wrdntlgo) 
        print("| ",lp," | ",lf," | ",le," | ",NPF)




    #  scénarios
    print( " ")
    print("--------------------------------------------------------------------------")
    p0=0 ; p1=1 ; p2=2  ;   f0=0 ; f1=0.001 ; f2=0.002  ;  e0=0 ; e1=0.1 ; e2=0.2
    print("|    punct             |      fatigue         |     experience       | NP ")
    print("--------------------------------------------------------------------------")
    run([ 1,2,2,0,0,2 ],[ 0.001,0.001,0,0,0,0 ],[ 0.2,0.2,0,0.2,0,0 ])


    run([ 1,2,2,0,2,2 ],[ 0.002,0,0,0,0,0 ],[ 0,0.1,0.1,0,0.1,0.2 ])

    print('termin : O ou N:')
    x = input()
    print('R : ' + x)
    n.close_model()


