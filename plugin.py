import importlib
import os
import importlib.util
from abc import ABC, abstractmethod
import pkgutil
from setuptools import find_packages
from termcolor import colored
from builder.template import add_template_path
from hooks import HOOK_BEFORE_LOAD, HOOK_AFTER_LOAD


class Plugin(ABC):
    """
    This abstract meta class is a blueprint for creating own plugins.
    You can override it's abstract methods, i.e. attach your plugin to hooks / callbacks.
    """
    @abstractmethod
    def install(self):
        pass

    def __init__(self):
        """
        Initialize plugin here
        """
        self.install()

    @abstractmethod
    def before_load(self, raw_content):
        """
        Gets called before the actual loading of the [meta] and [page] raw files through a suitable loader.
        Attach plugin code here, i.e. if you want to implement custom short codes
        """
        pass

    @abstractmethod
    def after_load(self, loaded_content):
        pass


class PluginHandler:
    """
    PluginHandler is responsible for finding and installing user generated plugins in a given directory
    If it's constructor is called, PluginHandler will automatically find the plugins, but not install them right away.
    You can process the found plugins before actually installing them, for instance.
    To eventually install the plugins, call the install_plugins() method
    """
    def __init__(self, plugin_path):
        self.path = plugin_path
        self.found_modules = []
        self.installed_plugins = []

        # Find plugins right away
        self._find_plugins()

    def _find_plugins(self):
        """
        Find all (nested) plugins inside the specified plugin directory
        """
        self.found_modules = []
        if os.path.isdir(self.path):
            for pkg in find_packages(self.path):
                pkg_path = os.path.join(self.path, pkg)
                for _, _, is_pkg in pkgutil.iter_modules([pkg_path]):
                    if not is_pkg:
                        self.found_modules.append({
                            'module': pkg,
                            'path': os.path.join(pkg_path, '{0}.py'.format(pkg))
                        })

    def install_plugins(self):
        """
        Installs and instantiate all found plugins
        """
        for plugin in self.found_modules:
            spec = importlib.util.spec_from_file_location(plugin['module'], plugin['path'])
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            try:
                self.installed_plugins.append(plugin_module.ChePlugin())
                print(colored('Plugin loaded: ', 'green'), plugin['module'])
            except AttributeError:
                print(colored('Plugin loading error: ', 'red'), plugin['module'])

    @staticmethod
    def install_template_path(path):
        """
        Install the specified path to the jinja templates list
        """
        add_template_path(path)

    def _exec_hook(self, hook, *payload):
        initial_payload = payload
        for plugin in self.installed_plugins:
            initial_payload = getattr(plugin, hook)(*initial_payload)
        return initial_payload

    def before_load(self, *payload):
        """
        Execute before_load hook on all installed plugins
        """
        return self._exec_hook(HOOK_BEFORE_LOAD, *payload)

    def after_load(self, *payload):
        """
        Execute after_load hook on all installed plugins
        """
        return self._exec_hook(HOOK_AFTER_LOAD, *payload)
