Description
===========
Bitbucket [announced](https://bitbucket.org/blog/sunsetting-mercurial-support-in-bitbucket) that they will delete all the Mercurial repositories from our accounts before **June 1st 2020**. For those who are still using Mercurial repositories, it is the right time to migrate them into Git. 

This little python script may help, it will clone all of your Bitbucket Mercurial repositories and convert them to Git and push the new Git repositories back to Bitbucket.

WARNING
-------

Be sure to leave sufficient space on your disk, as this script will clone and duplicate all of your Mercurial repositories. Also, if you've enabled 2 factor authentication in your Bitbucket account, you may want to create an [App Password](https://developer.atlassian.com/bitbucket/api/2/reference/meta/authentication#app-pw) to authenticate with this script (Repositories Read/Write/Admin are required).

This app is not destructive, it does not delete any Mercurial repositories, it renames them:

1. Downloads the Mercurial repository;
2. Creates a local Git repository;
3. Converts the Mercurial repository into the newly created local Git repository;
4. Renames the old Mercurial repository to `(Mercurial) {repo name}`;
5. Creates a new remote Git repository with the original name;
6. Pushes the local Git repository to remote.

Usage
=====
`python convert.py`

Requirements
============
* This was only tested on macOS. At the very least you will need a Unix-like system to execute the `popen` calls.
* Python 2.x and dependencies (`pip install mercurial pybitbucket`).
* `git` and `hg` command line tools.

The dependency packaged with this script:

* fast-export https://github.com/frej/fast-export

What am I left with?
====================
* Once the script has been run you should have your old Mercurial repository renamed as `(Mercurial) {repo name}`.
* A new Git repository with the name of the original repository.
* Not everything will be converted to your new Git repository. You will lose Issues, Downloads, Wiki etc.

In case of failure
==================
1. Delete the newly created Git repository (if it was created).
2. Rename the Mercurial repository back to the original name by removing the `(Mercurial)` prefix.