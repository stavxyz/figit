import json
import logging
import os
import platform
import sys

from mimetypes import guess_type
from subprocess import Popen, PIPE

import argh
import requests

from argh.decorators import arg

logger = logging.getLogger(__name__)

from .header import XCSRFTOKEN, COOKIE
try:
    from .header_no_commit import XCSRFTOKEN, COOKIE
except ImportError as err:
    logger.exception(err)
    print(err)
    print("Use header.py as a template for header_no_commit.py")

def good_filepath(filepath):
    filepath = os.path.expanduser(filepath)
    filepath = os.path.abspath(filepath)
    return os.path.isfile(filepath), filepath

@arg('path', nargs=1, help="path to a file you wish to upload")
@arg('-s', '--suffix', default='rackspace',
     help='enterprise GitHub suffix, viz. github.<suffix>.com')
def push(args):

    isfile, filepath = good_filepath(args.path[0])
    if not isfile:
        raise IOError("No such file or directory: %s" % filepath)
    else:
        _, filename = os.path.split(filepath)
        content_type, _ = guess_type(filename)
        filesize = os.path.getsize(filepath)

    base_url = "https://github.{}.com".format(args.suffix)
    policies = base_url + "/upload/policies/assets"
    headers = {
    "X-CSRF-Token": XCSRFTOKEN,
    "Cookie": COOKIE
    }
    data = {"name": filename,
            "size": filesize,
            "content_type": content_type}

    r = requests.post(policies, data=data, headers=headers)
    r.raise_for_status()

    rjson = r.json()
    upload_url = base_url + rjson['upload_url']
    image_url = rjson['asset']['href']
    asset = rjson['asset']

    cookie = r.headers.get('set-cookie')

    headers.update({'Cookie': cookie})

    files = {'id': str(asset['id']),
             'name': asset['name'],
             'size': str(asset['size']),
             'content_type': asset['content_type'],
             'file': (filename, open(filepath, 'rb'), content_type)}

    r = requests.post(upload_url, headers=headers, files=files)
    r.raise_for_status()

    if 'Darwin' in platform.platform():
        p1 = Popen(['echo', '-n', image_url], stdout=PIPE)
        Popen(['pbcopy'], stdin=p1.stdout, stdout=PIPE)
        print "\n  ++ url copied to clipboard ++"
    print "\n  go to:\n\n  " + image_url + "\n"


def main():

    argp = argh.ArghParser()
    argp.set_default_command(push)
    argp.dispatch()


if __name__ == '__main__':

    main()

