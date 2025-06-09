""" The heart of the installer process (Python 3 version).

The 'InstallerState' object is at the heart of the installer process.
The state contains a number of important objects:
    - journal
    - library
    
The state also has a list of goals which are the actions that need to be
carried out to complete the install process.

As each goal is finished, the next is popped off and run; the state watches
the return value of the state to determine if it should continue running,
or if it should error out. Each action that is run is passed the current state,
so the action can record its actions, query options, etc.
"""
import logging
from xml.dom.minidom import getDOMImplementation, parse

logger = logging.getLogger("installer.state")

class InstallerState(object):
    """Heart of the installer creation process (Python 3 version).
    
    The InstallerState is the central collection of everything required to run
    the installer creation process. The 'state' tracks the current goals/previous goals,
    etc. The state is also responsible for containing the journal and the library.
    """
    def __init__(self, opts, args, configs):
        from core.library import InstallerLibrary
        self.library = InstallerLibrary(opts, args, configs)
        self._action = None
        self.goal = None
        self.goals = []
        self.goal_map = {}
        self._goal_ptr = None

    def finalize_goals(self):
        """Marks the goals as prepared (nothing more will be added/removed/changed)."""
        self._goal_ptr = -1

    def next_action(self):
        """Performs the next action in the goal list (if more are available)."""
        if self.has_more_goals():
            self._run_action()
        else:
            logging.info("No Actions Left.")

    def has_more_goals(self):
        """Check to see if there are more goals."""
        if self.goals and self._goal_ptr < (len(self.goals) - 1):
            return True
        return False

    def _run_action(self):
        """Private member-func to run the next goal action."""
        self._goal_ptr += 1
        self._goal = self.goals[self._goal_ptr]
        self._action = self.goal_map[self._goal]()
        # TODO: should probably move the skipgoal check into the InstallerAction class.
        if hasattr(self.library.options, 'skipgoals') and self.library.options.skipgoals and self._goal in self.library.options.skipgoals:
            logging.warning(f"SKIPPING GOAL: {self._goal}")
        else:
            self._action.run(self)

    def save(self, filename):
        """Saves the entire state to an XML file."""
        impl = getDOMImplementation()
        doc = impl.createDocument(None, "installer", None)
        rootnode = doc.documentElement
        # create storage for the 'state' elements to save out.
        statenode = doc.createElement("state")
        rootnode.appendChild(statenode)
        # create storage for the library.
        libnode = doc.createElement("library")
        rootnode.appendChild(libnode)
        self.library.save(libnode, doc)
        with open(filename, "w", encoding="utf-8") as f:
            doc.writexml(f, indent=" ", addindent="  ", newl="\n")

    def load(self, filename, options, arguments, configs):
        """Loads a previously saved state from an XML file."""
        with open(filename, "r", encoding="utf-8") as f:
            dom = parse(f)
        # grab the base installer element        
        installernode = dom.getElementsByTagName('installer')[0]
        # create a new library and load it from the xml
        from core.library import InstallerLibrary
        libraryobj = InstallerLibrary(options, arguments, configs)
        libraryobj.load(installernode.getElementsByTagName('library')[0])
        # once all loading is finished, perform a fixup to repair references objects had.
        from core.archival import Archivable
        Archivable.fix_links()
        self.library = libraryobj
