import json
import getpass
import logging
import os
import platform
import sys

from mimetypes import guess_type
from subprocess import Popen, PIPE

import argh
import keyring
import requests
import xerox

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

    isfile, filepath = good_filepath(args.path[0])
    if not isfile:
        raise IOError("No such file or directory: %s" % filepath)
    else:
        _, filename = os.path.split(filepath)
        content_type, _ = guess_type(filename)
        filesize = os.path.getsize(filepath)

    base_url = "https://{}".format(args.github)

    cookie = keyring.get_password('figit', 'cookie')
    x_csrf_token = keyring.get_password('figit', 'x_csrf_token')

    if not cookie or not x_csrf_token:
        logger.debug("Cookie or X-CSRF-Token not found in keyring... fetching those.")

        # get session cookie and csrf token
        login_url = base_url + "/login"
        r = requests.get(login_url)
        if not r.ok:
            logger.debug("GET %s | Status Code: %s", login_url, r.status_code)
            logger.debug("GET %s failed | Reason: %s", login_url, r.reason)
        r.raise_for_status()
        soup = BeautifulSoup(r.content)
        x_csrf_token = soup.find(attrs={'name': 'csrf-token'}).get('content')
        cookie = r.headers['set-cookie']
        headers = {"Cookie": cookie}

        # auth and get new cookie (csrf token is probably the same)
        session_url = base_url + "/session"
        github_username = raw_input("%s username:" % args.github)
        github_password = getpass.getpass("%s:%s password:"
                                          % (args.github, github_username))
        data = {'authenticity_token': x_csrf_token,
                'login': github_username,
                'password': github_password,
                'commit': 'Sign in'}
        logger.debug("Authenticating %s on %s ",
                     github_username, args.github)
        r = requests.post(session_url, headers=headers, data=data)
        if not r.ok:
            logger.debug("Authenticating %s on %s | Status Code: %s",
                         github_username, args.github, r.status_code)
            logger.debug("Authentication failed | Reason: %s", r.reason)
            sys.exit("Failed to authenticate user '%s' on %s"
                     % (github_username, args.github))
        r.raise_for_status()
        soup = BeautifulSoup(r.content)
        x_csrf_token = soup.find(attrs={'name': 'csrf-token'}).get('content')
        cookie = r.headers['set-cookie']
        keyring.set_password('figit', 'cookie', cookie)
        keyring.set_password('figit', 'x_csrf_token', x_csrf_token)

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
        keyring.set_password('figit', 'cookie', '')
        keyring.set_password('figit', 'x_csrf_token', '')
    r.raise_for_status()

    try:
        rjson = r.json()
    except ValueError, err:
        typ, value, traceback = sys.exc_info()
        keyring.set_password('figit', 'cookie', '')
        keyring.set_password('figit', 'x_csrf_token', '')
        raise err.__class__, \
              ("The credentials you provided may have been invalid."), \
              traceback

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
        keyring.set_password('figit', 'cookie', '')
        keyring.set_password('figit', 'x_csrf_token', '')
    r.raise_for_status()


    try:
        xerox.copy(image_url)
        print("Clipboard success!")
        print("{} copied to clipboard".format(image_url))
    except Exception as e:
        print("Unable to copy to clipboard.")
        print("Image at {}".format(image_url))

def main():

    argp = argh.ArghParser()
    argp.set_default_command(push)
    argp.dispatch()


if __name__ == '__main__':

    main()

