# coding: utf-8

import os
from unittest import TestCase

import for_runners_test_project
from django_tools.unittest_utils.django_command import DjangoCommandMixin

MANAGE_DIR = os.path.abspath(os.path.dirname(for_runners_test_project.__file__))


class CheckTestEnvironment(DjangoCommandMixin, TestCase):

    def call_manage_py(self, *args, **kwargs):
        return super(CheckTestEnvironment, self).call_manage_py(args, manage_dir=MANAGE_DIR, **kwargs)

    def test_help(self):
        output = self.call_manage_py("--help")
        print(output)
        self.assertNotIn("ERROR", output)
        self.assertIn("[django]", output)
        self.assertIn("Type 'manage.py help <subcommand>' for help on a specific subcommand.", output)

    def test_django_check(self):
        output = self.call_manage_py("check")
        self.assertIn("System check identified no issues (0 silenced).", output)
