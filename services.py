# With this file we are going to send te request to our server
import requests
import json
import time
from datetime import datetime
import re
import sched, time
from BASE_IP import chose_base



# define our base URL: this is the location of the API
BASE = chose_base()



global data_user_total
global data_mission_total
global data_assignment_total
global data_drone_total
global drones_paths
data_user_total = []
data_mission_total = []
data_assignment_total = []
data_drone_total = []
drones_paths = []

# OK
def set_post_station(f_name, l_name, address, city, state, zip_code, user_coords, availability_from, availability_to):
    user_coords = str(user_coords)  # convert an array in string
    
    if (availability_from >= availability_to):
        print("The availability range inserted is not correct, please try again")
        user_IDD = "None"
    else: 
        # Get how many user have already applied
        user_list = requests.get(BASE + "addresses")
        user_list = user_list.json()
        last_user = len(user_list) # How many users, this allows to keep count of the next user ID to insert next people
        # Insert data in the addresses table (increment the table to keep track of user id, how many users we have got)
        data_user1 = {"first_names":f_name, "last_names": l_name, "addresses": address, "cities": city, "states": state, "zipcodes": zip_code, "coords": user_coords, "days": availability_from, "av_froms": availability_from , "av_tos": availability_to}
        response = requests.put(BASE + "addresses", data_user1)
    # Insert data in the user table
        data_user = {"user_coords":user_coords, "availability_from": availability_from, "availability_to": availability_to}
        response = requests.put(BASE + "user/" + str(last_user),data_user)  # return the last inserted item
        # Return the user ID to allow the user to require with its user ID if there are drones for him
        user_IDD = str(last_user)
        print("Your user id is: " + user_IDD )  # to let the user know which is his user id (later he will need this info)

    return(user_IDD)    
 
# OK
def get_post_station():
    response = requests.get(BASE + "addresses")
    print("A new subscription has been received: ")
    response = response.json()
    print(response)
    cs_x = []
    cs_y = []
    for i in range(len(response)):
        coordinates = response[i]['coords'] # Extract from the dict the coods
        #Split the retrieved coordinates to x and y cs coordinates for the opt algorithm
        a = coordinates.split(',')
        cs_x.append(int(a[0])) # Fill cs_x vector
        cs_y.append(int(a[1])) # Fill cs_y vector
    
    # Add a remote CS -> for the correct functioning of the algorithm
    cs_x.append(200)
    cs_y.append(200)

    return (cs_x, cs_y)    

        

# OK
def set_path(drone_ID, path_coords, mission_from, mission_to, covered_path, uncovered_path, uncovered_from, uncovered_to, mission_status):

    if (mission_from >= mission_to):
        print("The time mission range inserted is not correct, please try again")
    else:
        path_coords = str(path_coords)
        covered_path = str(covered_path)
        uncovered_path = str(uncovered_path)
        data_mission = {"path_coords":path_coords, "mission_from": mission_from, "mission_to": mission_to, 
         "covered_path": covered_path, "uncovered_path": uncovered_path, "uncovered_from": uncovered_from,
          "uncovered_to": uncovered_to, "mission_status": mission_status}
        data_mission_total.append(data_mission)   
        response = requests.put(BASE + "mission/" + str(drone_ID), data_mission_total[len(data_mission_total)-1])
        # paths = "ID:" + str(drone_ID) + ":Path: " + data_mission.get('path_coords')
        # drones_paths.append(paths)
        # Split the path into the subpaths and create the covered and uncovered array which contains the reference number of each subpath
        subpaths = path_coords[1:-1]  # remove the sart and finish bracktes
        subpaths = subpaths.split(', 1000, ')
        uncoveredpath_dictionary = {}  # initialize an empty dictionary 
        coveredpath_dictionary = {}  # initialize an empty dictionary
        for i in range(len(subpaths)):
            uncoveredpath_dictionary["subpath_{0}".format(i)] = subpaths[i]  # fill the dictionary with all paths for a certain drone  (at the begginning they are uncovered paths)

        # Update uncovered_path and covered_path in the mission table
        uncoveredpath_dictionary_string = str(uncoveredpath_dictionary)  
        coveredpath_dictionary_string = str(coveredpath_dictionary)
        update_uncovered_covered = requests.patch(BASE + "mission/" + str(drone_ID), {"covered_path":coveredpath_dictionary_string, "uncovered_path":uncoveredpath_dictionary_string})



# OK
def get_path(drone_ID):
    drone_ID = str(drone_ID)
    print()
    print("The informartion about the drone " + drone_ID + " are: ")
    response = requests.get(BASE + "mission/" + drone_ID)
    print(response.json()) 
    
    return response.json()

# OK
def get_mission_status(drone_ID):
    drone_ID = str(drone_ID)
    print()
    print("The mission status of the drone " + drone_ID + " is: ")
    response = requests.get(BASE + "mission/" + drone_ID)
    info = response.json()
    info = info['mission_status']
    print(info)
    return(info)
    
# OK        
def get_path_user(user_ID, user_coords, request_from, request_to, request_status):
    
    # initialize the id_drone variable to NONE until we do not know which drone should be rescued
    id_drone = "NONE"

    if (request_from >= request_to):
        print("The requested time range inserted is not correct, please try again")
    else:    
        user_coords = str(user_coords)
        print()
        print("Analyzing the request of the user: " + str(user_ID))

        # Create a dictionary for the data_assignment
        data_assignment = {"id_drone":id_drone, "user_coords":user_coords, "request_from":request_from, "request_to":request_to, "request_status":request_status}
        
        # Fill the assignment table
        data_assignment_total.append(data_assignment) 

        fill_assignment = requests.put(BASE + "assignment/" + str(user_ID), data_assignment_total[len(data_assignment_total)-1])
        
        # Download from the cloud the drones that have been selected by the cpt to act in the mission
        which_drones = requests.get(BASE + "which")
        which_drones = which_drones.json()
        len_which_drone = len(which_drones)
        selected_drones = which_drones[len_which_drone-1]["which"]
        selected_drones = selected_drones[1:-1]
        selected_drones = selected_drones.split(",")
       
    
        # Create a vector containing all the drones paths
        for ii in range(0, len(selected_drones)):
            to_pass = int(selected_drones[ii])
            download_info = requests.get(BASE + "mission/" + str(to_pass)) # extract info from the cloud about all drones
            print(download_info.json())
            my_dict = download_info.json()
            my_path_coords = my_dict["path_coords"] # path info
            path = "ID:"+str(to_pass)+":Path:"+my_path_coords            
            drones_paths.append(path)
        print(drones_paths)

        for i in range(len(drones_paths)):  # get all the drones paths
            splitted = drones_paths[i].split(':')  # extract from the string drones_paths all the info
            ID = splitted[1]  # extract the drone ID 
            path = splitted[3]  # extract the drone path
            path = path[1:-1]  # delete from the path the first and the last bracket
            subpaths = path.split(', 1000, ')  # divide the path subsections knowing that in the main file I passed the path coordinates by dividing them with the "symbol" 1000
            for j in range(len(subpaths)):  # for each subpath
                subpaths[j] = str(subpaths[j])  # convert the subpath into string
                if user_coords in subpaths[j]:  # if the user coordinates are inside the subpath
                    response = requests.get(BASE + "mission/" + ID)  # get the info regarding a mission of a certain drone
                    resp_dict = response.json()  
                    mission_from = resp_dict["mission_from"]  # from the json file extract mission_from and mission_to coloumn
                    mission_to = resp_dict["mission_to"]

                    # split and convert mission_from into datetime type
                    mission_from = mission_from.split('T')
                    date, time = str(mission_from[0]), str(mission_from[1])
                    date = date.split('-')
                    time = time.split(':')
                    year, month, day, hour, seconds, milliseconds = int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]) 
                    mission_from = datetime(year, month, day, hour, seconds, milliseconds, 1).isoformat()
                    
                    # split and convert mission_to into datetime type
                    mission_to = mission_to.split('T')
                    date2, time2 = str(mission_to[0]), str(mission_to[1])
                    date2 = date2.split('-')
                    time2 = time2.split(':')
                    year2, month2, day2, hour2, seconds2, milliseconds2 = int(date2[0]), int(date2[1]), int(date2[2]), int(time2[0]), int(time2[1]), int(time2[2]) 
                    mission_to = datetime(year2, month2, day2, hour2, seconds2, milliseconds2, 1).isoformat()
                    
                    response_uncovered = requests.get(BASE + "mission/" + ID)  # get the info regarding a mission of a certain drone
                    response_uncovered_json = response_uncovered.json()  # translate the info in a json format
                    uncovered_path = response_uncovered_json["uncovered_path"]  # from the json file extract uncovered_path information

                    # split and convert uncovered_path into dictionary type
                    uncovered_path = uncovered_path[1:-1]  # remove the {} brackets
                    uncovered_path = uncovered_path.split("'")  # split using ' character
                    del uncovered_path[0::2]  # remove some blank vakues (resulted from the split
                    # split the list into two list alternatley in order to have a list containing the keys and the other the values of the dictionary                 
                    keys = uncovered_path[::2]
                    values = uncovered_path[1::2]
                    uncoveredpath_dictionary = dict(zip(keys, values))
                    # check if the subpath is still inside the subpaths dictionary which is posted in the uncovered path value 
                    # and check if the request time interval of the user is inside the mission time interval
                    if (subpaths[j] in uncoveredpath_dictionary.values()): # and (mission_from < request_from) and (request_to < mission_to): 
                        
                        # return the key of the dictionary that contains the certain subpath 
                        index = list(uncoveredpath_dictionary.keys())[list(uncoveredpath_dictionary.values()).index(subpaths[j])]
                        check = "You will have to take care of the drone " + ID + " in the subpath "+str(j) 
                        my_subpath = subpaths[j]
                        subpath_string = "subpath_"+str(j)
                        my_info = [check, my_subpath, j, int(ID), subpath_string]
                        return(my_info)
                    else:
                        check = "There are no drones for you"
                        my_info = [check, 0, 0, 0]   
                else:
                    check = "There are no drones for you"
                    my_info = [check, 0, 0, 0] 
                    
    

    return(my_info)                



# OK
def confirm_post_station(user_ID, drone_ID, index):

    user_ID = str(user_ID)
    drone_ID = str(drone_ID)

    response_coveredUncovered = requests.get(BASE + "mission/" + drone_ID)  # get the info regarding a mission of a certain drone
    response_coveredUncovered_json = response_coveredUncovered.json()  # translate the info in a json format
    uncovered_path = response_coveredUncovered_json["uncovered_path"]  # from the json file extract uncovered_path information
    covered_path = response_coveredUncovered_json["covered_path"]  # from the json file extract covered_path information

    # split and convert uncovered_path into dictionary type
    uncovered_path = uncovered_path[1:-1]  # remove the {} brackets
    uncovered_path = uncovered_path.split("'")  # split using ' character
    del uncovered_path[0::2]  # remove some blank vakues (resulted from the split
    # split the list into two list alternatley in order to have a list containing the keys and the other the values of the dictionary                 
    keys_uncovered = uncovered_path[::2]
    values_uncovered = uncovered_path[1::2]
    uncoveredpath_dictionary = dict(zip(keys_uncovered, values_uncovered))

    # split and convert covered_path into dictionary type
    covered_path = covered_path[1:-1]  # remove the {} brackets
    covered_path = covered_path.split("'")  # split using ' character
    del covered_path[0::2]  # remove some blank vakues (resulted from the split
    # split the list into two list alternatley in order to have a list containing the keys and the other the values of the dictionary                 
    keys_covered = covered_path[::2]
    values_covered = covered_path[1::2]
    coveredpath_dictionary = dict(zip(keys_covered, values_covered))
    
    # update the request_status and the drone_id in the assignment table
    update_assignment = requests.patch(BASE + "assignment/" + user_ID, {"id_drone":drone_ID, "request_status":"CONFIRMED"})
                        
    temp_subpath = uncoveredpath_dictionary[index]  # store temporanely in this variable the value of the subpath of the corresponding index
    # update the confirmed path in mission table removing it from the uncovered_path and add it to the covered path
    # remove the item with the subpath from the uncovered dictionary to reduce the uncovered_path dimension
    remove_index = uncoveredpath_dictionary.pop(index)
    print()
    print("REQUEST CONFIRMED") 

    # add the item with the subpath from the covered dictionary to increase the size of covered_path
    coveredpath_dictionary[index] = temp_subpath

    # update the uncovered_path and covered_path in mission_table
    uncoveredpath_dictionary_string = str(uncoveredpath_dictionary)
    coveredpath_dictionary_string = str(coveredpath_dictionary)
    print(uncoveredpath_dictionary_string)
    update_uncovered_covered = requests.patch(BASE + "mission/" + drone_ID, {"covered_path":coveredpath_dictionary_string, "uncovered_path":uncoveredpath_dictionary_string})

    # check if the uncovered dictionary is empy:
    # remember that empty dictionaries evaluate to False
    # if (bool(uncoveredpath_dictionary)==False): 
    #     update_mission_status = requests.patch(BASE + "mission/" + drone_ID, {"mission_status":"ALL PATHS ARE COVERED: the drone can take off"}) # update the mission status
                           
    # elif (bool(uncoveredpath_dictionary)==True):
    #     update_mission_status = requests.patch(BASE + "mission/" + drone_ID, {"mission_status":"THERE ARE STILL UNCOVERED PATHS"}) # update the mission status
    if (uncoveredpath_dictionary_string== "{'subpath_0': '[0, 0, 0]'}"): 
        update_mission_status = requests.patch(BASE + "mission/" + drone_ID, {"mission_status":"ALL PATHS ARE COVERED: the drone can take off"}) # update the mission status
                           
    else:
        update_mission_status = requests.patch(BASE + "mission/" + drone_ID, {"mission_status":"THERE ARE STILL UNCOVERED PATHS"}) # update the mission status
                                

# OK
def get_uncovered_path(drone_ID): 

    drone_ID = str(drone_ID)
    response = requests.get(BASE + "mission/" + drone_ID)
    info = response.json()
    print()
    print("The uncovered paths for the drone " + drone_ID + " are:")
    print()
    print(info['uncovered_path'])





# OK
def stream_data(drone_ID, status, landing_status, battery, drone_coords, stream_URL):

    drone_ID = str(drone_ID)
    drone_coords = str(drone_coords)

    data_drone = {"status":status, "landing_status": landing_status, "battery": battery, 
         "drone_coords": drone_coords, "stream_URL": stream_URL} 

    data_drone_total.append(data_drone)   
    response = requests.put(BASE + "drone/" + drone_ID, data_drone_total[len(data_drone_total)-1])



# OK
def get_data(drone_ID):

    drone_ID = str(drone_ID)
    response = requests.get(BASE + "drone/" + drone_ID)
    print()
    print("The information about the drone " + drone_ID + " are:")
    print()
    print(response.json())


# OK
def get_landing_info(drone_ID):

    drone_ID = str(drone_ID)
    response = requests.get(BASE + "drone/" + drone_ID)
    info = response.json()
    print()
    print("The landing information about the drone " + drone_ID + " are:")
    print()
    print(info['battery'] + " of battery")
    print(info['landing_status'])
    



# OK
def set_pause_mission(user_ID, drone_ID):

    user_ID = str(user_ID)
    drone_ID = str(drone_ID)
    print()
    print("I am the user " + user_ID + " and I have recovered the drone " + drone_ID)
    update_drone_status = requests.patch(BASE + "drone/" + drone_ID, {"status":"RECOVERED"})



# OK
def get_pause_mission(drone_ID):

    drone_ID = str(drone_ID)
    # Check for the status
    response = requests.get(BASE + "drone/" + drone_ID)
    info = response.json()
    status = info['status']
    if (status == "RECOVERED"):
        print() 
        print("The drone " + drone_ID + " is recovered")
    else:
        time.sleep(10)  # wait for some minutes that a user sets the status to RECOVERED
        if (status == "RECOVERED"):
            pass
        else: 
            update_drone_status = requests.patch(BASE + "drone/" + drone_ID, {"status":"SOS"})
            print()
            print("SOS for the drone " + drone_ID)



   
# OK
def set_resume_mission(user_ID, drone_ID):

    user_ID = str(user_ID)
    drone_ID = str(drone_ID)
    print()
    print("I am the user " + user_ID + " and I have resumed the drone " + drone_ID)
    update_drone_status = requests.patch(BASE + "drone/" + drone_ID, {"status":"RESUMED"})



# OK
def get_resume_mission(drone_ID):

    drone_ID = str(drone_ID)
    # Check for the status
    response = requests.get(BASE + "drone/" + drone_ID)
    info = response.json()
    status = info['status']
    if (status == "RESUMED"): 
        print()
        print("I am the drone " + drone_ID + " I am able to resume my mission")
    else:
        print()
        print("I am the drone " + drone_ID + " I am still NOT able to resume my mission")

# OK
def set_targets(Target, my_targets, my_insp_time):

    data = {"target": my_targets, "insp_time": my_insp_time, "drone_point": "", "drone_coord": ""}
    response = requests.put(BASE + "opt", data) # upload the required target
    download_info = requests.get(BASE + "opt") # dowload the info with the opt paths
    the_info = download_info.json()
    coords_dict = the_info[1]["drone_coord"]
    coords_dict = coords_dict[1:-1]
    coords_dict = coords_dict.split("]]") # split the string using this criteria
    wh_drone = [] # to know which drone will be chosen: these will be uploaded on the clou, since they will be useful alter for the user requests
    wh_path = []
    # Manage the strings containing the info
    for i in range(len(coords_dict)-1):
        if (i == 0):
            coords_dict[i] = coords_dict[i]+"]]" 
            coords_dict[i] = coords_dict[i].split(":")
            wh_drone.append(coords_dict[i][0])
            wh_path.append(coords_dict[i][1])
        else:
            coords_dict[i] = coords_dict[i][1:]
            coords_dict[i] = coords_dict[i]+"]]" 
            coords_dict[i] = coords_dict[i].split(":")
            wh_drone.append(coords_dict[i][0])
            wh_path.append(coords_dict[i][1])
    print("********************************")
    print(wh_drone) # Final array containing which drone can be selected by the cpt
    print(wh_path) # Final array containing which paths are assigned to the drones

    # Remove the initial space in the wh_path string of each path
    for ii in range(len(wh_path)):
        wh_path[ii] = wh_path[ii][1:]  

    # Translate in int to upload these info on the cloud
    for i in range(len(wh_drone)):
        wh_drone[i] = int(wh_drone[i])

    # Initialise an array where the selected drones are saved
    sel_drones = []

    # Ask the cpt which path to assign to the drones
    for j in range(len(wh_drone)):
        print("\nWould you like to assign the path: ", wh_path[j], "\n to drone number", str(wh_drone[j]), "?")
        print("Type \"y\" for \"yes\" and \"n\" for \"no\"")
        my_input = input('Enter your input:') 
        # Set the path
        if (my_input == "y"):
            sel_drones.append(wh_drone[j])
            drone_ID = wh_drone[j]
            path_coords = wh_path[j] # ogni volta che drone raggiunge un punto nuovo questo punto è frame 0,0,0
            mission_from = datetime(2021, 10, 23, 3, 30, 0, 0).isoformat() # Set the mission beginning
            mission_to = datetime(2021, 10, 29, 15, 30, 0, 0).isoformat() # Set the mission end
            covered_path = []
            uncovered_path = []
            uncovered_from = datetime(1, 1, 1, 1, 1, 1, 1).isoformat()
            uncovered_to = datetime(1, 1, 1, 1, 1, 1, 1).isoformat()
            mission_status = ("Waiting for updates")

            set_path(drone_ID, path_coords, mission_from, mission_to, covered_path, uncovered_path, uncovered_from, uncovered_to, mission_status)


    # Upload the array which_drone on the cloud
    which_drone_upload = {"which":str(sel_drones)}
    response = requests.put(BASE + "which", which_drone_upload)                        










