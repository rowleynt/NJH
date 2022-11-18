import os
import mysql.connector
from time import sleep
from datetime import date
from User import User
from pokemontcgsdk import *

# TODO: add bio column to user table (varchar[255]), allow users to set their own bio from within the program
#  add bio to profile
#  a lot of other stuff


def main():
    njh = connect_to_db()  # connect to mySQL database
    state = "GUEST"  # begin in logged out state
    stop_code = 0  # used to exit program
    curr_user = 0  # initialize curr_user outside of loop, so it can be used anywhere
    clear_screen()
    while stop_code != 1:  # loop runs until user enters 4
        if state == "GUEST":  # do this if user not logged in
            clear_screen()
            print("[1]>login [2]>register [3]>search [4]>exit")
            choice = eval(input())

            match choice:
                case 1:  # log in user
                    curr_user = login_user(njh)
                    state = "LOGGED IN"
                case 2:  # register user, log in as new user
                    curr_user = register_user(njh)
                    state = "LOGGED IN"
                case 3:  # do search function
                    result = search(njh)
                    print(result)
                    input()  # wait for user input to erase search result
                case 4:  # exits program
                    stop_code = 1
                case _:  # wildcard
                    print("Invalid input")
                    sleep(0.3)
            clear_screen()
        if state == "LOGGED IN":  # do this if user has logged in
            clear_screen()
            print("LOGGED IN AS", curr_user.getUsername())
            print("[1]>log out [2]>search [3]>view your profile [4]>follow other user [5]>exit ")
            choice = eval(input())
            match choice:
                case 1:  # log out
                    state = "GUEST"
                case 2:  # search cards or users
                    result = search(njh)
                    print(result)
                    input()
                case 3:  # view your profile
                    clear_screen()
                    display_profile(curr_user, njh)
                    input("\n<[Go Back]")
                case 4:
                    follow_user(njh, curr_user)
                case 5:  # exit program
                    stop_code = 1
                case _:  # wildcard
                    print("Invalid input")
                    sleep(0.3)


def connect_to_db():
    """Connects to MySQL database with given attributes"""
    db = mysql.connector.connect(host="localhost", user="root", password="password", database="njh")
    return db


# TODO: fix bug when no users exist
# TODO: disallow spaces in username and password
# TODO: disallow duplicate usernames
def register_user(db):
    """Takes user input and adds a new row to the passed database. Dynamically assigns new userID to
    every new user. WIP"""
    clear_screen()

    print("<Register>")
    username = input("Username: ")
    password = input("Password: ")

    clear_screen()

    c = db.cursor()  # access database
    c.execute("SELECT userID FROM user")  # SQL query
    new_id = c.fetchall()[-1][0] + 1  # fetches userID from last row, adds 1, assigns to new_id
    today = date.today().strftime("%Y-%m-%d")  # gets today's date for use in User object
    sql = "INSERT INTO user (userID, username, pass, joinDate) VALUES (%s, %s, %s, %s)"
    val = (new_id, username, password, today)
    c.execute(sql, val)  # execute query

    db.commit()  # commit changes to database
    c.execute(f"SELECT * FROM user WHERE userID = {new_id}")
    return create_user(c.fetchall()[0])  # returns User object using row with userID = new_id


def login_user(db):
    """Takes input from user and matches it to information pulled from the passed database. Fails if no matching
    information found in database"""
    clear_screen()
    good_input = False
    c = db.cursor()  # access database

    while not good_input:  # exit when good_input = True
        print("<Log In>")
        username = input("Username: ")
        password = input("Password: ")
        temp = (username, password)  # temporary tuple to hold user input

        clear_screen()

        c.execute("SELECT username, pass FROM user")  # gets all columns 'username' and 'pass' from user table
        fetch = c.fetchall()  # fetch data from above query
        if temp in fetch:  # checks for a database row matching temp (username, password)
            good_input = True  # exit loop
        else:  # database row not found
            print("Username or password incorrect.")
        c.execute(f"SELECT userID, username, joinDate FROM user WHERE username = \"{temp[0]}\"")
    return create_user(c.fetchall()[0])  # returns User object from row with given username (usernames will be unique)


def follow_user(db, current):
    """Updates followers table in database with a new id (max + 1), target_id (who is being followed) and
    follow_id (user doing the following"""
    clear_screen()
    target = input("Username of user to follow: ")
    targetID = -1
    c = db.cursor()
    goodInput = False
    while not goodInput:
        c.execute(f"SELECT userID, username FROM user WHERE username = \'{target}\'")
        fetch = c.fetchall()[0]
        if target in fetch:
            targetID = fetch[0]
            goodInput = True
        else:
            print("Target user not found")
    c.execute(f"SELECT id FROM followers")
    id_next = c.fetchall()[-1][0] + 1
    c.execute(f"INSERT INTO followers (id, target_id, follow_id) VALUES ({id_next}, {targetID}, {current.getUserID()});")
    db.commit()


# TODO: make search functionality smarter, implement while loop to check for good input
def search(db):
    """Search module, very WIP"""
    clear_screen()
    print("[1]>search cards [2]>search users")
    choice = eval(input())
    match choice:
        case 1:  # filtered search
            clear_screen()
            print("[1]>by name [2]>by set [3]>by rarity [4]>by supertype")
            s_choice = eval(input())
            # TODO: almost everything
            match s_choice:
                case 1:  # by name
                    s_input = input("Search [name]: ")
                    s_result = Card.where(q=f"name:{s_input}*")  # works
                    return s_result
                case 2:  # by set
                    s_input = input("Search [set]: ")
                    s_result = Card.where(q=f"set.name:{s_input}*")  # works
                    return s_result
                case 3:  # by rarity
                    s_input = input("Search [rarity]: ")
                    s_result = Card.where(q=f"rarity:{s_input}*")  # might work, don't use in demo
                    return s_result
                case 4:  # by supertype
                    s_input = input("Search [supertype]: ")
                    s_result = Card.where(q=f"supertype:{s_input}*")  # works
                    return s_result
                case _:  # wildcard
                    print("invalid input")
        case 2:  # search user # need to press enter twice to go back for some reason
            clear_screen()
            user = user_search_helper(db)
            display_profile(user, db)
            input("\n<[Go Back]")
        case _:  # wildcard
            print("invalid input")


def clear_screen():
    """Clears the terminal and prints <Nurse Joy's Handbook> at the top"""
    os.system('cls')
    print("<Nurse Joy's Handbook>\n")


def create_user(user_data):
    """Builds and returns new User object from passed user data"""
    uid = user_data[0]  # first item in tuple
    name = user_data[1]  # second item in tuple
    jdate = user_data[2]  # fourth item in tuple (skips password column)
    return User(uid, name, jdate)  # create new User object with given parameters


def user_search_helper(db):
    """Gets user data from database and builds and returns User object"""
    clear_screen()
    s_input = input("Username: ")
    clear_screen()
    c = db.cursor()  # access database
    c.execute(f"SELECT userID, username, joinDate FROM user WHERE username = \"{s_input}\"")
    user = create_user(c.fetchall()[0])  # create new User object from database row
    return user


def display_profile(user, db):
    """Displays information of the passed User object"""
    followers = []
    c = db.cursor()
    c.execute(f"SELECT follow_id FROM followers WHERE target_id = {user.getUserID()}")
    temp = c.fetchall()
    for ID in temp:
        c.execute(f"SELECT username FROM user WHERE userID = {ID[0]}")
        target_name = c.fetchall()[0][0]
        followers.append(target_name)

    print(f"Viewing profile of user: {user.getUsername()}")
    print(f"\n>Default bio\n\nCurrent Decks: 0\n\nCurrent Wishlists: 0\n"
          f"\nFollowers: {followers}\n\nJoined On: {user.getJoinDate()}")


if __name__ == "__main__":
    main()
