import logging
from core.action import InstallerAction

logger = logging.getLogger("installer.core.machine")

class InstallerMachine:
    """
    State machine that drives the installer build process.
    Executes a sequence of actions to build the installer.
    """
    
    def __init__(self):
        self.actions = []
        self._register_actions()
        
    def _register_actions(self):
        # Import actions to register them
        import actions.set_env
        import actions.query_db
        import actions.msi
        import actions.create_cabs
        import actions.make_pfw
        
        # Build the sequence
        self.actions = [
            'setenv',
            'query_db',
            'create_cabs',
            'buildmsi',
            'make_pfw'
        ]
        
    def run(self, state):
        """Run the build process"""
        logger.info("Starting installer build sequence...")
        
        for action_name in self.actions:
            action = InstallerAction.get_action(action_name)
            if not action:
                logger.error(f"Unknown action: {action_name}")
                return False
                
            logger.info(f"Running action: {action_name}")
            try:
                action.do(state)
            except Exception as e:
                logger.error(f"Action {action_name} failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False
                
        logger.info("Build sequence completed.")
        return True
