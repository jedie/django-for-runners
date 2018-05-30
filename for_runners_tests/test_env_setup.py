# coding: utf-8



import os
from unittest import TestCase

import pytest

from django.core.management import call_command

from django_tools.unittest_utils.django_command import DjangoCommandMixin

import for_runners_test_project

MANAGE_DIR = os.path.abspath(os.path.dirname(for_runners_test_project.__file__))


class CheckTestEnvironment(DjangoCommandMixin, TestCase):

    def call_manage_py(self, *args, **kwargs):
        return super(CheckTestEnvironment, self).call_manage_py(
            args, manage_dir=MANAGE_DIR, **kwargs
        )

    def test_help(self):
        output = self.call_manage_py("--help")
        print(output)
        self.assertNotIn("ERROR", output)
        self.assertIn("[django]", output)
        self.assertIn("[cms]", output)
        self.assertIn("Type 'manage.py help <subcommand>' for help on a specific subcommand.", output)

    def test_django_check(self):
        output = self.call_manage_py("check")
        self.assertIn("System check identified no issues (0 silenced).", output)

    @pytest.mark.django_db
    def test_cms_check(self):
        """
        We can't call "cms check" via ./manage.py because the database
        doesn't exist, so it will raise errors.
        """
        call_command("cms", "check")

        # output = self.call_manage_py("cms", "check")
        # print(output)
        # self.assertNotIn("error", output)
        # self.assertIn("Installation okay", output)

