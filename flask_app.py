# Use a database
from datetime import datetime
from tkinter.constants import FIRST
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with 
from evaluate_path import evaluate_path
from services import get_post_station
import requests
import json



# Initialize the RESTful API
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'   # define the location of the database
db = SQLAlchemy(app)  # database


# Drone Model
class DroneModel(db.Model): # define all the fields inside a drone model
    id = db.Column(db.Integer, primary_key=True) # primary_key=True means that each id will be different for all the drones
    status = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a status
    landing_status = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a status
    battery = db.Column(db.String(100), nullable=False)
    drone_coords = db.Column(db.String(100), nullable=False)
    stream_URL = db.Column(db.String(100), nullable=False)



    def __repr__(self):  # when I want to see the representation of the object
        return f"Drone(status = {status}, landing_status = {landing_status}, battery = {battery}, drone_coords = {drone_coords}, stream_URL = {stream_URL})"


# User Model
class UserModel(db.Model): # define all the fields inside a drone model
    id = db.Column(db.Integer, primary_key=True) # primary_key=True means that each id will be different for all the drones
    user_coords = db.Column(db.String(100), nullable=False)
    availability_from = db.Column(db.String(100), nullable=False)
    availability_to = db.Column(db.String(100), nullable=False)
    # name_user = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a name
    # surname_user = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a name
    # document = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a name

    def __repr__(self):  # when I want to see the representation of the object
        return f"User(user_coords = {user_coords}, availability_from = {availability_from}, availability_to = {availability_to})"


# Assignment Model
class AssignmentModel(db.Model): # define all the fields inside a drone model
    id_user = db.Column(db.Integer, primary_key=True) # primary_key=True means that each id will be different for all the drones
    id_drone = db.Column(db.String(100), nullable=False)
    user_coords = db.Column(db.String(100), nullable=False)
    request_from = db.Column(db.String(100), nullable=False)
    request_to = db.Column(db.String(100), nullable=False)
    request_status = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a status


    def __repr__(self):  # when I want to see the representation of the object
        return f"Assignment(id_drone = {id_drone}, user_coords = {user_coords}, request_from = {request_from}, request_to = {request_to}, request_status = {request_status})"


# Mission Model
class MissionModel(db.Model): # define all the fields inside a drone model
    id_drone = db.Column(db.Integer, primary_key=True)
    path_coords = db.Column(db.String(100), nullable=False)
    mission_from = db.Column(db.String(100), nullable=False)
    mission_to = db.Column(db.String(100), nullable=False)
    covered_path = db.Column(db.String(100), nullable=False)
    uncovered_path = db.Column(db.String(100), nullable=False)
    uncovered_from = db.Column(db.String(100), nullable=False)
    uncovered_to = db.Column(db.String(100), nullable=False)
    mission_status = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a status


    def __repr__(self):  # when I want to see the representation of the object
        return f"Model(path_coords = {path_coords}, mission_from = {mission_from}, mission_to = {mission_to}, covered_path = {covered_path}, uncovered_path = {uncovered_path}, uncovered_from = {uncovered_from}, uncovered_to = {uncovered_to}, mission_status = {mission_status})"


# Addresses Model
class AddressesModel(db.Model): # define all the fields inside a address model
    id = db.Column(db.Integer, primary_key=True) # primary_key=True means that each id will be different for all the drones
    first_names = db.Column(db.String(100), nullable=False)
    last_names = db.Column(db.String(100), nullable=False)
    addresses = db.Column(db.String(100), nullable=False)
    cities = db.Column(db.String(100), nullable=False)
    states = db.Column(db.String(100), nullable=False)
    zipcodes = db.Column(db.String(100), nullable=False)
    coords = db.Column(db.String(100), nullable=False)
    days = db.Column(db.String(100), nullable=False)
    av_froms = db.Column(db.String(100), nullable=False)
    av_tos = db.Column(db.String(100), nullable=False)


    def __repr__(self):  # when I want to see the representation of the object
        return f"Addresses(first_names = {first_names}, last_names = {last_names}, addresses = {addresses}, cities = {cities}, states = {states}, zipcodes = {zipcodes} , coords = {coords} , days = {days} , av_froms = {av_froms} , av_tos = {av_tos})"



# Opt Model
class OptModel(db.Model): # define all the fields inside a drone model
    id = db.Column(db.Integer, primary_key=True) # primary_key=True means that each id will be different for all the drones
    target = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a status
    insp_time = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a status
    drone_point = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a status
    drone_coord = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a status


    def __repr__(self):  # when I want to see the representation of the object
        return f"OptModel(target = {target}, insp_time = {insp_time}, drone_point = {drone_point}, drone_path = {drone_path})"


# Which Model
class WhichModel(db.Model): # define all the fields inside a drone model
    id = db.Column(db.Integer, primary_key=True) # primary_key=True means that each id will be different for all the drones
    which = db.Column(db.String(100), nullable=False) # nullable=False means that each drone must have a status


    def __repr__(self):  # when I want to see the representation of the object
        return f"WhichModel(which = {which})"



db.create_all()  # creates the database: do this only the first time, otherwise the database will be reinitialised every time




# Drone Request Parser
drone_put_args = reqparse.RequestParser()  # parse the request and make sure it fits the guidelines and contains the correct data
# Request parser arguments that are mandatory to be sent
drone_put_args.add_argument("status", type=str, help="Status of the drone is required", required=True)  # if I insert required=True the server will crash if I do not obtain this info
drone_put_args.add_argument("landing_status", type=str, help="Landing status of the drone is required", required=True)
drone_put_args.add_argument("battery", type=str, help="Battery of the drone is required", required=True)
drone_put_args.add_argument("drone_coords", type=str, help="Drone coordinates are required", required=True)
drone_put_args.add_argument("stream_URL", type=str, help="URL stream of the drone is required", required=True)

# To update the drone
drone_update_args = reqparse.RequestParser()
drone_update_args.add_argument("status", type=str, help="Status of the drone is required")  # if I insert required=True the server will crash if I do not obtain this info
drone_update_args.add_argument("landing_status", type=str, help="Landing status of the drone is required")
drone_update_args.add_argument("battery", type=str, help="Battery of the drone is required")
drone_update_args.add_argument("drone_coords", type=str, help="Drone coordinates are required")
drone_update_args.add_argument("stream_URL", type=str, help="URL stream of the drone is required")



# User Request Parser
user_put_args = reqparse.RequestParser()  # parse the request and make sure it fits the guidelines and contains the correct data
# Request parser arguments that are mandatory to be sent
user_put_args.add_argument("user_coords", type=str, help="Coordinates of the user are required", required=True)  # if I insert required=True the server will crash if I do not obtain this info
user_put_args.add_argument("availability_from", type=str, help="Availability start of the user is required", required=True)
user_put_args.add_argument("availability_to", type=str, help="Availability end of the user is required", required=True)
# To update the user
user_update_args = reqparse.RequestParser()
user_update_args.add_argument("user_coords", type=str, help="Coordinates of the user are required")  # if I insert required=True the server will crash if I do not obtain this info
user_update_args.add_argument("availability_from", type=str, help="Availability start of the user is required")
user_update_args.add_argument("availability_to", type=str, help="Availability end of the user is required")



# Assignment Request Parser
assignment_put_args = reqparse.RequestParser()  # parse the request and make sure it fits the guidelines and contains the correct data
# Request parser arguments that are mandatory to be sent
assignment_put_args.add_argument("id_drone", type=str, help="Id of the drone is required", required=True)  # if I insert required=True the server will crash if I do not obtain this info
assignment_put_args.add_argument("user_coords", type=str, help="Coordinates of the user are required", required=True)  # if I insert required=True the server will crash if I do not obtain this info
assignment_put_args.add_argument("request_from", type=str, help="Start of the mission is required", required=True)
assignment_put_args.add_argument("request_to", type=str, help="End of the mission is required", required=True)
assignment_put_args.add_argument("request_status", type=str, help="Status of the mission is required", required=True)
# To update the user
assignment_update_args = reqparse.RequestParser()
assignment_update_args.add_argument("id_drone", type=str, help="Id of the drone is required")  # if I insert required=True the server will crash if I do not obtain this info
assignment_update_args.add_argument("user_coords", type=str, help="Coordinates of the user are required")  # if I insert required=True the server will crash if I do not obtain this info
assignment_update_args.add_argument("request_from", type=str, help="Start of the mission is required")
assignment_update_args.add_argument("request_to", type=str, help="End of the mission is required")
assignment_update_args.add_argument("request_status", type=str, help="Status of the mission is required")



# Mission Request Parser
mission_put_args = reqparse.RequestParser()  # parse the request and make sure it fits the guidelines and contains the correct data
# Request parser arguments that are mandatory to be sent
mission_put_args.add_argument("path_coords", type=str, help="Coordinates of the path are required", required=True)
mission_put_args.add_argument("mission_from", type=str, help="Start of the mission is required", required=True)
mission_put_args.add_argument("mission_to", type=str, help="End of the mission is required", required=True)
mission_put_args.add_argument("covered_path", type=str, help="Covered path subsection is required", required=True)
mission_put_args.add_argument("uncovered_path", type=str, help="Uncovered path is required", required=True)
mission_put_args.add_argument("uncovered_from", type=str, help="Start of the mission is required", required=True)
mission_put_args.add_argument("uncovered_to", type=str, help="End of the mission is required", required=True)
mission_put_args.add_argument("mission_status", type=str, help="Status of the mission is required", required=True)


# To update the mission
mission_update_args = reqparse.RequestParser()
mission_update_args.add_argument("path_coords", type=str, help="Coordinates of the path are required")
mission_update_args.add_argument("mission_from", type=str, help="Start of the mission is required")
mission_update_args.add_argument("mission_to", type=str, help="End of the mission is required")
mission_update_args.add_argument("covered_path", type=str, help="Covered path subsection is required")
mission_update_args.add_argument("uncovered_path", type=str, help="Uncovered path is required")
mission_update_args.add_argument("uncovered_from", type=str, help="Start of the mission is required")
mission_update_args.add_argument("uncovered_to", type=str, help="End of the mission is required")
mission_update_args.add_argument("mission_status", type=str, help="Status of the mission is required")



# Addresses Request Parser
addresses_put_args = reqparse.RequestParser()  # parse the request and make sure it fits the guidelines and contains the correct data
# Request parser arguments that are mandatory to be sent
addresses_put_args.add_argument("first_names", type=str, help="First name is required", required=True)  # if I insert required=True the server will crash if I do not obtain this info
addresses_put_args.add_argument("last_names", type=str, help="Last name is required", required=True)
addresses_put_args.add_argument("addresses", type=str, help="Address is required", required=True)
addresses_put_args.add_argument("cities", type=str, help="City is required", required=True)
addresses_put_args.add_argument("states", type=str, help="State is required", required=True)
addresses_put_args.add_argument("zipcodes", type=str, help="Zip code is required", required=True)
addresses_put_args.add_argument("coords", type=str, help="Coordinates are required", required=True)
addresses_put_args.add_argument("days", type=str, help="Day is required", required=True)
addresses_put_args.add_argument("av_froms", type=str, help="Availability from is required", required=True)
addresses_put_args.add_argument("av_tos", type=str, help="Availability to is required", required=True)

# To update the drone
addresses_update_args = reqparse.RequestParser()
addresses_update_args.add_argument("first_names", type=str, help="First name is required", required=True)  # if I insert required=True the server will crash if I do not obtain this info
addresses_update_args.add_argument("last_names", type=str, help="Last name is required", required=True)
addresses_update_args.add_argument("addresses", type=str, help="Address is required", required=True)
addresses_update_args.add_argument("cities", type=str, help="City is required", required=True)
addresses_update_args.add_argument("states", type=str, help="State is required", required=True)
addresses_update_args.add_argument("zipcodes", type=str, help="Zip code is required", required=True)
addresses_update_args.add_argument("coords", type=str, help="Coordinates are required", required=True)
addresses_update_args.add_argument("days", type=str, help="Day is required", required=True)
addresses_update_args.add_argument("av_froms", type=str, help="Availability from is required", required=True)
addresses_update_args.add_argument("av_tos", type=str, help="Availability to is required", required=True)


# Opt Request Parser
opt_put_args = reqparse.RequestParser()  # parse the request and make sure it fits the guidelines and contains the correct data
# Request parser arguments that are mandatory to be sent
opt_put_args.add_argument("target", type=str, help="Target is required", required=True)  # if I insert required=True the server will crash if I do not obtain this info
opt_put_args.add_argument("insp_time", type=str, help="Inspection time is required", required=True)  # if I insert required=True the server will crash if I do not obtain this info
opt_put_args.add_argument("drone_point", type=str, help="Drone_point is required", required=True)  # if I insert required=True the server will crash if I do not obtain this info
opt_put_args.add_argument("drone_coord", type=str, help="Drone_coord is required", required=True)  # if I insert required=True the server will crash if I do not obtain this info

# To update the opt
opt_update_args = reqparse.RequestParser()
opt_update_args.add_argument("target", type=str, help="Target is required")  # if I insert required=True the server will crash if I do not obtain this info
opt_update_args.add_argument("insp_time", type=str, help="Inspection time is required")  # if I insert required=True the server will crash if I do not obtain this info
opt_update_args.add_argument("drone_point", type=str, help="Drone_point is required")  # if I insert required=True the server will crash if I do not obtain this info
opt_update_args.add_argument("drone_coord", type=str, help="Drone_coord is required")  # if I insert required=True the server will crash if I do not obtain this info


# Which Request Parser
which_put_args = reqparse.RequestParser()  # parse the request and make sure it fits the guidelines and contains the correct data
# Request parser arguments that are mandatory to be sent
which_put_args.add_argument("which", type=str, help="Which drone is required", required=True)  # if I insert required=True the server will crash if I do not obtain this info

# To update the which
which_update_args = reqparse.RequestParser()
which_update_args.add_argument("which", type=str, help="Which drone is required")  # if I insert required=True the server will crash if I do not obtain this info


# Drone Dictionary
resource_drone = { # to serialize an object since when dealing with databases I can have more drones with same info
    'id': fields.Integer,
    'status': fields.String,
    'landing_status': fields.String,
    'battery': fields.String,
    'drone_coords': fields.String,
    'stream_URL': fields.String

}


# User Dictionary
resource_user = { # to serialize an object since when dealing with databases I can have more drones with same info
    'id': fields.Integer,
    'user_coords': fields.String,
    'availability_from': fields.String,
    'availability_to': fields.String
}


# Assignment Dictionary
resource_assignment = { # to serialize an object since when dealing with databases I can have more drones with same info
    'id_user': fields.Integer,
    'id_drone': fields.String,
    'user_coords': fields.String,
    'request_from': fields.String,
    'request_to': fields.String,
    'request_status': fields.String
}


# Mission Dictionary
resource_mission = { # to serialize an object since when dealing with databases I can have more drones with same info
    'id_drone': fields.Integer,
    'path_coords': fields.String,
    'mission_from': fields.String,
    'mission_to': fields.String,
    'covered_path': fields.String,
    'uncovered_path': fields.String,
    'uncovered_from': fields.String,
    'uncovered_to': fields.String,
    'mission_status': fields.String

}


# Addresses Dictionary
resource_addresses = { # to serialize an object since when dealing with databases I can have more drones with same info
    'id': fields.Integer,
    'first_names': fields.String,
    'last_names': fields.String,
    'addresses': fields.String,
    'cities': fields.String,
    'states': fields.String,
    'zipcodes': fields.String,
    'coords': fields.String,
    'days': fields.String,
    'av_froms': fields.String,
    'av_tos': fields.String

}


# Opt Dictionary
resource_opt = { # to serialize an object since when dealing with databases I can have more drones with same info
    'id': fields.Integer,
    'target': fields.String,
    'insp_time': fields.String,
    'drone_point': fields.String,
    'drone_coord': fields.String,

}


# Which Dictionary
resource_which = { # to serialize an object since when dealing with databases I can have more drones with same info
    'id': fields.Integer,
    'which': fields.String

}



# Initialize the drone class
class Drone(Resource):
    # marshal_with is a decorator to put before each method that I want its return to be a serialized object
    @marshal_with(resource_drone)  # when we return, takes the return value and serialize it using the above field resource_fields
    def get(self, drone_id):  # get request
        result = DroneModel.query.filter_by(id=drone_id).first()  # search for an id filterning all the drones and return the first response in that filter. Do .all() to get all of them
        if not result:  # if no id for this drone
            abort(404, message="Could not find drone with this id...")

        return result# I'll receive all the info about my request


    # put() to insert a drone
    @marshal_with(resource_drone)
    def put(self, drone_id):
        args = drone_put_args.parse_args()
        result = DroneModel.query.filter_by(id=drone_id).first()
        if result:  # if result already exists
            abort(409, message="Drone id already taken...")

        drone = DroneModel(id=drone_id, status=args['status'], landing_status=args['landing_status'], battery=args['battery'], drone_coords=args['drone_coords'], stream_URL=args['stream_URL'])
        db.session.add(drone) # add the drone to the current database session
        db.session.commit()  # commit all the changes I have done on the database and make them permanent
        return drone, 201  # add the status code to the specific returned data


    # patch() to update
    @marshal_with(resource_drone)
    def patch(self, drone_id):  # update
        args = drone_update_args.parse_args()
        result = DroneModel.query.filter_by(id=drone_id).first()
        if not result:  # if result already exists
            abort(404, message="Drone doesn't exist, cannot update...")

        if  args['status']:  # cioè :  "status" in args and args['status'] not None  ovvero if this args are not none
            result.status = args['status']
        if args['landing_status']:
            result.landing_status = args['landing_status']
        if args['battery']:
            result.battery = args['battery']
        if args['drone_coords']:
            result.drone_coords = args['drone_coords']
        if args['stream_URL']:
            result.stream_URL = args['stream_URL']    


        db.session.commit()

        return result



    # delete() to remove a drone
    @marshal_with(resource_drone)
    def delete(self, drone_id):
        result = DroneModel.query.get(drone_id)
        if not result:  # if result already exists
            abort(404, message="Drone doesn't exist, cannot delete...")
        else:
            db.session.delete(result)
            db.session.commit()
        return '', 204  # blank string, able to delete



# Initialize the user class
class User(Resource):
    # marshal_with is a decorator to put before each method that I want its return to be a serialized object
    @marshal_with(resource_user)  # when we return, takes the return value and serialize it using the above field resource_fields
    def get(self, user_id):  # get request
        result = UserModel.query.filter_by(id=user_id).first()  # search for an id filterning all the drones and return the first response in that filter. Do .all() to get all of them
        if not result:  # if no id for this user
            abort(404, message="Could not find user with this id...")

        return result# I'll receive all the info about my request


    # put() to insert a user
    @marshal_with(resource_user)
    def put(self, user_id):
        args = user_put_args.parse_args()
        result = UserModel.query.filter_by(id=user_id).first()
        if result:  # if result already exists
            abort(409, message="User id already taken...")

        user = UserModel(id=user_id, user_coords=args['user_coords'], availability_from=args['availability_from'], availability_to=args['availability_to'])
        db.session.add(user) # add the user to the current database session
        db.session.commit()  # commit all the changes I have done on the database and make them permanent
        return user, 201  # add the status code to the specific returned data


    # patch() to update
    @marshal_with(resource_user)
    def patch(self, user_id):  # update
        args = user_update_args.parse_args()
        result = UserModel.query.filter_by(id=user_id).first()
        if not result:  # if result already exists
            abort(404, message="User doesn't exist, cannot update...")

        if  args['user_coords']:  # cioè :  "name" in args and args['name'] not None  ovvero if this args are not none
            result.user_coords = args['user_coords']
        if args['availability_from']:
            result.availability_from = args['availability_from']
        if args['availability_to']:
            result.availability_to = args['availability_to']


        db.session.commit()

        return result



    # delete() to remove a user
    @marshal_with(resource_user)
    def delete(self, user_id):
        result = UserModel.query.get(user_id)
        if not result:  # if result already exists
            abort(404, message="User doesn't exist, cannot delete...")
        else:
            db.session.delete(result)
            db.session.commit()
        return '', 204  # blank string, able to delete



# Initialize the assignment class
class Assignment(Resource):
    # marshal_with is a decorator to put before each method that I want its return to be a serialized object
    @marshal_with(resource_assignment)  # when we return, takes the return value and serialize it using the above field resource_fields
    def get(self, id_user):  # get request
        result = AssignmentModel.query.filter_by(id_user=id_user).first()  # search for an id filterning all the drones and return the first response in that filter. Do .all() to get all of them
        if not result:  # if no id for this assignment
            abort(404, message="Could not find assignment with this id user...")

        return result# I'll receive all the info about my request


    # put() to insert a assignment
    @marshal_with(resource_assignment)
    def put(self, id_user):
        args = assignment_put_args.parse_args()
        result = AssignmentModel.query.filter_by(id_user=id_user).first()
        if result:  # if result already exists
            abort(409, message="Assignment id already taken...")

        assignment = AssignmentModel(id_user=id_user, id_drone=args['id_drone'], user_coords=args['user_coords'], request_from=args['request_from'], request_to=args['request_to'], request_status=args['request_status'])
        db.session.add(assignment) # add the assignment to the current database session
        db.session.commit()  # commit all the changes I have done on the database and make them permanent
        return assignment, 201  # add the status code to the specific returned data



    # patch() to update
    @marshal_with(resource_assignment)
    def patch(self, id_user):  # update
        args = assignment_update_args.parse_args()
        result = AssignmentModel.query.filter_by(id_user=id_user).first()
        if not result:  # if result already exists
            abort(404, message="Assignment doesn't exist, cannot update...")

        if  args['id_drone']:  # cioè :  "name" in args and args['name'] not None  ovvero if this args are not none
            result.id_drone = args['id_drone']
        if  args['user_coords']: 
            result.user_coords = args['user_coords']    
        if args['request_from']:
            result.request_from = args['request_from']
        if args['request_to']:
            result.request_to = args['request_to']
        if args['request_status']:
            result.request_status = args['request_status']


        db.session.commit()

        return result


    # delete() to remove an assignment
    @marshal_with(resource_assignment)
    def delete(self, id_user):
        result = AssignmentModel.query.get(id_user)
        if not result:  # if result already exists
            abort(404, message="Assignment doesn't exist, cannot delete...")
        else:
            db.session.delete(result)
            db.session.commit()
        return '', 204  # blank string, able to delete



# Initialize the mission class
class Mission(Resource):
    # marshal_with is a decorator to put before each method that I want its return to be a serialized object
    @marshal_with(resource_mission)  # when we return, takes the return value and serialize it using the above field resource_fields
    def get(self, id_drone):  # get request
        result = MissionModel.query.filter_by(id_drone=id_drone).first()  # search for an id filterning all the drones and return the first response in that filter. Do .all() to get all of them
        if not result:  # if no id for this mission
            abort(404, message="Could not find drone with this id...")

        return result# I'll receive all the info about my request


    # put() to insert a mission
    @marshal_with(resource_mission)
    def put(self, id_drone):
        args = mission_put_args.parse_args()
        result = MissionModel.query.filter_by(id_drone=id_drone).first()
        if result:  # if result already exists
            abort(409, message="Mission id already taken...")

        mission = MissionModel(id_drone=id_drone, path_coords=args['path_coords'], mission_from=args['mission_from'], mission_to=args['mission_to'], covered_path=args['covered_path'], uncovered_path=args['uncovered_path'], uncovered_from=args['uncovered_from'], uncovered_to=args['uncovered_to'], mission_status=args['mission_status'])
        db.session.add(mission) # add the mission to the current database session
        db.session.commit()  # commit all the changes I have done on the database and make them permanent
        return mission, 201  # add the status code to the specific returned data



    # patch() to update
    @marshal_with(resource_mission)
    def patch(self, id_drone):  # update
        args = mission_update_args.parse_args()
        result = MissionModel.query.filter_by(id_drone=id_drone).first()
        if not result:  # if result already exists
            abort(404, message="Drone doesn't exist, cannot update...")

        if args['path_coords']:
            result.path_coords = args['path_coords']
        if args['mission_from']:
            result.mission_from = args['mission_from']
        if args['mission_to']:
            result.mission_to = args['mission_to']
        if args['covered_path']:
            result.covered_path = args['covered_path'] 
        if args['uncovered_path']:
            result.uncovered_path = args['uncovered_path']
        if args['uncovered_from']:
            result.uncovered_from = args['uncovered_from']
        if args['uncovered_to']:
            result.uncovered_to = args['uncovered_to']
        if args['mission_status']:
            result.mission_status = args['mission_status']
        

        db.session.commit()

        return result


    # delete() to remove a mission
    @marshal_with(resource_mission)
    def delete(self, id_drone):
        result = MissionModel.query.get(id_drone)
        if not result:  # if result already exists
            abort(404, message="Drone doesn't exist, cannot delete...")
        else:
            db.session.delete(result)
            db.session.commit()
        return '', 204  # blank string, able to delete




# Initialize the addresses class
class Addresses(Resource):
    # marshal_with is a decorator to put before each method that I want its return to be a serialized object
    @marshal_with(resource_addresses)  # when we return, takes the return value and serialize it using the above field resource_fields
    def get(self):  # get request
        result = AddressesModel.query.all()  # search for an id filterning all the addresses and return the first response in that filter. Do .all() to get all of them
        return result# I'll receive all the info about my request


    # put() to insert a addresses
    @marshal_with(resource_addresses)
    def put(self):
        args = addresses_put_args.parse_args()
        result = AddressesModel.query.all()

        addresses = AddressesModel(first_names=args['first_names'], last_names=args['last_names'], addresses=args['addresses'], cities=args['cities'], states=args['states'], zipcodes=args['zipcodes'], coords=args['coords'], days=args['days'], av_froms=args['av_froms'], av_tos=args['av_tos'])
        db.session.add(addresses) # add the addresses to the current database session
        db.session.commit()  # commit all the changes I have done on the database and make them permanent
        return addresses, 201  # add the status code to the specific returned data


    # # patch() to update
    # @marshal_with(resource_addresses)
    # def patch(self, addresses_id):  # update
    #     args = addresses_update_args.parse_args()
    #     result = AddressesModel.query.filter_by(id=addresses_id).first()
    #     if not result:  # if result already exists
    #         abort(404, message="Address doesn't exist, cannot update...")

    #     if  args['first_names']:  
    #         result.first_names = args['first_names']
    #     if args['last_names']:
    #         result.last_names = args['last_names']
    #     if args['addresses']:
    #         result.addresses = args['addresses']
    #     if args['cities']:
    #         result.cities = args['cities']
    #     if args['states']:
    #         result.states = args['states']   
    #     if args['zipcodes']:
    #         result.zipcodes = args['zipcodes']      
    #     if args['coords']:
    #         result.coords = args['coords'] 
    #     if args['days']:
    #         result.days = args['days'] 
    #     if args['av_froms']:
    #         result.av_froms = args['av_froms'] 
    #     if args['av_tos']:
    #         result.av_tos = args['av_tos']     

    #     db.session.commit()

    #     return result



    # # delete() to remove a addresses
    # @marshal_with(resource_addresses)
    # def delete(self, addresses_id):
    #     result = AddressesModel.query.get(addresses_id)
    #     if not result:  # if result already exists
    #         abort(404, message="Address doesn't exist, cannot delete...")
    #     else:
    #         db.session.delete(result)
    #         db.session.commit()
    #     return '', 204  # blank string, able to delete


# Initialize the opt class
class Opt(Resource):
    # marshal_with is a decorator to put before each method that I want its return to be a serialized object
    @marshal_with(resource_opt)  # when we return, takes the return value and serialize it using the above field resource_fields
    def put(self):
        args = opt_put_args.parse_args()
        result = OptModel.query.all()
        
        # Save the parameters passed during the put call
        my_target = args['target']
        my_insp_time = args['insp_time']

        opt = OptModel(target=args['target'], insp_time=args['insp_time'], drone_point=args['drone_point'], drone_coord=args['drone_coord'])
        db.session.add(opt) # add the drone to the current database session
        db.session.commit()  # commit all the changes I have done on the database and make them permanent

        # Manage the target input to be pass to the evaluate_path function
        my_target = my_target.split(";")
        my_target_x = my_target[0]
        my_target_y = my_target[1]
        my_target_x = my_target_x.split(",")
        my_target_y = my_target_y.split(",")

        # Initialize empty vectors and fill them in the for loop
        target_x = []
        target_y = []
        for i in range(len(my_target_x)):
            target_x.append(int(my_target_x[i]))
        for j in range(len(my_target_y)):
            target_y.append(int(my_target_y[j]))  
        
        insp_time = int(my_insp_time)
        
        # Call the opt function
        dictionaries = evaluate_path(target_x, target_y, insp_time)   
        drone_point_dict = dictionaries[0] 
        drone_coord_dict = dictionaries[1]  
        opt = OptModel(target=args['target'], insp_time=args['insp_time'], drone_point=drone_point_dict, drone_coord=drone_coord_dict)
        db.session.add(opt) # add the drone to the current database session
        db.session.commit()  # commit all the changes I have done on the database and make them permanent


        return opt, 201  # add the status code to the specific returned data
     
     # COME FACCIO A FARE RITORNARE ANCHE IL DICTIONARY ??


    @marshal_with(resource_opt)  # when we return, takes the return value and serialize it using the above field resource_fields
    def get(self):  # get request
        result = OptModel.query.all()  # search for an id filterning all the addresses and return the first response in that filter. Do .all() to get all of them
        return result# I'll receive all the info about my request



# Initialize the addresses class
class Which(Resource):
    # marshal_with is a decorator to put before each method that I want its return to be a serialized object
    @marshal_with(resource_which)  # when we return, takes the return value and serialize it using the above field resource_fields
    def get(self):  # get request
        result = WhichModel.query.all()  # search for an id filterning all the addresses and return the first response in that filter. Do .all() to get all of them
        return result# I'll receive all the info about my request


    # put() to insert a addresses
    @marshal_with(resource_which)
    def put(self):
        args = which_put_args.parse_args()
        result = WhichModel.query.all()

        which = WhichModel(which=args['which'])
        db.session.add(which) # add the addresses to the current database session
        db.session.commit()  # commit all the changes I have done on the database and make them permanent
        return which, 201  # add the status code to the specific returned data




# whatever value is going to be put after drone/ it is going to be the drone_id inside the dictionary
# and it is gointo to be associated with the passed data
api.add_resource(Drone, "/drone/<int:drone_id>")  # my key
api.add_resource(User, "/user/<int:user_id>")  # my key
api.add_resource(Assignment, "/assignment/<int:id_user>")  # my key
api.add_resource(Mission, "/mission/<int:id_drone>")  # my key
api.add_resource(Addresses, "/addresses")  # my key
api.add_resource(Opt, "/opt")  # my key
api.add_resource(Which, "/which")  # my key



# Start our Flask application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    # app.run(debug=True)
