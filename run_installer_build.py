import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.state import InstallerState
from actions.set_env import SetEnvVariables
from actions.query_db import QueryDBAction
from actions.msi import InstallerBuildMSIAction
from actions.create_cabs import CreateCabsAction
from actions.make_pfw import InstallerMakePFWAction

# --- Options/configs setup ---
class Options:
    skipgoals = []
    debugbuild = False
    local = False
    # Set required installer variables
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'example_project'))
    cpu = 'x86'
    main_root = root_path
    bindirname = 'bin'
    project_bin = os.path.join(root_path, 'bin')
    project_name = 'ExampleApp'
    # Output directory configuration
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'out'))
    # Add more as needed for your actions

# Ensure output directory exists
if not os.path.exists(Options.output_dir):
    os.makedirs(Options.output_dir)
    print(f"Created output directory: {Options.output_dir}")

opts = Options()
args = []
configs = None  # Load or set as needed

# --- Initialize state machine ---
state = InstallerState(opts, args, configs)

# --- Set up goals and goal_map ---
state.goals = [
    'setenv',
    'query_db',
    'create_cabs',
    'buildmsi',
    'make_pfw'
]
state.goal_map = {
    'setenv': SetEnvVariables,
    'query_db': QueryDBAction,
    'buildmsi': InstallerBuildMSIAction,
    'create_cabs': CreateCabsAction,
    'make_pfw': InstallerMakePFWAction
}

state.finalize_goals()

# --- Run all actions ---
while state.has_more_goals():
    state.next_action()

print(f"Build complete. Check {opts.output_dir} for installer files.")
