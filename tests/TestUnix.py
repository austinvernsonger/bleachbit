# vim: ts=4:sw=4:expandtab
# -*- coding: UTF-8 -*-

# BleachBit
# Copyright (C) 2008-2016 Andrew Ziem
# http://www.bleachbit.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Test case for module Unix
"""


import os
import sys
import unittest

sys.path.append('.')
import bleachbit.Common
from bleachbit.Unix import *


class UnixTestCase(unittest.TestCase):

    """Test case for module Unix"""

    def setUp(self):
        """Initialize unit tests"""
        self.locales = Locales()

    def test_apt_autoclean(self):
        """Unit test for method apt_autoclean()"""
        if 0 != os.geteuid() or not FileUtilities.exe_exists('apt-get'):
            self.assertRaises(RuntimeError, apt_autoclean)
        else:
            bytes_freed = apt_autoclean()
            self.assert_(isinstance(bytes_freed, (int, long)))

    def test_is_broken_xdg_desktop(self):
        """Unit test for is_broken_xdg_desktop()"""
        menu_dirs = ['/usr/share/applications',
                     '/usr/share/autostart',
                     '/usr/share/gnome/autostart',
                     '/usr/share/gnome/apps',
                     '/usr/share/mimelnk',
                     '/usr/share/applnk-redhat/',
                     '/usr/local/share/applications/']
        for dirname in menu_dirs:
            for filename in [fn for fn in FileUtilities.children_in_directory(dirname, False)
                             if fn.endswith('.desktop')]:
                self.assert_(type(is_broken_xdg_desktop(filename) is bool))

    def test_is_running(self):
        # Fedora 11 doesn't need realpath but Ubuntu 9.04 uses symlink
        # from /usr/bin/python to python2.6
        exe = os.path.basename(os.path.realpath(sys.executable))
        self.assertTrue(is_running(exe))
        self.assertFalse(is_running('does-not-exist'))

    def test_locale_regex(self):
        """Unit test for locale_to_language()"""
        tests = [('en', 'en'),
                 ('en_US', 'en'),
                 ('en_US@piglatin', 'en'),
                 ('en_US.utf8', 'en'),
                 ('pl.ISO8859-2', 'pl'),
                 ('sr_Latn', 'sr'),
                 ('zh_TW.Big5', 'zh')]
        import re
        regex = re.compile('^' + Locales.localepattern + '$')
        for test in tests:
            m = regex.match(test[0])
            self.assertEqual(m.group("locale"), test[1])
        for test in ['default', 'C', 'English']:
            self.assertTrue(regex.match('test') is None)

    def test_localization_paths(self):
        """Unit test for localization_paths()"""
        from xml.dom.minidom import parseString
        configpath = parseString(
            '<path location="/usr/share/locale/" />').firstChild
        locales.add_xml(configpath)
        counter = 0
        for path in locales.localization_paths(['en']):
            self.assert_(os.path.lexists(path))
            # self.assert_(path.startswith('/usr/share/locale'))
            # /usr/share/locale/en_* should be ignored
            self.assert_(path.find('/en_') == -1)
            counter += 1
        self.assert_(
            counter > 0, 'Zero files deleted by localization cleaner.  This may be an error unless you really deleted all the files.')

    def test_rotated_logs(self):
        """Unit test for rotated_logs()"""
        for path in rotated_logs():
            self.assert_(os.path.exists(path),
                         "Rotated log path '%s' does not exist" % path)

    def test_start_with_computer(self):
        """Unit test for start_with_computer*"""
        b = start_with_computer_check()
        self.assert_(isinstance(b, bool))

        if not os.path.exists(bleachbit.Common.launcher_path) and \
                os.path.exists('bleachbit.desktop'):
            # this happens when BleachBit is not installed
            bleachbit.Common.launcher_path = 'bleachbit.desktop'

        # opposite setting
        start_with_computer(not b)
        two_b = start_with_computer_check()
        self.assert_(isinstance(two_b, bool))
        self.assertEqual(b, not two_b)
        # original setting
        start_with_computer(b)
        three_b = start_with_computer_check()
        self.assert_(isinstance(b, bool))
        self.assertEqual(b, three_b)

    def test_wine_to_linux_path(self):
        """Unit test for wine_to_linux_path()"""
        tests = [("/home/foo/.wine",
                  "C:\\Program Files\\NSIS\\NSIS.exe",
                  "/home/foo/.wine/drive_c/Program Files/NSIS/NSIS.exe")]
        for test in tests:
            self.assertEqual(wine_to_linux_path(test[0], test[1]), test[2])

    def test_yum_clean(self):
        """Unit test for yum_clean()"""
        if 0 != os.geteuid() or os.path.exists('/var/run/yum.pid') \
                or not FileUtilities.exe_exists('yum'):
            self.assertRaises(RuntimeError, yum_clean)
        else:
            bytes_freed = yum_clean()
            self.assert_(isinstance(bytes_freed, (int, long)))
            print 'debug: yum bytes cleaned %d', bytes_freed


def suite():
    return unittest.makeSuite(UnixTestCase)


if __name__ == '__main__' and 'posix' == os.name:
    unittest.main()
