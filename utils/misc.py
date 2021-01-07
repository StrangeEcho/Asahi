from datetime import timedelta

#Credit Goes To crazygmr101/aoi
def time_notation(td: timedelta, sep="", full=False):
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    return sep.join([f"{td.days}{'days' if full else 'd '}",
                     f"{hours}{'hours' if full else 'h '}",
                     f"{minutes}{'minutes' if full else 'm '}"])