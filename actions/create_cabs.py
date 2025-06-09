from core.action import InstallerAction
import logging

logger = logging.getLogger("installer.actions.create_cabs")

class CreateCabsAction(InstallerAction):
    name = 'create_cabs'

    def do(self, state):
        # CAB creation is handled in the MSI action for this workflow.
        logging.info("CAB creation handled in buildmsi action.")
