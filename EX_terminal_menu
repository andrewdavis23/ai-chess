MENU_STR = """
    #-----------------#
    |  1 - func1      |
    |  2 - func2      |
    |  0 - exit       |
    #-----------------#
    > """

def func1():
    print("func1")

def func2():
    print("func2")

menu_actions = {
    1: func1,
    2: func2
}

while True:
    try:
        x = int(input(MENU_STR))
    except ValueError:
        print("Enter a number.")
        continue

    if x == 0:
        break
    
    action = menu_actions.get(x)
    if action:
        action()
    else:
        print("Invalid selection.")
