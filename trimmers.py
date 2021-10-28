import re

# Matches a HTTP(S) protocol or nothing
PROTOCOL = r"(?:(?:http|https)://)?"
# Matches URL GET parameters
GETPARAMS = r"(?:\?(?:(?:[^=]+=[^&]+)(?:&[^=]+=[^&]+)*)?)?"


trimmers = {}


def trimmer(regex):
    def wrap(func):
        trimmers[regex] = func
        return func
    return wrap


@trimmer(fr"{PROTOCOL}(?:www\.)?amazon\.com/"
         fr"(?:[^/]*/)?dp/([^/]+)/?.*{GETPARAMS}")
def amazon_item(ordered_groups, named_groups):
    return "https://www.amazon.com/dp/{}".format(*ordered_groups)


STACKEXCHANGE_SITES = ['stackoverflow.com', 'serverfault.com', 'superuser.com',
                       'askubuntu.com', 'stackapps.com', 'mathoverflow.net',
                       'pt.stackoverflow.com', 'ja.stackoverflow.com',
                       'ru.stackoverflow.com', 'es.stackoverflow.com']


# https://regex101.com/r/ftibFj/4
@trimmer(fr"{PROTOCOL}"
         fr"((?:{'|'.join(list(map(re.escape, STACKEXCHANGE_SITES)))})|"
         r"[A-Za-z_-]+\.stackexchange\.com)/q(?:uestions)?/([0-9]+)"
         fr"(?:/[A-Za-z-_0-9]*)?{GETPARAMS}")
def stackexchange_question(ordered_groups, named_groups):
    # return "https://www.amazon.com/dp/{}".format(*groups)
    return "https://{}/q/{}".format(*ordered_groups)


# https://regex101.com/r/5aT33H/2
@trimmer(fr"{PROTOCOL}(?:(?:(?:www.|m.)?youtube.com/watch\?v=)|youtu.be/)"
         r"([A-Za-z\d+/]+)(?:(?:\?|&)"
         r"(?:(?:(?:t=([0-9]+))|(?:[^=]+=[^&]+))&?)+)?")
def youtube_video(ordered_groups, named_groups):
    if ordered_groups[1]:
        return "https://youtu.be/{}?t={}".format(*ordered_groups)
    else:
        return "https://youtu.be/{}".format(ordered_groups[0])
