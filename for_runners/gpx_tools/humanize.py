import math


def human_seconds(duration):
    minutes = math.floor(duration/60)
    seconds = math.floor(duration - (minutes*60))
    return "%i:%02i" % (minutes, seconds)
