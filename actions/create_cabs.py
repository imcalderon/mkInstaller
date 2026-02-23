from core.action import InstallerAction
import logging
import os
import shutil
import tempfile

logger = logging.getLogger("installer.actions.create_cabs")

class CreateCabsAction(InstallerAction):
    name = 'create_cabs'

    def do(self, state):
        logging.info("Creating CAB file...")
        
        # Get output directory from options
        output_dir = getattr(state.library.options, 'output_dir', os.path.abspath('out'))
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if we have files from query_db action
        if not hasattr(state.library, 'files') or not state.library.files:
            logging.warning("No files found to include in CAB. Check query_db action.")
            print(f"DEBUG: state.library.files = {getattr(state.library, 'files', None)}")
            return

        # Prepare CAB directory
        cab_dir = os.path.abspath('build_cab_temp')
        os.makedirs(cab_dir, exist_ok=True)

        # Prepare CAB configuration
        cab_name = f"{state.library.project_name}.cab"
        cab_path = os.path.join(output_dir, cab_name)

        # Copy files to the CAB directory
        with open('cabs.ddf', 'w') as ddf:
            ddf.write(".OPTION EXPLICIT\n")
            ddf.write(".Set CabinetName1=" + cab_name + "\n")
            ddf.write(".Set DiskDirectoryTemplate=" + output_dir + "\n")
            ddf.write(".Set Cabinet=on\n")
            ddf.write(".Set Compress=on\n")
            for f in state.library.files:
                src = getattr(f, 'abs_source', os.path.join(state.library.root_path, f.path))
                ddf.write(f'"{src}" "{f.path}"\n')
                logging.info(f"Added {src} to DDF")

        # Create CAB file using makecab
        cmd = f'makecab /F cabs.ddf'
        result = os.system(cmd)
        
        if result != 0:
            logging.error(f"Failed to create CAB file with command: {cmd}")
            return
            
        if os.path.exists('cabs.ddf'): os.remove('cabs.ddf')
        if os.path.exists('setup.inf'): os.remove('setup.inf')
        if os.path.exists('setup.rpt'): os.remove('setup.rpt')
        
        # Store CAB path in state for MSI action to use
        state.library.cab_path = os.path.join(output_dir, cab_name)
        state.library.cab_name = cab_name
        
        logging.info(f"CAB file created at: {state.library.cab_path}")
