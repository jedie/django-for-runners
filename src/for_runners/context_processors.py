from for_runners import __version__


def for_runners_version_string(request):
    return {"version_string": f"v{__version__}"}
