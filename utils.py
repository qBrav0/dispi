from telebot.handler_backends import State, StatesGroup 
from SQLighter import SQLighter
from config import database_name

class UserStates(StatesGroup):
    '''Class for defining states'''

    #General states
    start_menu = State()
    сheck_for_registration_or_login = State()
    confirm_registration = State()

    #Entering states
    enter_login = State()
    enter_password = State()

    #Registration states
    reg_login = State()
    reg_password = State()
    reg_telegram_username = State()

    reg_first_name = State()
    reg_surname = State()
    reg_patronymic = State()


class Lists:
    """Class for lists:
    list of members,
    list of projects, 
    list of connection betwen members and projects"""

    def __init__(self):
        self.members_list = get_members_list()
        self.projects_list = get_projects_list()
        self.members_to_projects_list = get_members_to_projects_list()

    def return_members(self):
        return self.members_list
    
    def return_projects(self):
        return self.projects_list
    
    def return_members_to_projects(self):
        return self.members_to_projects_list
    
    def update_all_lists(self):
        self.members_list = get_members_list()
        self.projects_list = get_projects_list()
        self.members_to_projects_list = get_members_to_projects_list()

    def login_exist(self, login):
        '''Checks if such a login exists'''
        for member in self.members_list:
            if member[1] == login:
                return True
        return False

    def get_password_for_login(self, login ):
        '''Returns the password for the given login'''
        for member in self.members_list:
            if member[1] == login:
                return member[2]

def get_members_list():
    '''Getting members list
    Returns:
      list of members - list'''
    db = SQLighter(database_name)
    members_list = db.select_all_members()
    db.close()
    return members_list

def get_projects_list():
    '''Getting projects list
    Returns:
      list of projects - list'''
    db = SQLighter(database_name)
    projects_list = db.select_all_projects()
    db.close()
    return projects_list

def get_members_to_projects_list():
    '''Getting members to projects list
    Returns:
      list of connection members to projects - list'''
    db = SQLighter(database_name)
    members_to_projects_list = db.select_members_to_projects()
    db.close()
    return members_to_projects_list

def register_new_member(member):
    db = SQLighter(database_name)
    db.add_member(member['reg_login'],member['reg_password'],member['reg_telegram_username'])
    db.close()
