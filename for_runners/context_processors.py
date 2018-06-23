
from for_runners.version import __version__

def for_runners_version_string(request):
    return {
        "version_string": "v%s" % __version__
    }
