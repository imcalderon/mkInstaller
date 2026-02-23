import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.state import InstallerState
from actions.set_env import SetEnvVariables
from actions.query_db import QueryDBAction
from actions.load_manifest import LoadManifestAction
from actions.msi import InstallerBuildMSIAction
from actions.create_cabs import CreateCabsAction
from actions.make_pfw import InstallerMakePFWAction

def main():
    parser = argparse.ArgumentParser(description='Build Windows Installer')
    parser.add_argument('--manifest', help='Path to JSON manifest file (project-agnostic mode)')
    parser.add_argument('--project', default='ExampleApp', help='Project name (for DB mode)')
    parser.add_argument('--root', help='Root path for project files')
    parser.add_argument('--out', help='Output directory')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # --- Options setup ---
    class Options:
        skipgoals = []
        debugbuild = args.verbose
        local = True
        project_name = args.project
        manifest = args.manifest
        
        # Paths
        root_path = os.path.abspath(args.root) if args.root else os.getcwd()
        output_dir = os.path.abspath(args.out) if args.out else os.path.abspath('out')
        
        # ModernArchive path (auto-patched by devenv if needed)
        archive_exe = r'C:\Users\ivanm\ModernArchive\build\archive-2.0.0.exe'

    opts = Options()
    
    # Ensure output directory exists
    if not os.path.exists(opts.output_dir):
        os.makedirs(opts.output_dir)
        logging.info(f"Created output directory: {opts.output_dir}")

    # --- Initialize state machine ---
    # We pass opts as the 'options' object
    state = InstallerState(opts, {}, {})
    
    # Initialize core vars in the library so they are available via __getattr__
    state.library.project_name = opts.project_name
    state.library.root_path = opts.root_path
    state.library.output_dir = opts.output_dir

    # --- Set up goals ---
    state.goals = []
    state.goal_map = {
        'setenv': SetEnvVariables,
        'query_db': QueryDBAction,
        'load_manifest': LoadManifestAction,
        'create_cabs': CreateCabsAction,
        'buildmsi': InstallerBuildMSIAction,
        'make_pfw': InstallerMakePFWAction
    }

    if opts.manifest:
        state.goals.append('load_manifest')
    else:
        state.goals.append('query_db')

    # Now we can set up the environment using the loaded data
    state.goals.append('setenv')

    # Add remaining build steps
    state.goals.extend(['create_cabs', 'buildmsi', 'make_pfw'])

    state.finalize_goals()

    # --- Run all actions ---
    logging.info(f"Starting build for project: {opts.project_name}")
    if opts.manifest:
        logging.info(f"Using manifest: {opts.manifest}")
    
    try:
        while state.has_more_goals():
            state.next_action()
        logging.info(f"Build complete. Check {opts.output_dir} for installer files.")
    except Exception as e:
        logging.error(f"Build failed: {e}")
        if args.verbose:
            import traceback
            logging.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()
