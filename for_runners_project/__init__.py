import sys

from for_runners.version import __version__

if __name__ == "for_runners_project":
    #
    # This will be called before the click cli
    #
    if not "--version" in sys.argv:
        print("Django-ForRunners v%s" % __version__)

    if len(sys.argv) == 1:
        # FIXME: How can be a "default" action set in click?
        sys.argv.append("run-server")
