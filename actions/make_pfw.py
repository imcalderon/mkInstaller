from core.action import InstallerAction
import logging
import os

logger = logging.getLogger("installer.actions.make_pfw")

class InstallerMakePFWAction(InstallerAction):
    name = 'make_pfw'

    def do(self, state):
        # Get output directory from options
        output_dir = getattr(state.library.options, 'output_dir', os.path.abspath('out'))
        os.makedirs(output_dir, exist_ok=True)
        
        # Example: create a self-extracting archive using generic pfw logic
        # This would use a compression utility or custom logic
        logging.info("Creating self-extracting archive (pfw)...")
        
        # Get MSI path if it exists
        msi_path = getattr(state.library, 'msi_path', None)
        
        if msi_path and os.path.exists(msi_path):
            # Create a self-extracting archive (this is a placeholder)
            pfw_name = f"{state.library.project_name}_setup.exe"
            pfw_path = os.path.join(output_dir, pfw_name)
            
            # Here you would actually create the self-extracting archive
            # For now, we'll just simulate it by copying the MSI
            import shutil
            try:
                shutil.copy2(msi_path, pfw_path)
                state.library.pfw_path = pfw_path
                logging.info(f"Self-extracting archive created at: {state.library.pfw_path}")
            except Exception as e:
                logging.error(f"Failed to create self-extracting archive: {e}")
        else:
            logging.warning("No MSI file found to package into self-extracting archive")
            state.library.pfw_path = None
