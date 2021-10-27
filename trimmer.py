#!/usr/bin/env python3

try:
    import sys
    import re
    import traceback

    trimmers = {}
    # Matches a HTTP(S) protocol or nothing
    PROTOCOL = r"(?:(?:https|https)://)?"
    # Matches URL GET parameters
    GETPARAMS = r"(?:\?(?:(?:[^=]+=[^&]+)(?:&[^=]+=[^&]+)*)?)?"

    def trimmer(regex):
        def wrap(func):
            trimmers[regex] = func
            return func
        return wrap

    @trimmer(fr"{PROTOCOL}www\.amazon\.com/"
             fr"(?:[^/]*/)?dp/([^/]+)/?.*{GETPARAMS}")
    def amazon_item(groups):
        return "https://www.amazon.com/dp/{}".format(*groups)

    STACKEXCHANGE_SITES = ['stackoverflow.com', 'serverfault.com',
                           'superuser.com', 'askubuntu.com', 'stackapps.com',
                           'mathoverflow.net', 'pt.stackoverflow.com',
                           'ja.stackoverflow.com', 'ru.stackoverflow.com',
                           'es.stackoverflow.com']

    # https://regex101.com/r/ftibFj/4
    @trimmer(fr"{PROTOCOL}"
             fr"((?:{'|'.join(list(map(re.escape, STACKEXCHANGE_SITES)))})|"
             r"[A-Za-z_-]+\.stackexchange\.com)/q(?:uestions)?/([0-9]+)"
             fr"(?:/[A-Za-z-_0-9]*)?{GETPARAMS}")
    def stackexchange_question(groups):
        # return "https://www.amazon.com/dp/{}".format(*groups)
        return "https://{}/q/{}".format(*groups)

    def trim(url):
        for i in trimmers:
            match = re.fullmatch(i, url)
            if match is not None:
                return trimmers[i](match.groups())
        return url

    url = sys.argv[1]
    sys.stdout.write("success:" + trim(url.strip()))
except Exception:
    sys.stdout.write("fail:" + traceback.format_exc())
sys.stdout.flush()
