RUN=True
NOP=10
SPE=20
S_Data=[]
for j in range(0,SPE+1):
    S_Data.append([])

def ADD():
    location=0
    progress=True
    print("Adding patient")
    try:
        spec=int(input("Specialization (Enter number from 1 to 20): "))
        name=str(input("Enter name: "))
        status=int((input("Status (0 normal/1 urgent/2 super urgent): ")))
        if spec not in range(1,SPE+1) or status not in range(0,3):
            print("stick to the determined range, please.")
            ADD()
    except:
        print("Enter input as requested,please.")
        ADD()
    if progress==True:
         if len(S_Data[spec])>=NOP:
              print("NO place in specializtion "+str(spec))
         else:
             if len(S_Data[spec])==0 or location==len(S_Data[spec]):
                 S_Data[spec].append([name,status])
             else:
                 try:
                     for key in S_Data[spec]:
                         s=key[1]
                         if s>=status:
                             location+=1
                         else:
                             break
                     S_Data[spec].insert(location,[name,status])
                 except:
                     print("Item already there.")
         progress=False

def DATA():
    exist=True
    for i in range(0,SPE+1):
        if len(S_Data[i])!=0:
            print("Specialization "+str(i)+" : There are "+str(len(S_Data[i]))+" patients.")
            for key in range(0,len(S_Data[i])):
                if S_Data[i][key][1]==0:
                     Status="Normal"
                elif S_Data[i][key][1]==1:
                     Status="urgent"
                elif S_Data[i][key][1]==2:
                     Status="super urgent"
                print("Patient: "+S_Data[i][key][0]+" is "+Status)
            exist=False
    if exist==True:
         print("No Data in the system")

def Enter(S):
      if len(S)==0:
             print("There are no patients. Get some rest,Doctor.")
      else:
          print(S[0][0]+",Please go with the doctor.")
          S.remove(S[0])
      return False

def Enter_next():
    run=True
    try:
       spec=int(input("Enter specialization (from 1 to 20): "))
       if spec not in range(1,SPE+1):
           print("Enter a number from the determined range, please.")
           run=Enter_next()
    except:
        print("please, Enter input as requested.")
        run=Enter_next()
    if run==True:
            run=Enter(S_Data[spec])
    return False

def search(lis):
       name=str(input("Enter patient name: "))
       count=len(lis)
       for i in range(0,len(lis)):
           count-=1
           if lis[i][0]==name:
              print("Patient found and deleted")
              lis.remove(lis[i])
              break
           if count==0:
              print("Patient not found")
       return False

def Remove():
    start=True
    try:
       spec=int(input("Enter specialization (from 1 to 20): "))
       if spec not in range(1,SPE+1):
           print("Enter a number from the determined range, please.")
           start=Remove()
    except:
        print("please, Enter input as requested.")
        start=Remove()
    if start==True:
         start=search(S_Data[spec])
    return False

while(RUN==True):
    print("program options: ")
    print("1)Add new patient")
    print("2)Print all patients")
    print("3)Get next patient")
    print("4)Remove a leaving patient")
    print("5)End the program")
    try:
        O_number=int(input("Enter your choice (From 1 to 5): "))
    except:
        print("Enter input as requested,please.")
        continue
    if O_number not in range(1,6):
        print("Please, stick to the range of numbers.")
        continue
    else:
         if O_number==1:
             ADD()
         elif O_number==2:
             DATA()
         elif O_number==3:
             Enter_next()
         elif O_number==4:
             Remove()
         elif O_number==5:
             print("The sytem is turning Off.")
             RUN=False
