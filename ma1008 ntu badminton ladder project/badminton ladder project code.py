import tkinter as tk
from tkinter import ttk
import datetime as dt
from datetime import timedelta

#Transfer ladder data file into a dictionary




current_ladder = {}
activity_list=[]            #Here is where each activity will be placed in a list
uncomchallenge = []

def update_current_ladder():
    rankfile = open("cher rank.txt", "r")
    rankfile.seek(0)
    global current_ladder
    current_ladder = {}
    rank=0
    for i in rankfile:      #for loop to insert each file line into dictionary
        rank+=1
        j=i.replace("\n", "")
        current_ladder[rank]=j
    rankfile.close()

def update_activity_list():
    activityfile = open("cher activities.txt", "r")
    activityfile.seek(0)
    global activity_list
    activity_list =[]
    for line in activityfile:
        newline = line.replace("\n", "")
        activity_list.append(newline)
    activityfile.close()

def update_uncomchallenge():
    uncom_challengefile = open("uncompleted challenges.txt", "r")  
    uncom_challengefile.seek(0)
    global uncomchallenge
    uncomchallenge = []
    for line in uncom_challengefile:
        newline = line.replace("\n", "")
        uncomchallenge.append(newline)
    uncom_challengefile.close()

        
def issue_challenge(P1, rank1, P2, rank2, date_of_challenge):
    uncom_challengefile = open("uncompleted challenges.txt", "a")
    date_of_challenge_obj = dt.datetime.strptime(date_of_challenge, "%d-%m-%Y").date()
    line = "{} {}/{} {}/{}/".format(P1, rank1, P2, rank2, date_of_challenge)
    print(line, file = uncom_challengefile)
    uncom_challengefile.close()
     
def activity_check(insert):             #insert is line_list, list data format
    if len(insert) == 2:
        return "player leave/join"
    elif insert[-1] == "":
        return "forfeit/uncomchallenge"
        
    else:
        return "completed challenge"

def combine_funcs(*funcs):              #Purpose is to combine functions into one, to be executed by tkinter button
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func


#To initialise these vars so changes can be made in organise(line) function, onto these var
datetime_obj = ""
##datetime_obj = datetime_obj.date()
P1 = P2 = player = datetime_str = winner = loser = purpose = ""     
rank1 = rank2 = player_rank = P1_match1_score = P1_match2_score = P1_match3_score = P2_match1_score = P2_match2_score = P2_match3_score = 0

#function is to assign relevant variables based on the activity (line) as input
#The activity (line) is obtained from the datafile
def organise(line):         
    global P1, P2, datetime_str, winner, loser, purpose, rank1, rank2, P1_match1_score, P1_match2_score, P1_match3_score,\
        P2_match1_score, P2_match2_score, P2_match3_score, player, player_rank, datetime_obj
    line_list=line.split("/")           #Split line at "/" so to put to put into class challenge

    if activity_check(line_list) == "completed challenge":    #Check if the activity is challenge or is player leaving/join the ladder ranks. Then, organise and create relevant variables to each activity
    # organise player1 name and rank, so it can be used to create a class easily
        name_n_rank_1 = line_list[0]
        name_n_rank_list_1=name_n_rank_1.split(" ")
        P1_list = name_n_rank_list_1[0:2]
        P1 = "{} {}".format(P1_list[0], P1_list[1])     #done to add space between fname and lname
        rank1 = name_n_rank_list_1[2]

        #organise player2 name and rank
        name_n_rank_2 = line_list[1]
        name_n_rank_list_2=name_n_rank_2.split(" ")
        P2_list = name_n_rank_list_2[0:2]
        P2 = "{} {}".format(P2_list[0], P2_list[1])
        rank2 = name_n_rank_list_2[2]

        #organise date
        datetime_str = line_list[2]             #data type is in string, which can be converted to datetime object later
        datetime_obj = dt.datetime.strptime(datetime_str, "%d-%m-%Y").date()   #Create a datetime object
##        datetime_obj.date()

        #organise for either 2 or 3 matches
        list_match = line_list[3].split(" ")     #split into [XX-XX, XX-XX, XX-XX]
        #allow variables = score number
        P1_match1_score = list_match[0][0:2]
        P1_match2_score=list_match[1][0:2]
        P2_match1_score=list_match[0][3:]
        P2_match2_score=list_match[1][3:]

        #To catch challenges without third match using IndexError
        try:
            P1_match3_score=list_match[2][0:2]
            P2_match3_score=list_match[2][3:]
        except IndexError:
            P1_match3_score="0"
            P2_match3_score="0"
        #Call upon the Challenge class to create an instance for the challenge
        winner = P2
        loser = P1
        P1_match1_score, P1_match2_score, P1_match3_score, P2_match1_score, P2_match2_score, P2_match3_score=int(P1_match1_score), int(P1_match2_score), int(P1_match3_score), int(P2_match1_score), int(P2_match2_score), int(P2_match3_score)
        if P1_match1_score > P2_match1_score:
            if P1_match2_score > P2_match2_score:
                winner = P1
                loser = P2
            else:       #P1_match2_score < P2_match2_score
                if P1_match3_score > P2_match3_score:
                    winner = P1
                    loser = P2
        else:           #P1_match1_score < P2_match1_score
            if P1_match2_score > P2_match2_score:
                if P1_match3_score > P2_match3_score:
                    winner = P1
                    loser = P2
                
            
        

    elif activity_check(line_list) == "forfeit/uncomchallenge":
        name_and_rank_1 = line_list[0]
        name_and_rank_list_1=name_and_rank_1.split(" ")
        P1 = "{} {}".format(name_and_rank_list_1[0], name_and_rank_list_1[1])
        rank1 = name_and_rank_list_1[2]
        name_and_rank_2 = line_list[1]
        name_and_rank_list_2 = name_and_rank_2.split(" ")
        P2 = "{} {}".format(name_and_rank_list_2[0], name_and_rank_list_2[1])
        rank2 = name_and_rank_list_2[2]
        datetime_str = line_list [2]
        datetime_obj = dt.datetime.strptime(datetime_str, "%d-%m-%Y").date()
##        datetime_obj = datetime_obj.date()
        winner = P1
        loser = P2


    else:       #For activity that is either player leaving or joining the ladder rank
        datetime_str=line_list[1]
        datetime_obj = dt.datetime.strptime(datetime_str, "%d-%m-%Y").date()            #Create a datetime object
##        datetime_obj = datetime_obj.date()
        if line_list[0][0] == "+":
            purpose = "join"
            player = line_list[0][1:]
            player_rank = len(current_ladder)               #rank of new player
         
        else:
            purpose = "leave"
            player_rank_list = line_list[0].split(" ")
            player="{} {}".format(player_rank_list[0][1:], player_rank_list[1])         #referring to players join/leave, use player and player_rank instead of P1 and P2, rank1 and rank2
            player_rank = player_rank_list[2]                      #rank of ex player
       

#Function is to update ladder with current challenges
def update_winlose(ladder, P1, rank1, P2, rank2, playeddate, challengeddate, scores):
    update_uncomchallenge()
    update_current_ladder()
    global uncomchallenge
    rank1, rank2 = int(rank1), int(rank2)
    playedline = "{} {}/{} {}/{}/{}".format(P1, rank1, P2, rank2, playeddate, scores)
    organise(playedline)
    if winner == P1:
        if abs(rank1-rank2)==1:            #if the position diff is 1, 2 players swaped
            ladder[rank2], ladder[rank1] = ladder[rank1], ladder[rank2]
            
        elif abs(rank1-rank2) == 2:       #diff by 2, 3 players swapped
            ladder[rank2], ladder[rank2+1], ladder[rank2+2]= ladder[rank1], ladder[rank2], ladder[rank2+1]

        else:     #diff by 3, 4 players swapped
            ladder[rank2],ladder[rank2+1], ladder[rank2+2], ladder[rank2+3]=ladder[rank1], ladder[rank2], ladder[rank2+1], ladder[rank2+2]
        print(ladder)
        with open('cher rank.txt', 'w') as rankfile:
            players_list = list(ladder.values())
            for line in players_list:
                print(line, file = rankfile)

    #Update activity file
    with open('cher activities.txt', 'a') as activityfile:
        print(playedline, file = activityfile)

    uncomline = "{} {}/{} {}/{}/".format(P1, rank1, P2, rank2, challengeddate)
    uncomchallenge.remove(uncomline)
    with open("uncompleted challenges.txt", "w") as uncom_challengefile:
        for line in uncomchallenge:
            print(line, file = uncom_challengefile)
            
            
        

        
        
    

#Reverse the challenge so to obtain ladder at a particular date
def rev_update_winlose(ladder, P1, rank1, winner, P2, rank2):           
    rank1, rank2 = int(rank1), int(rank2)
    
    if winner == P1:
        if abs(rank1-rank2)==1:            #if the position diff is 1, 2 players swaped
            ladder[rank2], ladder[rank1] = ladder[rank1], ladder[rank2]
            
        elif abs(rank1-rank2) == 2:       #diff by 2, 3 players swapped
            ladder[rank2], ladder[rank2+1], ladder[rank2+2] = ladder[rank2+1], ladder[rank2+2], ladder[rank2]
            
        else:           #diff is 3
            ladder[rank2], ladder[rank2+1], ladder[rank2+2], ladder[rank1] = ladder[rank2+1], ladder[rank2+2], ladder[rank2+3], ladder[rank2]

#function update ladder based on players joining and leaving
def update_joinleave(player):              #this fn appends, while the rev fn does not
    global current_ladder
    update_current_ladder()
    update_activity_list()
    players = list(current_ladder.values())
    tot = len(current_ladder)
    with open('cher activities.txt', 'a') as activityfile:
        if player in players:       #Player want to leave        
            player_rank = players.index(player) + 1
            copy_ladder = current_ladder
            for j in range(player_rank, tot):
                current_ladder[j] = copy_ladder[j+1]
            current_ladder.popitem()
            line = "-{}/{}".format(player, dt.datetime.today().strftime("%d-%m-%Y"))
            print(line, file = activityfile)
            
        else:           #if not leave then is join
            current_ladder[tot+1] = player
            line = "+{}/{}".format(player, dt.datetime.today().strftime("%d-%m-%Y"))
            print(line, file = activityfile)

    players = list(current_ladder.values())
    with open('cher rank.txt', 'w') as rankfile:
        for line in players:
            print(line, file = rankfile)

#function reverse update ladder based on players joining and leaving
def rev_update_joinleave(hist_ladder, player, purpose, player_rank):
    player_rank = int(player_rank)
    tot = len(hist_ladder)
    if purpose == "leave":
        copy_ladder = hist_ladder.copy()
        hist_ladder[player_rank] = player
        for i in range(1, tot+2-player_rank):
            hist_ladder[player_rank+i] = copy_ladder[player_rank+i-1]
    else:       #If not leave then is join
        hist_ladder.popitem()

hist_ladder=current_ladder        
##With the infomation about the activity neatly placed inside classes, we can go on to design a function to display the ladder given a date input
def backtrack_ladder_to(datetime_input_str):
    global hist_ladder
    update_current_ladder()
    update_activity_list()
    datetime_input_obj = dt.datetime.strptime(datetime_input_str, "%d-%m-%Y").date()      #Convert datetime in string to datetime object
    hist_ladder = current_ladder.copy()           #Create this variable so to represent ladder at whichever date

    rev_activity_list = activity_list.copy()         #Reverse the order so I can reverse engineer the ladder ranks
    rev_activity_list.reverse()
    total=len(rev_activity_list)
    for line in rev_activity_list:
        LIST=line.split("/")
        organise(line)              #line has been organised based on types, providing relevant variables
        if activity_check(LIST) == "completed challenge" or activity_check(LIST) == "forfeit/uncomchallenge":
            if datetime_input_obj > datetime_obj:            #Check if the requested datetime is greater than current line, break if so
                break
            else:                   #We can then reverse the ladder
                rev_update_winlose(hist_ladder, P1, rank1, winner, P2, rank2)
        else:               #this is when player join/leave
            if datetime_input_obj > datetime_obj:
                 break
            else:
                rev_update_joinleave(hist_ladder, player, purpose, player_rank)

    
#Using class to contain widgets into Frames, allow switching of frames much easier


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        challenge_but = tk.Button(self, text = "view/record/issue Challenge", command = lambda: controller.show_frame(Challenge)).place(x = 150, y = 100)    #after logging in/Register
        
        def get():                                      #get data from entry and execute update function
            joinleave_name = joinleave_entry.get()
            update_joinleave(joinleave_name)
        joinleave_but = tk.Button(self, text = "join/leave  ladder", command = get).place(x=200,y=130)
        joinleave_entry = tk.Entry(self).place(x = 200, y =160)
        queries_but = tk.Button(self, text= "Queries", command=lambda: controller.show_frame(QueriesPage)).place(x = 200, y = 220)


class QueriesPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        lad_hist_but = tk.Button(self, text = "View ladder", command=lambda: controller.show_frame(LadderPage))
        lad_hist_but.place(x=200,y=50)
        players_queries_but= tk.Button(self, text="player queries")
        MIDR_but = tk.Button(self, text="Matches in date range")
        MIDR_but.place(x=200, y=150)
        def mostleast_active():
            update_activity_list()
            active_players = {}
            for i in activity_list:
                organise(i)
                if P1 in active_players.keys():
                    active_players[P1] += 1
                else:
                    active_players[P1] = 1
                if P2 in active_players.keys():
                    active_players[P2] += 1
                else:
                    active_players[P2] = 1
                    
            most_active = max(active_players, key = active_players.get)
            least_active = min(active_players, key = active_players.get)
            return [most_active, least_active]

        def disp_active_players():
            disptext = mostleast_active()
            active_label = tk.Label(self, text = disptext)
            active_label.place(x = 400, y = 380)
                                
        active_button = tk.Button(self, text = "active players", command = disp_active_players)
        active_button.place(x = 400, y = 360)
        matches_but = tk.Button(self, text = "Show matches of player and date", command = lambda: controller.show_frame(matches))
        matches_but.place(x = 400, y = 380)
        back_but = tk.Button(self, text="back", command=lambda: controller.show_frame(MainPage))
        back_but.place(x=350,y=400)

class matches (tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        matchestree_frame = tk.Frame(self)
        matchestree_frame.pack(pady=5)
        #Treeview Scrollbar
        matchestree_scroll = tk.Scrollbar(matchestree_frame)
        matchestree_scroll.pack(side=tk.RIGHT,fill=tk.Y)
        #Create Treeview and place inside Frame
        matchestree = ttk.Treeview(matchestree_frame, yscrollcommand = matchestree_scroll.set)
        #Configure scroll bar
        matchestree_scroll.config(command = matchestree.yview)
        matchestree.pack(side=tk.LEFT)
        matchestree["column"] = ("P1", "rank1", "P2", "rank2", "Date of challenge", "M1", "M2", "M3")
        matchestree.column("#0", width = 0)
        matchestree.heading("#0", text="")
        matchesdict = {"P1" : 100, "rank1" : 80, "P2" : 100, "rank2" : 80, "Date of challenge" : 150, "M1" : 70, "M2" : 70, "M3" : 70}
        for i in matchesdict:
            matchestree.heading(i, text = i)
            matchestree.column(i, width = matchesdict[i])
        
        def player_disp_matches():
            update_activity_list()
            matchestree.delete(*matchestree.get_children())
            player = player_disp_matches_entry.get()
            for line in activity_list:
                if player in line:
                    organise(line)
                    x = "{}-{}".format(P1_match1_score, P2_match1_score)
                    y = "{}-{}".format(P1_match2_score, P2_match2_score)
                    z = "{}-{}".format(P1_match3_score, P2_match3_score)
                    matchestree.insert(parent="", index="end", values=(P1, rank1, P2, rank2, datetime_str, x, y, z))
                    
        player_disp_matches_label = tk.Label(self, text = "Please Enter which player you want to see:")
        player_disp_matches_label.place(x = 250, y = 300)
        player_disp_matches_entry = tk.Entry(self)
        player_disp_matches_entry.place(x = 250, y = 320)
        player_disp_matches_but = tk.Button(self, text = "Display matches of player", command = player_disp_matches)
        player_disp_matches_but.place(x = 250, y = 340)

        def date_disp_matches():
            update_activity_list()
            matchestree.delete(*matchestree.get_children())
            date = date_disp_matches_entry.get()
            for line in activity_list:
                if date in line:
                    organise(line)
                    x = "{}-{}".format(P1_match1_score, P2_match1_score)
                    y = "{}-{}".format(P1_match2_score, P2_match2_score)
                    z = "{}-{}".format(P1_match3_score, P2_match3_score)
                    matchestree.insert(parent="", index="end", values=(P1, rank1, P2, rank2, datetime_str, x, y, z))
        date_disp_matches_label = tk.Label(self, text = "Please Enter which date you want to see:")
        date_disp_matches_label.place(x = 250, y = 360)
        date_disp_matches_entry = tk.Entry(self)
        date_disp_matches_entry.place(x = 250, y = 380)
        date_disp_matches_but = tk.Button(self, text = "Display matches on date", command = date_disp_matches)
        date_disp_matches_but.place(x = 250, y = 400)

        def range_disp_matches():
            update_activity_list()
            start_obj = dt.datetime.strptime(range1_disp_matches_entry.get(), "%d-%m-%Y").date()
            end_obj = dt.datetime.strptime(range2_disp_matches_entry.get(), "%d-%m-%Y").date()
            for line in activity_list:
                organise(line)
                if datetime_obj >= start_obj:
                    if datetime_obj <= end_obj:
                        x = "{}-{}".format(P1_match1_score, P2_match1_score)
                        y = "{}-{}".format(P1_match2_score, P2_match2_score)
                        z = "{}-{}".format(P1_match3_score, P2_match3_score)
                        matchestree.insert(parent="", index="end", values=(P1, rank1, P2, rank2, datetime_str, x, y, z))

        range_disp_matches_label = tk.Label(self, text = "Please Enter the date range:")
        range_disp_matches_label.place(x = 250, y = 420)
        range1_disp_matches_entry = tk.Entry(self)
        range1_disp_matches_entry.place(x = 250, y = 440)
        range2_disp_matches_entry = tk.Entry(self)
        range2_disp_matches_entry.place(x = 280, y = 440)
        range_disp_matches_but = tk.Button(self, text = "Display matches on date range", command = range_disp_matches)
        range_disp_matches_but.place(x = 300, y = 440)              
                    
                    
class Challenge (tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
         #Create Frame inside of self, to contain treeview and scrollbar
        uncomchallengetree_frame = tk.Frame(self)       #uncomchallengetree = uncompleted challenge tree
        uncomchallengetree_frame.pack(pady=5)
        #Treeview Scrollbar
        uncomchallengetree_scroll = tk.Scrollbar(uncomchallengetree_frame)
        uncomchallengetree_scroll.pack(side=tk.RIGHT,fill=tk.Y)
        #Create Treeview and place inside Frame
        uncomchallengetree = ttk.Treeview(uncomchallengetree_frame, yscrollcommand = uncomchallengetree_scroll.set)
        #Configure scroll bar
        uncomchallengetree_scroll.config(command=uncomchallengetree.yview)
        uncomchallengetree.pack(side=tk.LEFT)
        uncomchallengetree["column"] = ("Challenger", "rank1", "Challenged", "rank2", "Date of challenge")
        headingwidths = {"Challenger": 100, "rank1": 80, "Challenged" : 100, "rank2" : 80, "Date of challenge": 150}
        uncomchallengetree.column("#0", width = 0)
        uncomchallengetree.heading("#0", text = "")
        
        for i in headingwidths:
            uncomchallengetree.column(i, width = headingwidths[i])
            uncomchallengetree.heading(i, text = i)


        PLAYERS = 0
        def display_uncomchallenge():
##            global PLAYERS
            update_uncomchallenge()
            update_current_ladder()
##            PLAYERS = list(current_ladder.values())
            uncomchallengetree.delete(*uncomchallengetree.get_children())
            for challenge in uncomchallenge:
                organise(challenge)
                uncomchallengetree.insert(parent="", index="end", values=(P1, rank1, P2, rank2, datetime_str))
        display_uncomchallenge()

        def issue():
            global PLAYERS
            update_uncomchallenge()
            update_current_ladder()
            PLAYERS = list(current_ladder.values())
            P1 = challenger.get()
            rank1 = PLAYERS.index(P1) + 1
            P2 = challenged.get()
            rank2 = PLAYERS.index(P2) + 1
            date_of_challenge = challenge_date.get()
            issue_challenge(P1, rank1, P2, rank2, date_of_challenge)
        
        challenger_label = tk.Label(self, text = "Please enter your name: ")
        challenger_label.place(x=200, y=200)
        challenger = tk.Entry(self)
        challenger.place(x=200, y=225)
        challenged_label = tk.Label (self, text = "Please enter who you want to challenge, but only 3 positions up!")
        challenged_label.place(x=200, y=250)
        challenged = tk.Entry(self)
        challenged.place(x=200, y =275)
        challenge_date_label = tk.Label(self, text = "Challenge date, enter in the format of DD-MM-YYYY: ")
        challenge_date_label.place(x=200, y=300)
        challenge_date = tk.Entry(self, width = 15)
        challenge_date.place(x=200, y=350)
        issue_challenge_but = tk.Button(self, text="issue and display challenges", command = lambda: combine_funcs (issue(), display_uncomchallenge()))
        issue_challenge_but.place(x=200, y=375)
        back_but = tk.Button(self, text="back", command=lambda: controller.show_frame(MainPage))
        back_but.place(x=350,y=400)

        def record():
            update_current_ladder()
            selected = uncomchallengetree.item(uncomchallengetree.focus())
            scores = matchscores_entry.get()
            playeddate = playeddate_entry.get()
            print(selected["values"][0], selected["values"][1], selected["values"][2], selected["values"][3], playeddate, selected["values"][4], scores)
            update_winlose(current_ladder, selected["values"][0], selected["values"][1], selected["values"][2], selected["values"][3], playeddate, selected["values"][4], scores)

            
        matchscores_entry = tk.Entry(self)
        matchscores_entry.place(x = 300, y = 420)
        playeddate_entry = tk.Entry(self)
        playeddate_entry.place(x = 300, y = 440)
        record_but = tk.Button(self, text = "record", command = lambda: combine_funcs(record(), display_uncomchallenge()))
        record_but.place(x=300, y = 400)

class LadderPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #Create Frame inside of self, to contain treeview and scrollbar
        ranktree_frame = tk.Frame(self)
        ranktree_frame.pack(pady=5)
        #Treeview Scrollbar
        ranktree_scroll = tk.Scrollbar(ranktree_frame)
        ranktree_scroll.pack(side=tk.RIGHT,fill=tk.Y)
        #Create Treeview and place inside Frame
        ranktree = ttk.Treeview(ranktree_frame, yscrollcommand = ranktree_scroll.set)
        #Configure scroll bar
        ranktree_scroll.config(command=ranktree.yview)
        ranktree.pack(side=tk.LEFT)
        #Create option to navigate to historical ladder ranks
        lad_hist_label = tk.Label(self, text="Please enter the date for the ladder you want to see, in the format DD-MM-YYYY:")
        lad_hist_label.place(x=50, y=300)
        lad_hist_entry = tk.Entry(self, width=15)
        lad_hist_entry.place(x=100, y=320)
        get_lad_hist_but = tk.Button(self, text="Obtain historical ladder", command=lambda: combine_funcs(backtrack_ladder_to(lad_hist_entry.get()), display_ladder()))
        get_lad_hist_but.place(x=170, y=320)


        #Defining columns
        ranktree["columns"] = ("Name", "Rank")
        #Format columns
        ranktree.column("#0", width=0)          #phantom column = #0
        ranktree.heading("#0", text="")
        
        
        ranktree.heading("Name", text="Name")
        ranktree.column("Name", width = 100)
        ranktree.heading("Rank", text="Rank")
        ranktree.column("Rank", width = 100)

        def display_ladder():
            ranktree.delete(*ranktree.get_children())
            for rank_player in hist_ladder:
                ranktree.insert(parent="", index="end", iid= rank_player, values=(hist_ladder[rank_player], rank_player))

        back_but = tk.Button(self, text="back", command=lambda: controller.show_frame(QueriesPage))
        back_but.place(x=350,y=400)

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #creating a window
        window=tk.Frame(self)
        window.pack()

        window.grid_rowconfigure(0, minsize=500)
        window.grid_columnconfigure(0, minsize=500)

        self.frames = {}
        for F in (MainPage, QueriesPage, LadderPage, Challenge, matches):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column = 0, sticky="nsew")
        self.show_frame(MainPage)
    def show_frame(self, page):
        frame=self.frames[page]
        frame.tkraise()

app=Application()

app.resizable(False,False)

