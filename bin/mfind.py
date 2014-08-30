from __future__ import absolute_import
import mfinder


if __name__ == '__main__':
    try:
        mfinder.main()
    except KeyboardInterrupt:
        pass
    except AttributeError:
        print mfinder.__file__
        raise
