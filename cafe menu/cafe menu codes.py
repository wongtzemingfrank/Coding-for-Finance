import datetime

items_category = {"coffee":["EP", "IC", "LT"], "tea":["EG", "SG", "CP"], "dessert":["BG", "SP", "CC"]}


MENU = {"EP":{"fullname": "Espresso", "price":5.50, "discountable":"yes"}, "IC":{"fullname": "Iced Coffee", "price":4.95, "discountable":"no"}, "LT":{"fullname": "Latte", "price":4.95, "discountable":"no"}
        , "EG":{"fullname": "Earl Grey", "price":4.50, "discountable":"no"}, "SG":{"fullname": "Sakura Green Tea", "price":5.00, "discountable":"yes"}, "CP":{"fullname": "Chamomole Peppermint Tea", "price":5.00, "discountable":"no"},
        "BG":{"fullname": "Brownie Gelato", "price":4.95, "discountable":"yes"}, "SP":{"fullname": "Stawberry Pudding", "price":4.25, "discountable":"no"}, "CC":{"fullname": "Chocolate Cheesecake", "price":5.90, "discountable":"yes"}}

MENU_copy = {"EP":{"fullname": "Espresso", "price":5.50, "discountable":"yes"}, "IC":{"fullname": "Iced Coffee", "price":4.95, "discountable":"no"}, "LT":{"fullname": "Latte", "price":4.95, "discountable":"no"}
        , "EG":{"fullname": "Earl Grey", "price":4.50, "discountable":"no"}, "SG":{"fullname": "Sakura Green Tea", "price":5.00, "discountable":"yes"}, "CP":{"fullname": "Chamomole Peppermint Tea", "price":5.00, "discountable":"no"},
        "BG":{"fullname": "Brownie Gelato", "price":4.95, "discountable":"yes"}, "SP":{"fullname": "Stawberry Pudding", "price":4.25, "discountable":"no"}, "CC":{"fullname": "Chocolate Cheesecake", "price":5.90, "discountable":"yes"}}

cheaper_item_description_list = []

sales_report_dict = {"EP":{"fullname": "Espresso", "price":5.50, "qty": 0, "discountable":"yes"}, "IC":{"fullname": "Iced Coffee", "price":4.95,"qty": 0, "discountable":"no"}, "LT":{"fullname": "Latte", "price":4.95,"qty": 0, "discountable":"no"}
        , "EG":{"fullname": "Earl Grey", "price":4.50,"qty": 0, "discountable":"no"},
                     "SG":{"fullname": "Sakura Green Tea", "price":5.00,"qty": 0, "discountable":"yes"}, "CP":{"fullname": "Chamomole Peppermint Tea", "price":5.00,"qty": 0, "discountable":"no"},
        "BG":{"fullname": "Brownie Gelato", "price":4.95,"qty": 0, "discountable":"yes"}, "SP":{"fullname": "Stawberry Pudding", "price":4.25, "qty": 0, "discountable":"no"},
                     "CC":{"fullname": "Chocolate Cheesecake", "price":5.90, "qty": 0, "discountable":"yes"}}


def return_cheapest_price(dictionary):          #Put the dictionary data in to recieve the cheapest price
    cheapest = 100
    for item, description in dictionary.items():
        if description["price"] < cheapest:
            cheapest = description["price"]
    return cheapest


shoppingCart = {"EP":0, "IC":0, "LT":0,         #0 represents quantity
                    "EG":0, "SG":0, "CP":0,
                    "BG":0, "SP":0, "CC":0}
shoppingPrice = 0

def main():
    print("==================================")
    system()

    if choice == "1":
        print("Cafe items by category:")
        print()
        print("Coffee Options:")
        for item, description in MENU.items():
            if item in items_category["coffee"]:
                print("({0})  {1:<25}  ({2:<5}) discountable: {3:<6}".format(item, description["fullname"], description["price"], description["discountable"]))
        print()
        print("Tea Options:")
        for item, description in MENU.items():
            if item in items_category["tea"]:
                print("({0})  {1:<25}  ({2:<5}) discountable: {3:<6}".format(item, description["fullname"], description["price"], description["discountable"]))
        print()
        print("Dessert Options:")
        for item, description in MENU.items():
            if item in items_category["dessert"]:
                print("({0})  {1:<25}  ({2:<5}) discountable: {3:<6}".format(item, description["fullname"], description["price"], description["discountable"]))



    elif choice == "2":
        print("Cafe items alphabetically:")
        print()
        menu_list = []
        for item, description in MENU.items():
            menu_list.append(description["fullname"])
        menu_list.sort()
        for fullname in menu_list:
            for item, description in MENU.items():
                if description["fullname"] == fullname:
                    print("({0})  {1:<25}  ({2:<5}) discountable: {3:<6}".format(item, description["fullname"], description["price"], description["discountable"]))
        

    elif choice == "3":
        print("Cafe items by price (ascending)")
        print()
        flag3 = True
        while flag3:
        #find the cheaptest in MENU_copy
            cheapest = return_cheapest_price(MENU_copy)

            for item, description in MENU.items():
                if description["price"] == cheapest:
                    try:
                        MENU_copy.pop(item)
                    except KeyError:
                        continue
    
        #append ones with cheapest price tag to CIDL
            for item, description in MENU.items():
                if description["price"] == cheapest:
                    cheaper_item_description_list.append({item:description})

        #check if we have reached the end
            if len(MENU_copy) == 0:
                flag3 = False
        for element in cheaper_item_description_list:
            name = list(element.keys())[0]
            fullname = list(element.values())[0]["fullname"]
            price = list(element.values())[0]["price"]
            discountable = list(element.values())[0]["discountable"]
            print("({0})  {1:<25}  ({2:<5}) discountable: {3:<6}".format(item, fullname, price, discountable))
        
    elif choice == "4":
        choice4()

    elif choice == "5":
        choice5()

    elif choice == "6":
        choice6()

    elif choice == "7":
        choice7()
    elif choice == "8":
        choice8()
    elif choice == "0":
        global flag
        print("Thank you come again!")
        flag = False

def system():
    global choice
    menusystem = ["1. Cafe items by category", "2. Cafe items alphabetically", "3. Cafe items by price (ascending)",
                  "4. Add items to shopping cart", "5. View items in shopping cart", "6. Remove item from shopping cart", "7. Checkout/Payment",
                  "8. Supermarket sales summary report", "0. Exit"]
    count = 0
    while count < len(menusystem):
            print(menusystem[count])
            count += 1

    choice = input("Please select from following choices to continue: ")
    print("==================================")

def choice4():
    global itemchoices
    global shoppingPrice
    print("Please select items in Uppercase & Press 0 to exit")
    count = 0
    while True:
        itemchoices = input("Choice {0}: ".format(count+1))
        itemchoices_upper = itemchoices.upper()
        
        if (itemchoices_upper in MENU) and (itemchoices_upper != "0"):
            itemchoices_quantity = int(input("Please input the quantity: "))
        
        
        if itemchoices_upper not in MENU and (itemchoices_upper != "0"):
            print("Invalid Option")
        else:
            count += 1

        
        
        if itemchoices in MENU:
            if itemchoices_upper == "EP":
                shoppingCart["EP"] += itemchoices_quantity
                
            if itemchoices_upper == "IC":
                shoppingCart["IC"] += itemchoices_quantity
                
            if itemchoices_upper == "LT":
                shoppingCart["LT"] += itemchoices_quantity
                         
            if itemchoices_upper == "EG":
                shoppingCart["EG"] += itemchoices_quantity
                
            if itemchoices_upper == "SG":
                shoppingCart["SG"] += itemchoices_quantity
                
            if itemchoices_upper == "CP":
                shoppingCart["CP"] += itemchoices_quantity
                
            if itemchoices_upper == "BG":
                shoppingCart["BG"] += itemchoices_quantity
                
            if itemchoices_upper == "SP":
                shoppingCart["SP"] += itemchoices_quantity
                
            if itemchoices_upper == "CC":
                shoppingCart["CC"] += itemchoices_quantity
                

        if itemchoices == "0":
            break

def choice5():
    print("Items in Shopping Cart:")
    for item, quantity in shoppingCart.items():
        if quantity !=0:
            if item == "EP":
                print("Espresso with a quantiy of " + str(quantity) + ".")
            elif item == "IC":
                print("Iced Coffee with a quantiy of " + str(quantity) + ".")
            elif item == "LT":
                print("Latte with a quantiy of " + str(quantity) + ".")
            elif item == "EG":
                print("Earl Grey with a quantiy of " + str(quantity) + ".")
            elif item == "SG":
                print("Sakura Green Tea with a quantiy of " + str(quantity) + ".")
            elif item == "CP":
                print("Chamomile Peppermint Tea with a quantiy of " + str(quantity) + ".")
            elif item == "BG":
                print("Brownie Gelato Espresso with a quantiy of " + str(quantity) + ".")
            elif item == "SP":
                print("Strawberry Pudding Espresso with a quantiy of " + str(quantity) + ".")
            elif item == "CC":
                    print("Chocolate Cheesecake Espresso with a quantiy of " + str(quantity) + ".")

def choice6():
    print("Please select items to remove in Uppercase & 0 to exit")
    count = 0
    while True:
        itemchoices = input("Choice {0}: ".format(count+1))
        itemchoices_upper = itemchoices.upper()
        count += 1

        if (itemchoices_upper not in shoppingCart) and (itemchoices_upper != "0"):
            print("Invalid Option")
        elif (itemchoices_upper in shoppingCart) and (itemchoices_upper != "0"):
            quantity_to_remove = int(input("Please indicate the quantity to be removed for selected item: "))

        if itemchoices == "0":
            break
        
        if shoppingCart[itemchoices] >= quantity_to_remove:
            shoppingCart[itemchoices] -= quantity_to_remove
        else:
            print("Quantity to remove is greater than what you have, that is" + str(shoppingCart[itemchoices]) + ".  Please select again.")
        
def choice7():
    print("Checkout/Payment:")
    member = input("Are you a member? (Y/N): ")
    print("{0:^40}{1:^17}{2:^10}".format("item", "Quantity", "Amt"))
    for item1, quantity in shoppingCart.items():
        if quantity == 0:
            continue
        else:
            
            for item2, description in MENU.items():
                if item1 == item2:
                    item_price = description["price"]                
                    print("{0:^40}{1:^17}{2:^10}".format(item2, str(quantity), str(quantity*float(item_price))))

    total_cost = 0
    for item1, quantity in shoppingCart.items():
        for item2, description in MENU.items():
            if quantity != 0:
                total_cost += quantity*description["price"]
    
        
    print("GST total:      " + str(round(0.07*total_cost, 2)))
    print("Subtotal         " + str(total_cost))

    if (member == "Y") or (member == "y"):
        
        print()
        total_cost_with_discount = 0
        for item1, quantity in shoppingCart.items():
            for item2, description in MENU.items():
                if quantity != 0:
                    if description["discountable"] == "yes":
                        total_cost_with_discount += 0.85*description["price"]*quantity
                    elif description["discountable"] == "no":
                        total_cost_with_discount += description["price"]*quantity
        print("Discount:         -" + str(total_cost-total_cost_with_discount))
        print("Total with 15% off: ${0:.2f}".format(total_cost_with_discount))
        print()

    elif (member == "N") or (member == "n"):
        print()
        print("Total price w/o discount: ${0:.2f}".format(total_cost))
        print()
    print()
    confirmation = input("confirm payment? ")
    if confirmation == "y":
        print("Thanks, please come again")
        for item, quantity in shoppingCart.items():       #clear cart
            sales_report_dict[item]["qty"] += quantity
            shoppingCart[item] = 0
    elif confirmation == "n":
        pass
        
        
def choice8():
    print("date: " + str(datetime.datetime.today()))        #datetime module to get current
    print()
    print("{0:<5}{1:<30}{2:<10}{3:<25}{4:<8}".format("name", "fullname", "price", "qty sold", "total"))
    total_earning = 0
    for item, description in sales_report_dict.items():
        print("{0:<5}{1:<30}{2:<10}{3:<25}{4:<8}".format(item, description["fullname"], description["price"], description["qty"], str(int(description["qty"])*description["price"])))
        total_earning += int(description["qty"])*description["price"]
    print()
    print("Total earning: " + str(total_earning))

print("Welcome to Cafe")
flag = True
while flag:
    main()


