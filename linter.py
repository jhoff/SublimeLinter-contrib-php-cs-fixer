#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Jordan Hoff
# Copyright (c) 2017 Jordan Hoff
#
# License: MIT
#

"""This module exports the PhpCsFixer plugin class."""

import os

from SublimeLinter.lint import Linter, util


def _find_configuration_file(file_name):
    if file_name is None:
        return None

    if not isinstance(file_name, str):
        return None

    if not len(file_name) > 0:
        return None

    candidates = ['.php_cs', '.php_cs.dist']
    checked = []
    check_dir = os.path.dirname(file_name)
    while check_dir not in checked:
        for candidate in candidates:
            configuration_file = os.path.join(check_dir, candidate)
            if os.path.isfile(configuration_file):
                return configuration_file

        checked.append(check_dir)
        check_dir = os.path.dirname(check_dir)

    return None


class PhpCsFixer(Linter):
    """Provides an interface to php-cs-fixer."""

    cmd = None
    config_file = '.php_cs'
    executable = 'php-cs-fixer'
    regex = (
        r'^\s+\d+\)\s+.+\s+\((?P<message>.+)\)[^\@]*'
        r'@@\s+\-\d+,\d+\s+\+(?P<line>\d+),\d+\s+@@'
        r'[^-+]+[-+]?\s+(?P<error>[^\n]*)'
    )
    multiline = True
    defaults = {
        'selector': 'source.php, text.html.basic'
    }
    tempfile_suffix = 'php'
    error_stream = util.STREAM_STDOUT

    def split_match(self, match):
        """Extract and return values from match."""
        match, line, col, error, warning, message, near = super().split_match(match)

        line = line + 3
        message = "php-cs-fixer error(s) - " + message

        return match, line, col, error, warning, message, near

    def cmd(self):
        """Read cmd from inline settings."""
        settings = Linter.get_view_settings(self)

        if 'cmd' in settings:
            command = [settings.get('cmd')]
        else:
            command = [self.executable_path]

        if 'config_file' in settings:
            config_file = settings.get('config_file')
        else:
            config_file = _find_configuration_file(self.view.file_name())
            if not config_file:
                config_file = self.config_file

        command.append('fix')
        command.append('@')
        command.append('--dry-run')
        command.append('--diff')

        # Note: This option requires php-cs-fixer >= 2.7
        command.append('--diff-format=udiff')

        command.append('--using-cache=no')
        command.append('--no-ansi')
        command.append('--config=' + config_file)
        command.append('-vv')

        return command
