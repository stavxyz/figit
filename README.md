figit
=======

Upload images to your GitHub Enterprise account!

:camera: for your :octocat:

```bash
$ figit ~/Desktop/ScreenShot48.png -g github.starshipenterprise.com
github.starshipenterprise.com username:sambo
github.starshipenterprise.com:sambo password:
Clipboard success!
https://github.starshipenterprise.com/github-enterprise-assets/0000/1484/0000/0328/5ceb9f38-8791-11e3-88a6-d8fc9578c024.png copied to clipboard
```

#### Installation

```bash
$ pip install figit
```

#### Development

Clone, fork, or whatever you do.

```bash
$ cd figit
$ pip install -e .
```

#### Usage
figit caches your token (not your username/pw) using python keyring.  
figit will ask you again if it finds that your token has expired. 
```bash
$ figit ~/Desktop/ScreenShot48.png -g github.starshipenterprise.com
Clipboard success!
https://github.starshipenterprise.com/github-enterprise-assets/0000/1484/0000/0328/5ceb9f38-8791-11e3-88a6-d8fc9578c024.png copied to clipboard
```

```
