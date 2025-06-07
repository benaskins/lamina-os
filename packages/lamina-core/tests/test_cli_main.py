#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""Meaningful regression tests for CLI main entry point.

These tests focus on preventing breaking changes to the CLI interface
that users depend on. Tests cover:
- Command structure and argument parsing
- Help text consistency
- Error handling for invalid inputs
- Version reporting
"""

import sys
from io import StringIO
from unittest.mock import patch

import pytest

from lamina.cli.main import create_parser, print_banner


class TestCLIStructure:
    """Test the fundamental CLI structure and arguments."""

    def test_parser_creation_succeeds(self):
        """Verify parser can be created without errors.

        Regression test: Parser creation should never fail.
        """
        parser = create_parser()
        assert parser is not None
        # Parser prog name varies depending on how it's invoked
        assert parser.prog is not None

    def test_global_options_exist(self):
        """Verify global CLI options are consistently available.

        Regression test: These options are part of the public interface.
        """
        parser = create_parser()

        # Test version option
        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])

        # Test verbose and quiet options parse correctly
        args = parser.parse_args(["--verbose", "sanctuary", "list"])
        assert args.verbose is True

        args = parser.parse_args(["--quiet", "sanctuary", "list"])
        assert args.quiet is True

    def test_sanctuary_command_structure(self):
        """Verify sanctuary commands maintain expected structure.

        Regression test: Sanctuary commands are critical for user workflows.
        """
        parser = create_parser()

        # Test sanctuary init with required name
        args = parser.parse_args(["sanctuary", "init", "test-sanctuary"])
        assert args.command == "sanctuary"
        assert args.sanctuary_command == "init"
        assert args.name == "test-sanctuary"
        assert args.template == "basic"  # Default template

        # Test sanctuary init with template option
        args = parser.parse_args(["sanctuary", "init", "test", "--template", "advanced"])
        assert args.template == "advanced"

        # Test sanctuary list command
        args = parser.parse_args(["sanctuary", "list"])
        assert args.sanctuary_command == "list"

        # Test sanctuary status command
        args = parser.parse_args(["sanctuary", "status"])
        assert args.sanctuary_command == "status"

    def test_agent_command_structure(self):
        """Verify agent commands maintain expected structure.

        Regression test: Agent creation is a core feature.
        """
        parser = create_parser()

        # Test agent create with required name
        args = parser.parse_args(["agent", "create", "test-agent"])
        assert args.command == "agent"
        assert args.agent_command == "create"
        assert args.name == "test-agent"
        assert args.template == "conversational"  # Default template

    def test_help_text_accessibility(self):
        """Verify help text is available and informative.

        Regression test: Help text should guide new users effectively.
        """
        parser = create_parser()

        # Capture help output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            with pytest.raises(SystemExit):
                parser.parse_args(["--help"])
        finally:
            sys.stdout = old_stdout

        help_text = captured_output.getvalue()

        # Verify key sections are present
        assert "Lamina Core - Modular AI Agent Framework" in help_text
        assert "sanctuary" in help_text
        assert "agent" in help_text
        assert "Examples:" in help_text

    def test_invalid_command_handling(self):
        """Verify graceful handling of invalid commands.

        Regression test: Error messages should be helpful, not cryptic.
        """
        parser = create_parser()

        # Test invalid main command
        with pytest.raises(SystemExit):
            parser.parse_args(["invalid-command"])

        # Test missing required arguments
        with pytest.raises(SystemExit):
            parser.parse_args(["sanctuary", "init"])  # Missing name


class TestBannerOutput:
    """Test banner display functionality."""

    def test_banner_prints_correctly(self):
        """Verify banner output is consistent.

        Regression test: Banner format should remain stable.
        """
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            print_banner()
        finally:
            sys.stdout = old_stdout

        banner_text = captured_output.getvalue()

        # Verify banner contains expected elements
        assert "Lamina Core" in banner_text
        assert "Modular AI Agent Framework" in banner_text
        assert "║" in banner_text  # Box drawing characters
        assert "╔" in banner_text and "╗" in banner_text  # Top corners
        assert "╚" in banner_text and "╝" in banner_text  # Bottom corners


class TestCLIRegression:
    """Tests specifically for preventing regressions in CLI behavior."""

    def test_command_parsing_consistency(self):
        """Verify command parsing remains consistent across updates.

        Regression test: Command structure should not change unexpectedly.
        """
        parser = create_parser()

        # Test multiple valid command combinations
        test_cases = [
            (["sanctuary", "init", "test"], {"command": "sanctuary", "sanctuary_command": "init"}),
            (["sanctuary", "list"], {"command": "sanctuary", "sanctuary_command": "list"}),
            (["agent", "create", "helper"], {"command": "agent", "agent_command": "create"}),
        ]

        for args_list, expected_attrs in test_cases:
            args = parser.parse_args(args_list)
            for attr, expected_value in expected_attrs.items():
                assert getattr(args, attr) == expected_value

    def test_template_choices_validation(self):
        """Verify template choices are validated correctly.

        Regression test: Invalid templates should be rejected consistently.
        """
        parser = create_parser()

        # Valid template should work
        args = parser.parse_args(["sanctuary", "init", "test", "--template", "basic"])
        assert args.template == "basic"

        # Invalid template should fail
        with pytest.raises(SystemExit):
            parser.parse_args(["sanctuary", "init", "test", "--template", "invalid"])

    @patch("sys.argv", ["lamina", "--version"])
    def test_version_output_format(self):
        """Verify version output maintains expected format.

        Regression test: Version string format should be stable for automation.
        """
        parser = create_parser()

        # argparse version action outputs to stdout, not stderr
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            with pytest.raises(SystemExit) as exc_info:
                parser.parse_args(["--version"])
            assert exc_info.value.code == 0  # Success exit code
        finally:
            sys.stdout = old_stdout

        version_text = captured_output.getvalue()
        assert "lamina-core" in version_text
        # Version should follow semantic versioning pattern
        assert any(char.isdigit() for char in version_text)

    def test_global_flag_positioning(self):
        """Verify global flags work when placed before subcommands.

        Regression test: Global flags should be recognized before subcommands.
        """
        parser = create_parser()

        # Test verbose flag before subcommand (this should work)
        args = parser.parse_args(["--verbose", "sanctuary", "list"])
        assert args.verbose is True
        assert args.command == "sanctuary"
        assert args.sanctuary_command == "list"

        # Test quiet flag
        args = parser.parse_args(["--quiet", "sanctuary", "list"])
        assert args.quiet is True
        assert args.command == "sanctuary"

        # Test that flags have default values when not specified
        args = parser.parse_args(["sanctuary", "list"])
        assert args.verbose is False
        assert args.quiet is False
