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

        # Copy files to the CAB directory
        for f in state.library.files:
            src = os.path.join(state.library.root_path, f.path)
            dst = os.path.join(cab_dir, f.path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            logging.info(f"Copied {src} to {dst}")

        cab_name = f"{state.library.project_name}.cab"
        cab_path = os.path.join(output_dir, cab_name)
        print("Files in build_cab_temp:", os.listdir(r"E:\proj\mkInstaller\build_cab_temp"))
        # Create CAB file using makecab
        cmd = f'makecab /D CompressionType=LZX /D CompressionMemory=21 /D CabinetName1={cab_name} /D DiskDirectory1={output_dir} {cab_dir}\\*.*'
        result = os.system(cmd)
        
        if result != 0:
            logging.error(f"Failed to create CAB file with command: {cmd}")
            shutil.rmtree(cab_dir)
            return
            
        shutil.rmtree(cab_dir)
        
        # Store CAB path in state for MSI action to use
        state.library.cab_path = os.path.join(output_dir, cab_name)
        state.library.cab_name = cab_name
        
        logging.info(f"CAB file created at: {state.library.cab_path}")
