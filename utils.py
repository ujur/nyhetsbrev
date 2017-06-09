# encoding: UTF-8

from __future__ import print_function


def pip_install(*packages):
    """
    Install the packages using pip
    """
    try:
        import pip
        for package in packages:
            pip.main(["install", "--upgrade", package, "--user"])
    except Exception as e:
        print("Unable to install %s using pip." % package)
        print("Exception:", e)
        exit(-1)


def print_text_file(filename):
    "Send a text file to the default Windows printer"
    import subprocess
    try:
        subprocess.run(["notepad", "/p", filename])
    except Exception as e:
        print("Unable to start Notepad:", e)
