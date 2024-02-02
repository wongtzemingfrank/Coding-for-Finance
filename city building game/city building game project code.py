import pandas as pd
import random as rd
import numpy as np
import os

#try excepts for all inputs
#different scoreboards for different layout_size
#check for anymore errors by gg thru all options

#disp = display, ref = reference, qty = quantity, box = the placing in the building layout, empty or not empty.

prk_score_dict = {0:0, 1:1, 2:3, 3: 8, 4: 16, 5: 22, 6:23, 7: 24,  8: 25}


##ref_layout_data = pd.DataFrame([["", "", "", ""],["", "", "", ""],      #pretend data
##                           ["", "", "", ""], ["", "", "", ""]])
##ref_layout_data = ref_layout_data.rename(columns={0: "A", 1:"B", 2:"C",3:"D"})

def ref_layout_data_fn():
    global ref_layout_data
    if start_building_qty == 8:
        ref_layout_data = pd.DataFrame([["", "", "", ""],["", "", "", ""],      #pretend data
                       ["", "", "", ""], ["", "", "", ""]])
        ref_layout_data = ref_layout_data.rename(columns={0: "A", 1:"B", 2:"C",3:"D"})

    elif start_building_qty == 9:
        ref_layout_data = pd.DataFrame([["", "", "", "", ""],["", "", "", "", ""],      #pretend data
                       ["","", "", "", ""], ["","", "", "", ""], ["","", "", "", ""]])
        ref_layout_data = ref_layout_data.rename(columns={0: "A", 1:"B", 2:"C",3:"D", 4:"E"})

    elif start_building_qty == 10:
        ref_layout_data = pd.DataFrame([["","", "", "", "", ""],["","", "", "", "", ""],      #pretend data
                       ["","","", "", "", ""], ["","","", "", "", ""], ["","","", "", "", ""], ["","","", "", "", ""]])
        ref_layout_data = ref_layout_data.rename(columns={0: "A", 1:"B", 2:"C",3:"D", 4:"E", 5:"F"})

    elif start_building_qty == 11:
        ref_layout_data = pd.DataFrame([["","","", "", "", "", ""],["","","", "", "", "", ""],      #pretend data
                       ["","","","", "", "", ""], ["","","","", "", "", ""], ["","","","", "", "", ""], ["","","","", "", "", ""], ["","","","", "", "", ""]])
        ref_layout_data = ref_layout_data.rename(columns={0: "A", 1:"B", 2:"C",3:"D", 4:"E", 5:"F", 6:"G"})

    elif start_building_qty == 12:
        ref_layout_data = pd.DataFrame([["","","","", "", "", "", ""],["","","","", "", "", "", ""],      #pretend data
                       ["","","","","", "", "", ""], ["","","","","", "", "", ""], ["","","","","", "", "", ""], ["","","","","", "", "", ""], ["","","","","", "", "", ""]])
        ref_layout_data = ref_layout_data.rename(columns={0: "A", 1:"B", 2:"C",3:"D", 4:"E", 5:"F", 6:"G", 7:"H"})



def start_building_qty_fn(start_building_qty_choice):
    global start_building_qty
    global ref_inventory

    if start_building_qty_choice == "4x4":
        start_building_qty = 8


    elif start_building_qty_choice == "5x5":
        start_building_qty = 9


    elif start_building_qty_choice == "6x6":
        start_building_qty = 10


    elif start_building_qty_choice == "7x7":
        start_building_qty = 11


    elif start_building_qty_choice == "8x8":
        start_building_qty = 12
    else:
        return "invalid"

    for key in ref_inventory.keys():
        ref_inventory[key] = start_building_qty
        
##    ref_inventory = {"bch" : start_building_qty, "fac": start_building_qty, "hse":start_building_qty, "shp":start_building_qty, "hwy":start_building_qty, "prk":start_building_qty, "mon":start_building_qty}

start_building_qty = 8
def revert_back_to_normal():
    global ref_inventory
    global start_building_qty
    start_building_qty = 8
    ref_inventory = {"bch" : start_building_qty, "fac": start_building_qty, "hse":start_building_qty, "shp":start_building_qty, "hwy":start_building_qty, "prk":start_building_qty, "mon":start_building_qty}
    
revert_back_to_normal()

def hall_of_fame_fn(layout_type):   #e.g of layout_type, 4x4, 5x5, 6x6, 7x7, 8x8
    if layout_type == "4x4":
        hall_of_fame = pd.read_csv("hall_of_fame_4.csv")
    elif layout_type == "5x5":
        hall_of_fame = pd.read_csv("hall_of_fame_5.csv")
    elif layout_type == "6x6":
        hall_of_fame = pd.read_csv("hall_of_fame_6.csv")
    elif layout_type == "7x7":
        hall_of_fame = pd.read_csv("hall_of_fame_7.csv")
    elif layout_type == "8x8":
        hall_of_fame = pd.read_csv("hall_of_fame_8.csv")
    else:
        return "invalid"
    hall_of_fame = hall_of_fame.replace(np.nan, '', regex=True)
    hall_of_fame.index = hall_of_fame.index + 1

    
    return hall_of_fame

def disp_layout():            #display the layout nicely for player to play proper
    global disp_all_choices_loop
    turn = 1
    for column in user_layout_data.columns:
        for box in user_layout_data.loc[:, column]:
            if box != "":
                turn += 1


    if start_building_qty == 8:
                
        if turn == 17:
            print("game ended!")
            print("You scored a total of " + str(points_calculate()))

            for row_index in range(0, 10):
                if points_calculate() > hall_of_fame_fn("4x4").iloc[row_index,1]:
                    player_name = input("Your name? ")
                    line = pd.DataFrame({"Player": player_name, "Score": points_calculate()}, index=[row_index])
                    break

            first_df = hall_of_fame_fn("4x4").iloc[:row_index]
            middle_df = line
            last_df = hall_of_fame_fn("4x4").iloc[row_index:]
            middle_last_df = pd.concat([middle_df,last_df])
            middle_last_df.index = middle_last_df.index + 1
            full_df = pd.concat([first_df, middle_last_df])
            full_df = full_df.drop(full_df.index[10])
            print(full_df)

            full_df.to_csv('hall_of_fame_4.csv', index=False)
            return_to_menu = input("Congrats! Returning to main menu, press and key and hit enter to continue...")
            main()

    elif start_building_qty == 9:
                
        if turn == 26:
            print("game ended!")
            print("You scored a total of " + str(points_calculate()))

            for row_index in range(0, 10):
                if points_calculate() > hall_of_fame_fn("5x5").iloc[row_index,1]:
                    player_name = input("Your name? ")
                    line = pd.DataFrame({"Player": player_name, "Score": points_calculate()}, index=[row_index])
                    break
                
            first_df = hall_of_fame_fn("5x5").iloc[:row_index]
            middle_df = line
            last_df = hall_of_fame_fn("5x5").iloc[row_index:]
            middle_last_df = pd.concat([middle_df,last_df])
            middle_last_df.index = middle_last_df.index + 1
            full_df = pd.concat([first_df, middle_last_df])
            full_df = full_df.drop(full_df.index[10])
            print(full_df)
            full_df.to_csv('hall_of_fame_5.csv', index=False)
            return_to_menu = input("Congrats! Returning to main menu, press and key and hit enter to continue...")
            main()
    elif start_building_qty == 10:
                
        if turn == 37:
            print("game ended!")
            print("You scored a total of " + str(points_calculate()))

            for row_index in range(0, 10):
                if points_calculate() > hall_of_fame_fn("6x6").iloc[row_index,1]:
                    player_name = input("Your name? ")
                    line = pd.DataFrame({"Player": player_name, "Score": points_calculate()}, index=[row_index])
                    break
                
            first_df = hall_of_fame_fn("6x6").iloc[:row_index]
            middle_df = line
            last_df = hall_of_fame_fn("6x6").iloc[row_index:]
            middle_last_df = pd.concat([middle_df,last_df])
            middle_last_df.index = middle_last_df.index + 1
            full_df = pd.concat([first_df, middle_last_df])
            full_df = full_df.drop(full_df.index[10])
            print(full_df)
            full_df.to_csv('hall_of_fame_6.csv', index=False)
            return_to_menu = input("Congrats! Returning to main menu, press and key and hit enter to continue...")
            main()

    elif start_building_qty == 11:
                
        if turn == 50:
            print("game ended!")
            print("You scored a total of " + str(points_calculate()))

            for row_index in range(0, 10):
                if points_calculate() > hall_of_fame_fn("7x7").iloc[row_index,1]:
                    player_name = input("Your name? ")
                    line = pd.DataFrame({"Player": player_name, "Score": points_calculate()}, index=[row_index])
                    break
                
            first_df = hall_of_fame_fn("7x7").iloc[:row_index]
            middle_df = line
            last_df = hall_of_fame_fn("7x7").iloc[row_index:]
            middle_last_df = pd.concat([middle_df,last_df])
            middle_last_df.index = middle_last_df.index + 1
            full_df = pd.concat([first_df, middle_last_df])
            full_df = full_df.drop(full_df.index[10])
            print(full_df)
            full_df.to_csv('hall_of_fame_7.csv', index=False)
            return_to_menu = input("Congrats! Returning to main menu, press and key and hit enter to continue...")
            main()
    elif start_building_qty == 12:
                
        if turn == 65:
            print("game ended!")
            print("You scored a total of " + str(points_calculate()))

            for row_index in range(0, 10):
                if points_calculate() > hall_of_fame_fn("8x8").iloc[row_index,1]:
                    player_name = input("Your name? ")
                    line = pd.DataFrame({"Player": player_name, "Score": points_calculate()}, index=[row_index])
                    break
                
            first_df = hall_of_fame_fn("8x8").iloc[:row_index]
            middle_df = line
            last_df = hall_of_fame_fn("8x8").iloc[row_index:]
            middle_last_df = pd.concat([middle_df,last_df])
            middle_last_df.index = middle_last_df.index + 1
            full_df = pd.concat([first_df, middle_last_df])
            full_df = full_df.drop(full_df.index[10])
            print(full_df)
            full_df.to_csv('hall_of_fame_8.csv', index=False)
            return_to_menu = input("Congrats! Returning to main menu, press and key and hit enter to continue...")
            main()

    
    column_names_list = list(user_layout_data.columns)       #Can hardcode
    print("your turn: " + str(turn))
    inventory_beside_disp_list = list(user_inventory_function().items())        #convert dict to list to be iterated through

    for i in range(4):      #inject in dummy data so it is suitable for use in string formatting
        inventory_beside_disp_list.append(("", ""))

    if start_building_qty == 8: #4x4
        
        print("{0:^7}{1:^5}{2:^7}{3:^5}{4:^7}{5:^4}".format(column_names_list[0], column_names_list[1], column_names_list[2], column_names_list[3], inventory_beside_disp_list[0][0], inventory_beside_disp_list[0][1]))
        inventory_beside_disp_list.pop(0)   #remove the first one away, since it is alreay on display
        print("+-----"*4 + "+")
        
        for i in range(user_layout_data.shape[0]):
            row = user_layout_data.iloc[i,:]
            print("|{0:^5}|{1:^5}|{2:^5}|{3:^5}|{4:^5}{5:^5}".format(row[0], row[1], row[2], row[3], inventory_beside_disp_list[i][0], inventory_beside_disp_list[i][1]))
            print("+-----"*4 + "+")

    elif start_building_qty == 9:   #5x5
        
        print("{0:^7}{1:^5}{2:^7}{3:^5}{4:^8}{5:^5}{6:^5}".format(column_names_list[0], column_names_list[1], column_names_list[2], column_names_list[3], column_names_list[4], inventory_beside_disp_list[0][0], inventory_beside_disp_list[0][1]))
        inventory_beside_disp_list.pop(0)
        print("+-----"*5 + "+")
        for i in range(user_layout_data.shape[0]):
            row = user_layout_data.iloc[i,:]
            print("|{0:^5}|{1:^5}|{2:^5}|{3:^5}|{4:^5}|{5:^5}{6:^5}".format(row[0], row[1], row[2], row[3], row[4], inventory_beside_disp_list[i][0], inventory_beside_disp_list[i][1]))
            print("+-----"*5 + "+")

    elif start_building_qty == 10:  #6x6
        
        print("{0:^7}{1:^5}{2:^7}{3:^5}{4:^7}{5:^7}{6:^4}{7:^5}".format(column_names_list[0], column_names_list[1], column_names_list[2], column_names_list[3], column_names_list[4], column_names_list[5], inventory_beside_disp_list[0][0], inventory_beside_disp_list[0][1]))
        inventory_beside_disp_list.pop(0)
        print("+-----"*6 + "+")
        for i in range(user_layout_data.shape[0]):
            row = user_layout_data.iloc[i,:]
            print("|{0:^5}|{1:^5}|{2:^5}|{3:^5}|{4:^5}|{5:^5}|{6:^5}{7:^5}".format(row[0], row[1], row[2], row[3], row[4], row[5], inventory_beside_disp_list[i][0], inventory_beside_disp_list[i][1]))
            print("+-----"*6 + "+")

    elif start_building_qty == 11:  #7x7
        print("{0:^7}{1:^5}{2:^7}{3:^5}{4:^7}{5:^5}{6:^7}{7:^5}{8:^5}".format(column_names_list[0], column_names_list[1], column_names_list[2], column_names_list[3],
                                                                             column_names_list[4], column_names_list[5], column_names_list[6], inventory_beside_disp_list[0][0], inventory_beside_disp_list[0][1]))
        inventory_beside_disp_list.pop(0)
        inventory_beside_disp_list
        print("+-----"*7 + "+")
        for i in range(user_layout_data.shape[0]):
            row = user_layout_data.iloc[i,:]
            print("|{0:^5}|{1:^5}|{2:^5}|{3:^5}|{4:^5}|{5:^5}|{6:^5}|{7:^5}{8:^5}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], inventory_beside_disp_list[i][0], inventory_beside_disp_list[i][1]))
            print("+-----"*7 + "+")

    elif start_building_qty == 12:  #8x8
        
        print("{0:^7}{1:^5}{2:^7}{3:^5}{4:^7}{5:^5}{6:^5}{7:^8}{8:^5}{9:^5}".format(column_names_list[0], column_names_list[1], column_names_list[2], column_names_list[3],
                                                            column_names_list[4], column_names_list[5],column_names_list[6], column_names_list[7],
                                                                                    inventory_beside_disp_list[0][0], inventory_beside_disp_list[0][1]))
        inventory_beside_disp_list.pop(0)
        print("+-----"*8 + "+")
        for i in range(user_layout_data.shape[0]):
            row = user_layout_data.iloc[i,:]
            print("|{0:^5}|{1:^5}|{2:^5}|{3:^5}|{4:^5}|{5:^5}|{6:^5}|{7:^5}|{8:^5}{9:^5}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], inventory_beside_disp_list[i][0], inventory_beside_disp_list[i][1]))
            print("+-----"*8 + "+")
    
#This function detects if player tries to place building on an occupied box, or input invalid values,
#or input box positions that are out of range. If it is legal move, it will return "legal"
def illegal_move_check(building, box):
    
    try:
        row_index = int(box[1])
        column_index = box[0]
        
        if (row_index in range(4)) and (column_index in "ABCD"):
        
            user_layout_data.loc[row_index, column_index]
            if user_layout_data.loc[row_index, column_index] == "":
                return "legal"
         
            else:
                return "box is non empty, please select another"
        else:
            return "selected row and column is out of range or invalid, please select another"
         
    except:
        return "selected row and column is out of range or invalid, please select another"


#This function will return a dictionary of the user's left over buildings
#It will first receive the user_lay_data and then calcuate the total used.
#Then, it will deduce away from the ref_user_inventory, and then return
#a dictionary of the leftover dictionary.
#Creating a function this way helps to constantly update the user_inventory
#everytime the function is called, it will make less mistakes and it also auto
#update.    
def user_inventory_function():
    user_inventory = ref_inventory.copy()
    for column_index in user_layout_data:
        for box in user_layout_data.loc[:, column_index]:
            if box == "bch":
                user_inventory["bch"] -= 1
            elif box == "fac":
                user_inventory["fac"] -= 1
            elif box == "hse":
                user_inventory["hse"] -= 1
            elif box == "shp":
                user_inventory["shp"] -= 1
            elif box == "hwy":
                user_inventory["hwy"] -= 1
            elif box == "prk":
                user_inventory["prk"] -= 1
            elif box == "mon":
                user_inventory["mon"] -= 1
        
    return user_inventory
            
            

def points_calculate_hwy():
    if "hwy" not in list(ref_inventory.keys()):
        return 0
    hwy_points = 0
    row_index_count = -1
    for row_index  in range(user_layout_data.shape[0]):
        row_index_count += 1
        column_index_count = -1
        hwy_streak_count = 0
        for box in user_layout_data.iloc[row_index, :]:
            column_index_count += 1
            if box == "hwy":
                if column_index_count != (user_layout_data.shape[1]-1): #means u havent reach the last column with a hwy, so u still can continue streak after this
                    hwy_streak_count += 1
                    
                elif  column_index_count == (user_layout_data.shape[1]-1):
                    hwy_streak_count += 1
                    hwy_points += hwy_streak_count**2
                    hwy_streak_count = 0
            
            else:
                hwy_points += hwy_streak_count**2
                hwy_streak_count = 0
    return hwy_points

def streak_calculate_prk_1st_pt():
    prk_streak_count = 0
    prk_streak_count_list = []
    row_index_count = -1
    for row_index  in range(user_layout_data.shape[0]):
        row_index_count += 1
        column_index_count = -1
        prk_streak_count = 0
        for box in user_layout_data.iloc[row_index, :]:
            column_index_count += 1
            if box == "prk":
                if column_index_count != (user_layout_data.shape[1]-1): #means u havent reach the last column with a hwy, so u still can continue streak after this
                    prk_streak_count += 1
                    
                elif  column_index_count == (user_layout_data.shape[1]-1):
                    prk_streak_count += 1
                    prk_streak_count_list.append(prk_streak_count)
                    prk_streak_count = 0
            
            else:
                prk_streak_count_list.append(prk_streak_count)
                prk_streak_count = 0

    new_prk_streak_count_list = prk_streak_count_list.copy()
    for index in range(len(prk_streak_count_list)):
        if prk_streak_count_list[index] <2:
            new_prk_streak_count_list.remove(prk_streak_count_list[index])
    return new_prk_streak_count_list

def streak_calculate_prk_2nd_pt():
    prk_streak_count = 0
    prk_streak_count_list = []
    column_index_count = -1
    for column_index  in range(user_layout_data.shape[1]):  #iterates through the columns in the data
        column_index_count += 1
        row_index_count = -1
        prk_streak_count = 0
        for box in user_layout_data.iloc[:, column_index]:  #iterates through each column first
            row_index_count += 1
            if box == "prk":
                if row_index_count != (user_layout_data.shape[0]-1): #means u havent reach the last row with a prk, so u still can continue streak after this
                    prk_streak_count += 1
                    
                elif row_index_count == (user_layout_data.shape[0]-1):
                    prk_streak_count += 1
                    prk_streak_count_list.append(prk_streak_count)
                    prk_streak_count = 0
            
            else:
                prk_streak_count_list.append(prk_streak_count)
                prk_streak_count = 0

    new_prk_streak_count_list = prk_streak_count_list.copy()
    for index in range(len(prk_streak_count_list)):
        if prk_streak_count_list[index] <2:
            new_prk_streak_count_list.remove(prk_streak_count_list[index])
    return new_prk_streak_count_list    

def points_calculate_prk(): #using 1st and 2nd pt, we can then find out whats the total points are
    if "prk" not in list(ref_inventory.keys()):
        return 0
    prk_points = 0
    prk_streak_qty = 0
    for item in streak_calculate_prk_1st_pt():
        prk_points += prk_score_dict[item]
        prk_streak_qty += item
        
    for item in streak_calculate_prk_2nd_pt():
        prk_points += prk_score_dict[item]
        prk_streak_qty += item

    columncount_index = -1
    for column_index in range(user_layout_data.shape[1]):
        columncount_index += 1
        rowcount_index = -1
        
    #box here signify the building name, e.g "hse"
    for box in user_layout_data.iloc[:,columncount_index]: #calculate the single prk, as it is not in streak. The qty is also equals to the points generated by these standalone buildings.
        
        rowcount_index += 1
        two_dimension_connected_prk_qty = 0
        if box == "":
            continue
        
        else:
            left_box = (rowcount_index, columncount_index - 1)
            right_box = (rowcount_index, columncount_index + 1)
            top_box = (rowcount_index - 1, columncount_index)
            bottom_box = (rowcount_index + 1, columncount_index)

            box_positions_list = [left_box, right_box, top_box, bottom_box]

            
            for position in box_positions_list: #iterates through the surrounding box positions

                rowcount_index2 = position[0]
                columncount_index2 = position[1]
                if rowcount_index2 in range(user_layout_data.shape[0]):
                    if columncount_index2 in range (user_layout_data.shape[1]):
                        if box == "prk":
                            if user_layout_data.iloc[position[0], position[1]] == "prk":    #if the surrounding boxes == prk
                                two_dimension_connected_prk_qty += 1
                                break                                                        #break bcuz only need to add 1 count. we cannot add more than that. We need to let it move on to the next box!!

            
                               
                        
    
    standalone_prk_qty = start_building_qty - user_inventory_function()['prk'] - (prk_streak_qty - two_dimension_connected_prk_qty)
    prk_points += standalone_prk_qty
    return prk_points

def points_calculate_mon():
    if "mon" not in list(ref_inventory.keys()):
        return 0
    mon_corner_qty = 0
    if user_layout_data.iloc[0,0] == "mon":
        mon_corner_qty += 1
    if  user_layout_data.iloc[0,user_layout_data.shape[1]-1] == "mon":
        mon_corner_qty += 1
    if user_layout_data.iloc[user_layout_data.shape[0]-1, 0] == "mon":
        mon_corner_qty += 1
    if user_layout_data.iloc[user_layout_data.shape[0]-1, user_layout_data.shape[1]-1] == "mon":
        mon_corner_qty += 1

    deployed_mon_qty = start_building_qty - user_inventory_function()["mon"]
    
    if mon_corner_qty > 2:
        return deployed_mon_qty*4
    else:
        return mon_corner_qty*2 + (deployed_mon_qty - mon_corner_qty)
        
    




#this function calculates the points it will generate per turn. I start off
#by calculating the points the factory will generate first, since it is
#unaffected by its surroundings.
def points_calculate():
    
    columncount_index = -1
    total_points = 0
    #calculate for fac
    if "fac" in list(ref_inventory.keys()):
        deployed_fac_qty = start_building_qty - user_inventory_function()['fac']
        if deployed_fac_qty <5:
            total_points += deployed_fac_qty**2
        else:
            total_points += deployed_fac_qty**2 + (deployed_fac_qty-4)

    #end calculation for fac
    
    #calculate for bch
    if "bch" in list(ref_inventory.keys()):
        deployed_bch_qty = start_building_qty - user_inventory_function()['bch']
        bch_points = 0
        for building in user_layout_data.iloc[:,0]:
            if building == "bch":
                bch_points += 3
        
        for building in user_layout_data.iloc[:, user_layout_data.shape[1]-1]:
            if building == "bch":
                bch_points += 3
        deployed_bonus_bch_qty = bch_points/3
        deployed_normal_bch_qty = deployed_bch_qty - deployed_bonus_bch_qty
        deployed_normal_bch_points = deployed_normal_bch_qty*1
        bch_points += deployed_normal_bch_points
        total_points += bch_points

    #end calculation for bch

    for column_index in user_layout_data:
        columncount_index += 1
        rowcount_index = -1
        
        #box here signify the building name, e.g "hse"
        for box in user_layout_data.iloc[:,columncount_index]:
            
            rowcount_index += 1
    
            if box == "":
                continue
            
            else:
                left_box = (rowcount_index, columncount_index - 1)
                right_box = (rowcount_index, columncount_index + 1)
                top_box = (rowcount_index - 1, columncount_index)
                bottom_box = (rowcount_index + 1, columncount_index)
    
                box_positions_list = [left_box, right_box, top_box, bottom_box]

                types_of_buildings_deployed = []
                building_points = 0
                for position in box_positions_list: #iterates through the surrounding box positions

                    rowcount_index2 = position[0]
                    columncount_index2 = position[1]
                    if rowcount_index2 in range(user_layout_data.shape[0]):
                        if columncount_index2 in range (user_layout_data.shape[1]):
                            #now, we can calculate the points for each building that are affected by surrounding buildings, 
                            #unlike bch and fac
                            
                            if box == "hse":
                                
                                
                                if (user_layout_data.iloc[position[0], position[1]] == "hse") or (user_layout_data.iloc[position[0], position[1]] == "shp"):
                                    building_points += 1
                                        
                                elif (user_layout_data.iloc[position[0], position[1]] == "bch"):
        
                                    building_points += 2
                                
                                elif user_layout_data.iloc[position[0], position[1]] == "fac":  #break and move on to the next position already
                                    building_points = 1
                                    total_points += building_points
                                    break

                                if position == bottom_box:      #signify the end of the box_positions_list, hence add into the total points
                                    total_points += building_points
                
                            elif box == "shp":
                                if (user_layout_data.iloc[position[0], position[1]] not in types_of_buildings_deployed) and (user_layout_data.iloc[position[0], position[1]] != ""):
                                    types_of_buildings_deployed.append(user_layout_data.iloc[position[0], position[1]])

                                if position == bottom_box:
                                    building_points = len(types_of_buildings_deployed)
                                    total_points += building_points

                    
    total_points += points_calculate_hwy() + points_calculate_prk()
    return total_points
                                
#This function appends the new building at the box specified. Of course,
#it will run through the illegal_move_check function first to determine
#elligbility. If it is a legal move, it will then place the new building
#into the user_layout_data at the specified box. Do not worry about appending buildings
#that are zero, because the function disp_all_options has taken measures
#to make sure this building chosen has at least a quantity of one
def build_building(building, box):
    if illegal_move_check(building, box) == "legal":
         row_index = int(box[1])
         column_index = box[0]
         user_layout_data.loc[row_index, column_index] = building
    
    else:
        print(illegal_move_check(building, box))
        







#first two options display the building choice to user. It will ensure that the
#buildings given to choose are in stock.
def disp_all_choices():        #function cannot be used after turn 16 #function chooses building and change layout and inventory
    disp_layout()
    disp_all_choices_loop = True
    while disp_all_choices_loop:
        loop1 = True
        while loop1:
            building_1 = rd.choice(list(ref_inventory.keys()))
            if user_inventory_function()[building_1] ==0:
                continue
            else:
                loop1 = False
        
        loop2 = True
        while loop2:
            building_2 = rd.choice(list(user_inventory_function().keys()))
            if user_inventory_function()[building_2] ==0:
                continue
            
            elif (building_1 == building_2) and (user_inventory_function()[building_1] <=1):
                    continue
                
            else:
                print("1. Build a {}\n2. Build a {}".format(building_1, building_2))
                loop2 = False
        print("3. See remaining buildings\n4. See current score\n\n5. Save game\n0. Exit to main menu")
        
        choice = input("Your choice?")
        
        if choice in "123450":
            if choice == "1":
                choice_1_box = input("Please key in the box you want to place: ")
                build_building(building_1, choice_1_box)
                disp_layout()
            elif choice == "2":
                choice_2_box = input("Please key in the box you want to place: ")
                build_building(building_2, choice_2_box)
                disp_layout()
            
            elif choice == "3":
                print(user_inventory_function())
            
            elif choice == "4":
                print("Your total points are " + str(points_calculate() ))
            
            elif choice == "5":
                user_layout_data.to_csv('user_saved_data.csv', index=False)
            
            elif choice == "0":
                revert_back_to_normal()
                main()
                disp_all_choices_loop = False
        else:
            print("Invalid choice selected. Please try again.")
        
user_layout_data = 0
def main():
    print("1. Start new game\n2. Load saved game\n3. Show high scores\n0. Exit")
    mainloop = True
    while mainloop:
        choice = input("Your choice? ")
        global user_layout_data
        if choice == "1":     #start new game
            while True:
                try:
                    first_building_to_remove = input("Please give the first building to remove from the pool: ")
                    ref_inventory.pop(first_building_to_remove)
                    print(ref_inventory)
                    break
                except KeyError:
                    print("invalid input")

            while True:
                try:
                    second_building_to_remove= input("Please give the second building to remove from the pool: ")
                    ref_inventory.pop(second_building_to_remove)
                    print(ref_inventory)
                    break
                except KeyError:
                    print("invalid input")
           
            while True:
                city_size_choice = input("Please type in either 4x4, 5x5, 6x6, 7x7, 8x8 for your city size: ")
                reply_fr_fn = start_building_qty_fn(city_size_choice)
                if reply_fr_fn == "invalid":
                    print("invalid")
                else:
                    break
                    
            print(ref_inventory)
            ref_layout_data_fn()    #based on start_building_qty_fn, develop your ref layout data
            print(ref_inventory)
            user_layout_data = ref_layout_data.copy()
            print(user_layout_data)
            print(ref_inventory)
            
            disp_all_choices()
            mainloop = False
            
        elif choice == "2":   #load saved game
            try:
                global start_building_qty
                user_layout_data = pd.read_csv("user_saved_data.csv")
                
                user_layout_data =  user_layout_data.replace(np.nan, '', regex=True)
                if len(user_layout_data) == 4:
                    start_building_qty = 8
                    start_building_qty_input = "4x4"
                    
                elif len(user_layout_data) == 5:
                    start_building_qty = 9
                    start_building_qty_input = "5x5"
                    
                elif len(user_layout_data) == 6:
                    start_building_qty = 10
                    start_building_qty_input = "6x6"
                    
                elif len(user_layout_data) == 7:
                    start_building_qty = 11
                    start_building_qty_input = "7x7"
                    
                elif len(user_layout_data) == 8:
                    start_building_qty = 12
                    start_building_qty_input = "8x8"

                start_building_qty_fn(start_building_qty_input)
                disp_all_choices()
                mainloop = False
            except FileNotFoundError:
                    print("No user data found! Please start a new game and remember to save!")
            
        elif choice == "3":   #show high score
            while True:
                hall_of_fam_choice = input("Please type in either 4x4, 5x5, 6x6, 7x7, 8x8 for your city size: ")
                if hall_of_fam_choice == "invalid":
                    print("invalid input, try again")
                else:
                    break
            print(hall_of_fame_fn(hall_of_fam_choice))
        
        elif choice == "0":   #exit
            print("Bye!")
            mainloop = False
        else:
            print("Inavalid input, please try again!")


main()

    
