import sys

from for_runners import __version__


if __name__ == "for_runners_project":
    #
    # This will be called before the click cli
    #
    if "--version" not in sys.argv:
        print(f"Django-ForRunners v{__version__}")

    if len(sys.argv) == 1:
        # FIXME: How can be a "default" action set in click?
        sys.argv.append("run-server")
