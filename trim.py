#!/usr/bin/env python3
import sys
import re
import traceback
from trimmers import trimmers

try:
    def trim(url):
        for i in trimmers:
            match = re.fullmatch(i, url)
            if match is not None:
                value = trimmers[i](match.groups(), match.groupdict())
                if type(value) is tuple:
                    url, extra = value
                    if extra == "callagain":
                        return trim(value)
                    else:
                        return value
                else:
                    return value
        return None

    url = sys.argv[1]
    trimmed = trim(url.strip())
    if trimmed is None:
        sys.stdout.write("success:" + url)
    else:
        sys.stdout.write("success:" + trimmed)
except Exception:
    sys.stdout.write("fail:" + traceback.format_exc())
sys.stdout.flush()
