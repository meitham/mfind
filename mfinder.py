from __future__ import print_function

import argparse
import fnmatch
import functools
import logging
import os
import pprint
import subprocess

from pkg_resources import iter_entry_points


logging.basicConfig()
logger = logging.getLogger('mfind')


class Primary(object):
    """This will be extended by all primaries
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def path_match(context, case_match=True):
    """Compares a file path against a pattern
    similar to `find -path arg1`
    """
    dirname = context['dirname']
    pattern = context['args']
    if case_match and fnmatch.fnmatchcase(dirname, pattern):
        return context
    if not case_match and fnmatch.fnmatch(dirname.lower(), pattern.lower()):
        return context


def name_match(context, case_match=True):
    """Compares a file name against a pattern
    similar to `find -name arg1`
    """
    filename = context['filename']
    pattern = context['args']
    if case_match and fnmatch.fnmatchcase(filename, pattern):
        return context
    if not case_match and fnmatch.fnmatch(filename.lower(), pattern.lower()):
        return context


def print_path(context, null=False):
    """Prints out the filename
    similar to `find . -print`
    """
    path = context['path']
    suffix = context['args']
    context['buffer'].append(path)
    if suffix:
        context['buffer'].append(suffix)
    if null:
        context['buffer'].append('\0')
    return context


def print_linefeed(context):
    """Prints out a new line
    Useful to separate outputs into several lines
    """
    context['buffer'].append('\n')
    return context


def print_context(context):
    """Prints out the conext
    Useful for debugging
    """
    context['buffer'].append(pprint.pformat(context))
    return context


def exec_command(context):
    """Calls an external command, inspired by find -exec
    {} will be converted to file path anywhere it appears in the args.
    TODO: added context params inside {}
    """
    path = context['path']
    command = context['args']
    command = [path if t == '{}' else t for t in command]
    subprocess.call(command[:-1])
    return context


tests_map = {
    'name': name_match,
    'iname': functools.partial(name_match, case_match=True),
    'path': path_match,
    'ipath': functools.partial(path_match, case_match=True),
    'true': lambda context: context,
    'false': lambda _: False,
}

actions_map = {
    'print': print_path,
    'println': print_linefeed,
    'print0': functools.partial(print_path, null=True),
    'print_context': print_context,
    'exec': exec_command,
}


def evaluate(dirname, filename, tests, actions, verbosity):
    """Evaluates a user test and return True or False, like GNU find tests
    """
    context = {
        'dirname': dirname,
        'filename': filename,
        'path': os.path.relpath(os.path.join(dirname, filename)),
        'verbosity': verbosity,
        'buffer': [],
    }
    for test, args in tests:
        context.update({'args': args})
        test = tests_map[test]
        context = test(context)
        if not context:
            return False
    for action, args in actions:
        context.update({'args': args})
        action = actions_map[action]
        context = action(context)
        if not context:
            return False
    line = ''.join(context['buffer'])
    if line.strip():
        print(line)
    return True


class TreeWalker(object):
    """provides a functionality similar to os.walk but can do
    pre defined depth when needed.
    """
    def __init__(self, *args, **kwargs):
        self.top = kwargs.get('top', os.getcwd())
        if not os.path.exists(self.top):
            raise IOError('{}: No such file or directory'.format(self.top))
        self.max_depth = kwargs.get('max_depth')
        if isinstance(self.max_depth, list):
            self.max_depth = self.max_depth[0]
        self.depth_first = kwargs.get('depth_first', False)
        self._depth = 0
        self.recursive = self.max_depth is None or self.max_depth > 0
        self.follow_links = kwargs.get('follow_links', False)

    def __repr__(self):
        return 'TreeWalker(top=%(top)s, max_depth=%(max_depth)r)' % self.__dict__

    def walk(self, top=None, depth=0):
        if not top:
            top = self.top
        if self.max_depth is not None:
            if depth > self.max_depth:
                return
        if os.path.isdir(top):
            for f in sorted(os.listdir(top), key=os.path.isdir,
                            reverse=self.depth_first):
                file_path = os.path.join(top, f)
                if os.path.isdir(file_path) and self.recursive:
                    islink = os.path.islink(file_path)
                    if islink and not self.follow_links:
                        continue
                    for d, f in self.walk(file_path, depth + 1):
                        yield d, f
                elif os.path.isfile(file_path):
                    yield top, f
        else:
            yield os.path.split(top)


class ArgTest(argparse.Action):
    """An Action that collects arguments in the order they appear at the shell
    """

    def __call__(self, parser, namespace, values, option_string=None):
        if 'tests' not in namespace:
            setattr(namespace, 'tests', [])
        namespace.tests.append((self.dest, values))


class ArgAction(argparse.Action):
    """An Action that collects arguments in the order they appear at the shell
    """

    def __call__(self, parser, namespace, values, option_string=None):
        if 'actions' not in namespace:
            setattr(namespace, 'actions', [])
        namespace.actions.append((self.dest, values))


def cli_args():
    """
    """
    parser = argparse.ArgumentParser(
        description="extensible pure python gnu file like tool."
    )
    parser.add_argument('-follow',
                        dest='follow_links',
                        action='store_true',
                        help="Follow symbolic links, the default is not to follow.",
                        default=False)
    parser.add_argument('-depth',
                        '-d',
                        dest='depth_first',
                        action='store_true',
                        default=False,
                        help=("Process the subdirectory before processing the "
                              "sibling files available under that directory.")
                        )
    parser.add_argument('-maxdepth',
                        dest='max_depth',
                        action='store',
                        default=None,
                        type=int,
                        nargs=1,
                        help=("Limit the recursion to a maximum depth."
                              " The default is unlimited depth. ")
                        )
    parser.add_argument('path', action='store', nargs='?', default=os.getcwd(),
                        help="""The root of the processing tree, this defaults to the
                        current working directory `pwd`.""")
    parser.add_argument('-v', action='count', dest='verbose', default=0, help="""
                        The level of verbosirty. The more v you add the more stuff you will
                        see.
                        """)
    parser.add_argument('-name', dest='name', action=ArgTest,
                        help="""Match by filename, accepts UNIX globbing patterns.
                        e.g. `-name *.rst`
                        """)
    parser.add_argument('-iname', dest='iname', action=ArgTest,
                        help="""Match by filename, similar to `-name` but this is case
                        insensitive match.
                        """)
    parser.add_argument('-path', dest='path', action=ArgTest,
                        help="""Match by path, accepts UNIX globbing patterns.
                        e.g. `-path *.rst`
                        """)
    parser.add_argument('-ipath', dest='ipath', action=ArgTest,
                        help="""Match by filename, similar to `-ipath` but this is case
                        insensitive match.
                        """)
    parser.add_argument('-true', dest='true', action=ArgTest, nargs=0,
                        help="""Always evaluates to True""")
    parser.add_argument('-false', dest='false', action=ArgTest, nargs=0,
                        help="""Always evaluates to False""")
    parser.add_argument('-print', dest='print', action=ArgAction, nargs='?',
                        help="""Prints the file path. It accepts an optional argument as
                        a string which is used as a seperator, e.g. `-print ','` would
                        print the file path followed by a comma, thus any further print
                        from thie file context would be printed on the same line after the
                        comma. Each file is printed in a new line so this should not be
                        confused as a separator between matching files.""")
    parser.add_argument('-print0', dest='print0', action=ArgAction, nargs=0,
                        help="""Print the file path follows by a null character rather than
                        space. Helpful to be used with `xargs -0`.""")
    parser.add_argument('-println', dest='println', action=ArgAction,
                        nargs=0, help="""Print the file path followed by a new line.
                        """)
    parser.add_argument('-print-context', dest='print_context',
                        action=ArgAction, nargs=0, help=""""
                        Prints the context for the match, the context is implemented as a
                        mapping object where primaries can add/remove/modify any of the
                        key/value pairs.""")
    parser.add_argument('-exec', dest='exec', action=ArgAction, nargs='+',
                        help="""Execute a shell command when a match happens, any `{}` will
                        be replaced by the match path.""")
    # add plugins
    for plugin in iter_entry_points(group='mfind.plugin', name='cli_args'):
        parser = plugin.load()(parser)
    return parser


def main():
    parser = cli_args()
    ns = parser.parse_args()
    verbose = logging.DEBUG if ns.verbose >= 2 else logging.INFO
    logger.setLevel(verbose)
    tw = TreeWalker(top=ns.path, **ns.__dict__)
    tests = getattr(ns, 'tests', [])
    actions = getattr(ns, 'actions', [])
    if not actions:
        logger.debug('defaulting action to print')
        actions = [('print', None)]
    # add plugins
    for plugin in iter_entry_points(group='mfind.plugin', name='tests'):
        tests_map.update(plugin.load())
    for plugin in iter_entry_points(group='mfind.plugin', name='actions'):
        actions_map.update(plugin.load())
    for dirname, filename in tw.walk():
        evaluate(dirname, filename, tests, actions, ns.verbose)
