# -*- coding: utf-8 -*-
"""
Module containing top layer of backend communication.
"""
from __future__ import unicode_literals, print_function

import os

import financeager.pyro
import financeager.fflask
import financeager.server
from .config import CONFIG, CONFIG_DIR


class Cli(object):

    def __init__(self, cl_kwargs):
        self._cl_kwargs = cl_kwargs

        self._backend = CONFIG["SERVICE"]["name"]
        backend_modules = {
                "flask": "fflask",
                "pyro": "pyro",
                "none": "server"
                }
        self._communication_module = getattr(financeager,
                backend_modules[self._backend])

        self._stacked_layout = self._cl_kwargs.pop("stacked_layout", False)

    def __call__(self):
        command = self._cl_kwargs.pop("command")

        if command == "start":
            self._communication_module.launch_server()
            return

        proxy = self._communication_module.proxy()
        try:
            response = proxy.run(command, **self._cl_kwargs)

            if not isinstance(response, dict):
                return

            error = response.get("error")
            if error is not None:
                print("Command '{}' returned an error: {}".format(command, error))

            elements = response.get("elements")
            if elements is not None:
                from financeager.model import prettify
                print(prettify(elements, self._stacked_layout))

            periods = response.get("periods")
            if periods is not None:
                for p in periods:
                    print(p)

            if self._backend == "none":
                proxy.run("stop")
        except (self._communication_module.CommunicationError) as e:
            print("Error running command '{}': {}".format(command, e))
