gimages
=======

Upload images to your GitHub Enterprise account.

```
gimage ~/Desktop/ascreenshot.png

  ++ url copied to clipboard ++

  go to:

  https://github.starshipenterprise.com/github-enterprise-assets/0000/1484/0000/0276/2f4e73b4-750f-11e3-8d96-4f8f79feadd8.png
```

#### Installation

Quick and dirty mode:

```bash
pip install git+https://github.com/smlstvnh/gimages.git#egg=gimages
```

Development:

Clone, fork, or whatever you do.

```bash
cd gimage
pip install -e .
```

#### Configuration

Get the cookie named `_fi_sess` using your the javascript console of your favorite modern browser.

Drop it in `cookie.txt`. It should start with `_fi_sess` have some dashy bits `--` and end in a semi-colon.

#### Usage
```bash
gimage ~/Desktop/ascreenshot.png

  ++ url copied to clipboard ++

  go to:

  https://github.starshipenterprise.com/github-enterprise-assets/0000/1484/0000/0276/2f4e73b4-750f-11e3-8d96-4f8f79feadd8.png

```
