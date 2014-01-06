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
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

def good_filepath(filepath):
    filepath = os.path.expanduser(filepath)
    filepath = os.path.abspath(filepath)
    return os.path.isfile(filepath), filepath

@arg('-v', '--verbose', action="store_true", default=False)
@arg('path', nargs=1, help="path to a file you wish to upload")
@arg('-c', '--cookie', default='cookie.txt',
     help='path to cookie file')
@arg('-g', '--github', default='github.com',
     help='GitHub hostname, e.g. github.starshipenterprise.com')
def push(args):

    if args.verbose:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.setLevel(logging.DEBUG)


    cookie=None
    # Arbitrary cookie file name
    with open(args.cookie) as cookie_file:
        cookie = cookie_file.read().strip()

    if(not cookie):
        raise Exception("%s could not be read", args.cookie)


    isfile, filepath = good_filepath(args.path[0])
    if not isfile:
        raise IOError("No such file or directory: %s" % filepath)
    else:
        _, filename = os.path.split(filepath)
        content_type, _ = guess_type(filename)
        filesize = os.path.getsize(filepath)

    base_url = "https://{}".format(args.github)

    # We'll get the X-CSRF-Token using the cookie
    headers = {"Cookie": cookie}
    logger.debug("Fetching X-CSRF-Token | URL: %s", base_url)
    logger.debug("Fetching X-CSRF-Token | Headers: %s", headers)
    r = requests.get(base_url, headers=headers)
    if not r.ok:
        logger.debug("Fetching X-CSRF-Token | Status Code: %s", r.status_code)
        logger.debug("Fetching X-CSRF-Token | Reason: %s", r.reason)
    r.raise_for_status()

    soup = BeautifulSoup(r.content)
    x_csrf_token = soup.find(attrs={"name":"csrf-token"}).get('content')
    logger.debug("X-CSRF-Token: %s", x_csrf_token)

    policy_url = base_url + "/upload/policies/assets"

    headers = {"X-CSRF-Token": x_csrf_token,
               "Cookie": cookie}

    data = {"name": filename,
            "size": filesize,
            "content_type": content_type}

    logger.debug("Requesting asset slot | URL: %s", policy_url)
    logger.debug("Requesting asset slot | Headers: %s", headers)
    logger.debug("Requesting asset slot | Data: %s", data)
    r = requests.post(policy_url, data=data, headers=headers)
    if r.status_code != 201:
        logger.debug("Requesting asset slot | Status Code: %s", r.status_code)
        logger.debug("Requesting asset slot | Reason: %s", r.reason)
    r.raise_for_status()

    rjson = r.json()
    logger.debug("Requeseting asset slot | Response Data: %s", rjson)
    upload_url = base_url + rjson['upload_url']
    image_url = rjson['asset']['href']
    asset = rjson['asset']

    cookie = r.headers.get('set-cookie')
    headers.update({'Cookie': cookie})

    if args.github == 'github.com':
        upload_url = rjson['upload_url']
        headers.update({
            'Access-Control-Request-Method': 'POST',
            'Origin': 'https://github.com',
            })

        r = requests.options(upload_url, headers=headers)
        if r.status_code != 200:
            logger.debug("Requesting asset slot | Status Code: %s", r.status_code)
            logger.debug("Requesting asset slot | Reason: %s", r.reason)

        headers.pop('Cookie')
        headers.pop('Access-Control-Request-Method')

        files = {
            "key": rjson['form']['key'],
            "AWSAccessKeyId": rjson['form']['AWSAccessKeyId'],
            "acl": rjson['form']['acl'],
            "policy": rjson['form']['policy'],
            "signature": rjson['form']['signature'],
            "Content-Type": rjson['form']['Content-Type'],
            "Cache-Control": rjson['form']['Cache-Control'],
            "x-amz-meta-Surrogate-Control": rjson['form']['x-amz-meta-Surrogate-Control'],
            "x-amz-meta-Surrogate-Key": rjson['form']['x-amz-meta-Surrogate-Key'],
            }
    else:
        files = {
            'id': str(asset['id']),
            'name': asset['name'],
            'size': str(asset['size']),
            'content_type': asset['content_type']
            }

    files.update({'file': (filename, open(filepath, 'rb'), content_type)})

    logger.debug("Uploading file | URL: %s", upload_url)
    logger.debug("Uploading file | Headers: %s", headers)
    logger.debug("Uploading file | Files: %s", files)
    r = requests.post(upload_url, headers=headers, files=files)
    if not r.ok:
        logger.debug("Uploading file | Status Code: %s", r.status_code)
        logger.debug("Uploading file | Reason: %s", r.reason)
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

