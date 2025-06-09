from core.action import InstallerAction

class MyInstallerAction(InstallerAction):
    def __init__(self, *args, **kwargs):
        super(MyInstallerAction, self).__init__(*args, **kwargs)

    def run(self):
        # Your custom installation logic here
        print("Running my custom installer action!")