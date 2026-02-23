"""Base class for all installer actions (Python 3 version)

An action should be as much as possible a single operation to perform a
step in the install creation process.
"""

class InstallerAction(object):
    name = "Base Action"
    goal = "None"
    _registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, 'name') and cls.name != "Base Action":
            InstallerAction._registry[cls.name] = cls

    @classmethod
    def get_action(cls, name):
        action_cls = cls._registry.get(name)
        if action_cls:
            return action_cls()
        return None

    def __init__(self):
        """Simple init. Make sure to call super when overriding."""
        super().__init__()

    def run(self, state):
        """Called to run the actual action (subclasses should not override this).
        Internally simply calls self.do() while adding debug logs of the start/stop of the action.
        """
        print(f"Action {self.name} started.")
        self.do(state)
        print(f"Action {self.name} done.")

    def do(self, state):
        """The actual action's processing. Override in subclasses."""
        pass

    def rollback(self, state):
        """Attempt to rollback the action as much as possible."""
        pass
