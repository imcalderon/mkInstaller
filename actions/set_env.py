from core.action import InstallerAction
import logging
import os
import uuid
import time

logger = logging.getLogger("installer.actions.setenv")

def query_user(question):
    valid = {"yes": True, "y": True, "no": False, "n": False}
    prompt = " [Y/n]? "
    while True:
        choice = input(question + prompt).lower()
        if choice == '' or choice in valid:
            return valid.get(choice, True)
        else:
            print(prompt, end='')

def xstr(s):
    return '' if s is None else str(s)

class SetEnvVariables(InstallerAction):
    name = 'setenv'

    def do(self, state):
        self.set_env(state)
        self.validate_queried_data(state)
        self.print_info(state)

    def set_env(self, state):
        # Use options if present, but preserve if already set (e.g. by load_manifest)
        if not getattr(state.library, 'root_path', None):
            state.library.root_path = getattr(state.library.options, 'root_path', None) or os.environ.get('ROOT_PATH', '')
            
        if not getattr(state.library, 'cpu', None):
            state.library.cpu = getattr(state.library.options, 'cpu', None) or os.environ.get('CPU', 'x86').lower()
            
        if not getattr(state.library, 'main_root', None):
            state.library.main_root = getattr(state.library.options, 'main_root', None) or os.environ.get('MAIN_ROOT', '')
            
        if not getattr(state.library, 'bindirname', None):
            state.library.bindirname = getattr(state.library.options, 'bindirname', None) or os.environ.get('BINDIRNAME', '')
            
        if not getattr(state.library, 'project_bin', None):
            state.library.project_bin = getattr(state.library.options, 'project_bin', None) or os.environ.get('PROJECT_BIN', '')
            
        if not getattr(state.library, 'project_name', None):
            state.library.project_name = getattr(state.library.options, 'project_name', None) or os.environ.get('PROJECT_NAME', '')
            
        # These are usually cleared/initialized at start of build
        if not hasattr(state.library, 'features'): state.library.features = []
        if not hasattr(state.library, 'components'): state.library.components = []
        # Note: we don't clear 'files' if already present (loaded from manifest)
        if not hasattr(state.library, 'files'): state.library.files = []
        
        if not hasattr(state.library, 'directories'): state.library.directories = []
        if not hasattr(state.library, 'custom_actions'): state.library.custom_actions = []
        if not hasattr(state.library, 'shortcuts'): state.library.shortcuts = []
        if not hasattr(state.library, 'icons'): state.library.icons = []
        if not hasattr(state.library, 'media'): state.library.media = []
        if not hasattr(state.library, 'new_components'): state.library.new_components = []
        
        if not getattr(state.library, 'targetbin', None):
            state.library.targetbin = getattr(state.library.options, 'targetbin', None) or os.path.join(state.library.root_path, state.library.bindirname)
        
        state.library.build_number = 0

    def validate_queried_data(self, state):
        # Example: validate required fields
        required = [
            'cpu', 'root_path', 'project_bin', 'targetbin'
        ]
        for attr in required:
            if not getattr(state.library, attr, None):
                raise Exception(f"state.library.{attr} is NULL or empty.")

    def print_info(self, state):
        logging.warning("-------------------------- Installer Machine -------------------------------")
        logging.warning("----------------------------------------------------------------------------")
        logging.warning(time.asctime(time.localtime(time.time())))
        logging.warning(" cpu type    : " + state.library.cpu)
        logging.warning(" root path   : " + state.library.root_path)
        logging.warning(" project bin : " + state.library.project_bin)
        logging.warning(" target bin  : " + state.library.targetbin)
        logging.warning(" skip options: " + str(getattr(state.library.options, 'skipgoals', None)))
        logging.warning("----------------------------------------------------------------------------")
