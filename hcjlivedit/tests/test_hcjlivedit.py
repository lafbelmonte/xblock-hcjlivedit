import builtins
import datetime
import unittest
from unittest import mock

import pytest
import pytz
from django.contrib.auth.models import User
from opaque_keys.edx.locations import Location
from opaque_keys.edx.locator import CourseLocator
from workbench.runtime import WorkbenchRuntime
from xblock.field_data import DictFieldData

pytestmark = pytest.mark.django_db


class FakeWorkbenchRuntime(WorkbenchRuntime):
    anonymous_student_id = "MOCK"
    user_is_staff = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        User.objects.create(username=self.anonymous_student_id)

    def get_real_user(self, username):
        return User.objects.get(username=username)


class HtmlCssJsLiveEditorMockedTests(unittest.TestCase):
    def setUp(self):
        super().setUp()
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            try:
                return real_import(name, *args, **kwargs)
            except ImportError:
                for module in ("common", "courseware", "lms", "xmodule"):
                    if name.startswith(f"{module}.") or name == module:
                        return mock.Mock()
                if name == "openedx.core.lib.safe_lxml":
                    return real_import("lxml", *args, **kwargs)
                raise

        builtins.__import__ = fake_import

        def restore_import():
            """restore builtin importer"""
            builtins.__import__ = real_import

        self.addCleanup(restore_import)

        self.course_id = CourseLocator(org="foo", course="baz", run="bar")
        self.runtime = FakeWorkbenchRuntime()
        self.scope_ids = mock.Mock()
        self.staff = mock.Mock(
            return_value={"password": "test",
                          "username": "tester", "is_staff": True}
        )

    def make_xblock(self, display_name=None, **kwargs):
        from hcjlivedit.hcjlivedit import (
            HtmlCssJsLiveEditorXBlock as cls,
        )

        field_data = DictFieldData(kwargs)
        block = cls(self.runtime, field_data, self.scope_ids)
        block.location = Location(
            "foo", "bar", "baz", "category", "name", "revision")

        block.xmodule_runtime = self.runtime
        block.course_id = self.course_id
        block.scope_ids.usage_id = "i4x://foo/bar/category/name"
        block.category = "problem"

        if display_name:
            block.display_name = display_name

        block.start = datetime.datetime(2010, 5, 12, 2, 42, tzinfo=pytz.utc)
        return block

    def test_defaults(self):
        block = self.make_xblock()
        print(block)
        assert block.display_name == "HTML CSS JS Live Editor"
        assert block.css_code == None
        assert block.js_code == None
        assert block.html_code == None
        assert block.default_html_code == ""
        assert block.default_css_code == ""
        assert block.default_js_code == ""
        assert block.weight == 1.0
        assert block.comment == None
        assert block.has_submitted == False
        assert block.instruction == "<p>Hello World!</p>"
