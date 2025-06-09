from core.action import InstallerAction
from actions.msi import InstallerBuildMSIAction
from actions.make_pfw import InstallerMakePFWAction
from actions.set_env import SetEnvVariables
from actions.validate_msi import ValidateMSIAction
from actions.create_cabs import CreateCabsAction
from actions.query_db import QueryDBAction

import logging

logger = logging.getLogger('sfnrpack20')

def config_options(cfg):
    # TODO: add any config options you want to test here...
    pass
    
def modify_goals(goals, goal_map):

    del goals[:]
    goal_map.clear()

    goal_map['setenv']=SetEnvVariables
    goal_map['buildmsi'] = InstallerBuildMSIAction
    goal_map['make_pfw'] = InstallerMakePFWAction
    goal_map['clean_installer'] = CleanInstallerAction
    goal_map['validate_msi'] = ValidateMSIAction
    goal_map['create_cabs'] = CreateCabsAction
    goal_map['query_db'] = QueryDBAction

    
    goals.append('setenv')
    goals.append('query_db')
    goals.append('buildmsi')
    goals.append('validate_msi')
    goals.append('create_cabs')
    goals.append('make_pfw')