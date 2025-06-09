from core.action import InstallerAction
import logging
import os

logger = logging.getLogger("installer.actions.clean")

class CleanInstallerAction(InstallerAction):
    name = 'clean_installer'

    def do(self, state):
        # Example: clean up build artifacts or temporary files
        build_dir = getattr(state.library, 'build_dir', None)
        if build_dir and os.path.exists(build_dir):
            for root, dirs, files in os.walk(build_dir, topdown=False):
                for name in files:
                    try:
                        os.remove(os.path.join(root, name))
                    except Exception as e:
                        logging.warning(f"Failed to remove file: {name} ({e})")
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except Exception as e:
                        logging.warning(f"Failed to remove directory: {name} ({e})")
            logging.info(f"Cleaned build directory: {build_dir}")
        else:
            logging.info("No build directory to clean.")
