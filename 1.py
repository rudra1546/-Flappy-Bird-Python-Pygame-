def set_operation():

    set1 ={1,2,3,4}
    print("Direct Initilization :",set1)

    set2 = set()
    n=int(input("How many elements to add to set2:"))
    for i in range(n):
        val = int(input(f"Enter element {i+1}:"))
        set2.add(val)

    print("Empty set then add values:",set2)

    lst=list(map(int,input("Enter list element saparated by space: ").split()))
    set3=set(lst)
    print("From a list :",set3)

    set4=set(set1)
    print("From another set:",set4)

    start=int(input("Enter Starting Range :"))
    end=int(input("Enter Ending Range :"))
    set5= set(range(start,end+1))
    print("From range :",set5)

    set1.update(set2)
    print("Set1 after update with set2 :",set1)

    print("Iterating Set3 : ",end=" ")
    for elem in set3:
        print(elem,end=" ")
    print()

    if set3:
        val = int(input("Enter element to remove from set3: "))
        if val in set3:
            set3.remove(val)
            print(f"After remove({val}):", set3)
        else:
            print(f"{val} not in set3, remove() would cause error")
    val = int(input("Enter element to discard from set3: "))
    set3.discard(val)
    print(f"After discard({val}):", set3)

set_operation()