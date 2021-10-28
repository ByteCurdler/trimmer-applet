import re

# Matches a HTTP(S) protocol or nothing
PROTOCOL = r"(?:https?://)?"
# Matches URL GET parameters
GETPARAMS = r"(?:[\?&][^=&]+(?:=[^&\n]+)?)*"


trimmers = {}


def trimmer(regex):
    def wrap(func):
        trimmers[regex] = func
        return func
    return wrap


@trimmer(fr"{PROTOCOL}(?:www\.)?amazon\.com/"
         fr"(?:[^/]*/)?dp/([^/]+)/?.*{GETPARAMS}")
def amazon_item(groups):
    return "https://www.amazon.com/dp/{}".format(*groups)


STACKEXCHANGE_SITES = ['stackoverflow.com', 'serverfault.com', 'superuser.com',
                       'askubuntu.com', 'stackapps.com', 'mathoverflow.net',
                       'pt.stackoverflow.com', 'ja.stackoverflow.com',
                       'ru.stackoverflow.com', 'es.stackoverflow.com']


# https://regex101.com/r/ftibFj/4
@trimmer(fr"{PROTOCOL}"
         fr"((?:{'|'.join(list(map(re.escape, STACKEXCHANGE_SITES)))})|"
         r"[A-Za-z_-]+\.stackexchange\.com)/q(?:uestions)?/([0-9]+)"
         fr"(?:/[A-Za-z-_0-9]*)?{GETPARAMS}")
def stackexchange_question(groups):
    # return "https://www.amazon.com/dp/{}".format(*groups)
    return "https://{}/q/{}".format(*groups)


# https://regex101.com/r/5aT33H/2
@trimmer(fr"{PROTOCOL}(?:(?:(?:www.|m.)?youtube.com/watch\?v=)|youtu.be/)"
         r"([A-Za-z\d+/]+)(?:(?:\?|&)"
         r"(?:(?:(?:t=([0-9]+))|(?:[^=]+=[^&]+))&?)+)?")
def youtube_video(groups):
    if groups[1]:
        return "https://youtu.be/{}?t={}".format(*groups)
    else:
        return "https://youtu.be/{}".format(groups[0])


# https://regex101.com/r/p6A331/1
@trimmer(fr"{PROTOCOL}(?:www\.)?google\.com/url\?q=([^&]+){GETPARAMS}")
def google_redirect(groups):
    from urllib.parse import unquote
    return (unquote(groups[0]), "callagain")


@trimmer(fr"{PROTOCOL}bit\.ly/([a-zA-Z0-9]+)")
def bitly_redirect(groups):
    import requests as rq
    bit = rq.get(f"https://bit.ly/{groups[0]}", allow_redirects=False)
    if bit.is_redirect:
        return (bit.headers["Location"], "callagain")
    else:
        return None


# https://regex101.com/r/fOjVrd/2
@trimmer(fr"{PROTOCOL}drive.google.com/file/d/([A-Za-z0-9]+)"
         fr"(?:/[a-z]*)?{GETPARAMS}")
def google_drive_file(groups):
    return "https://drive.google.com/file/d/{}".format(*groups)
