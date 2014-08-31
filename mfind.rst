====
find
====

``find`` is an analogue to the famous BSD find command line.

..code-block:: python

>>> find('.') or find(os.getcwd())
An iterable of all the files under the current directory.

>>> find('/some/path')
An iterable of all the files under that directory.

>>> find('.', depth=0) or find('.', recursive=False)
An iterable of all the files under that directory, not recursively

>>> find('.', depth=range(3, 6))
An iterable of all the files under '.' starting from level 3 to level 6.

>>> find('.', depth=lambda d: d > 9)
An iterable of all the files under '.' where only depth is greater than 9.

>>> find('.', depth={'min': 2})
An iterable of all the files under '.' starting from min depth 2

>>> find('.', depth={'min': 2, 'max': 7})
An iterable of all the files under '.' starting from min depth 2 and max depth 7

>>> find('/some/path', traverse=find.depth_first)
Where travesal algorithms are:
        * depth_first
        * breadth_first
        * rdepth_first
        * rbreadth_first

>>> find('.').filter(lambda f: os.path.isfile(f))
filter takes any callable and call it for each file found. If your callable
accepts two arguments, then second would be the index of file.

The above is equivalent to
itertools.ifilter(find('.')) as our filter is actually an ifilter

>>> find('/some/path').filter(lambda f: os.path.basename(f).startswith('.git'))
find all the file called .git under /some/path

>>> find('.').action|apply|perform|do|exec|call not sure of a name yet

>>> find('.').apply(lambda f: os.path.unlink(f))
This removes all files under .

>>> find('.').delete(lambda f: os.size(f) > 100MB)
             .remove()
             .unlink()

>>> find('.').move(lambda f: f.lower())
renames all files under '.' to lowercase.

>>> find('.').all(filter() & filter() | filter())

>>> find('.').empty().delete()
