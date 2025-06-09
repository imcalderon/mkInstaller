"""Library object which acts as a repository of all the configs/settings/etc. (Python 3 version)

The library is used to collectively hold all of the 'data' elements that will
be used during the installer creation process. Items such as options, env
variables, and even path locations will be centrally stored here.
"""
import logging
import os
import sys
import configparser
from xml.dom.minidom import getDOMImplementation
from core.archival import load_keyed_object, save_object, Archivable

logger = logging.getLogger("installer.library")

class Configs(object):
    def __init__(self, project, machine_dir):
        self.configs = {}
        try:
            filename = os.path.join(machine_dir, "project", project, f"{project}.cfg")
            parser = configparser.ConfigParser()
            parser.read(filename)
            for section in parser.sections():
                self.add_config(section)
                cfg = self.get_config(section)
                for key, val in parser.items(section):
                    cfg[key] = val
        except Exception as exc:
            raise exc

    def get_config(self, name):
        return self.configs.get(name, {})

    def add_config(self, name):
        if name not in self.configs:
            self.configs[name] = {}

class EnvironmentLibrary(object):
    ''' Wrapper class for working with environ variables (Python 3 version) '''
    def __init__(self, env):
        super().__init__()
        object.__setattr__(self, 'env', {})
        for key, val in env.items():
            self.env[key.upper()] = val

    def get_env(self):
        return self.env.copy()

    def __getattr__(self, name):
        upper_name = name.upper()
        if upper_name in self.env:
            return self.env[upper_name]
        else:
            raise AttributeError(f"env variable '{name}' does not exist")

    def __setattr__(self, name, value):
        self.env[name.upper()] = value

    def __delattr__(self, name):
        upper_name = name.upper()
        if upper_name in self.env:
            del self.env[upper_name]

    def __contains__(self, item):
        return item.upper() in self.env

class InstallerLibrary(object):
    '''Installer library (Python 3 version)'''
    def __init__(self, options, args, configs):
        super().__init__()
        object.__setattr__(self, 'options', options)
        object.__setattr__(self, 'args', args)
        object.__setattr__(self, 'configs', configs)
        object.__setattr__(self, 'env', EnvironmentLibrary(os.environ))
        object.__setattr__(self, 'vars', dict())

    def __setattr__(self, name, value):
        self.vars[str(name)] = value

    def __getattr__(self, name):
        if name in self.vars:
            return self.vars[name]
        else:
            raise AttributeError(f"library variable '{name}' does not exist")

    def __delattr__(self, name):
        if name in self.vars:
            del self.vars[name]

    def __contains__(self, item):
        return item in self.vars

    def save(self, node, doc):
        for key in sorted(self.vars.keys()):
            node.appendChild(save_object(self.vars[key], doc, key))

    def load(self, node):
        for child in node.getElementsByTagName('key'):
            key, obj = load_keyed_object(child)
            if obj is None:
                logger.warning(f"Failed to load object from key [{child.getAttribute('xkey')}]" )
            self.__setattr__(key, obj)

    def dumpenv_to_string(self):
        return ''.join(f"{key} = {val}\n" for key, val in self.env.env.items())
