# HNN Textbook Source Code

## Where to access the deployed verison of this website?

Click here: <https://jonescompneurolab.github.io/textbook/content/preface.html>

## How to use this repository

1. Content creation step: First, you add or edit the actual content. Specifically, this means adding to or editing the various Markdown (filetype `.md`) files located in `content/`.
   - TODO: We should gradually describe with more detail here.

2. "Building" step: Second, you should "build" the Markdown content into actual HTML pages. This is done automatically when you run `python build.py` or `make` from the main directory. For installation of the python packages/environment, see below.

3. Git push step: At this point, you should be ready to push! Make a PR from your fork so we can then merge your changes.

## Install environment (Mac or Linux)

1. Ensure that Anaconda is installed.
2. Ensure that `make` is installed. You can test if `make` is installed by running the command `which make` which should then return a filename. If it returns nothing, then you need to install it.
   - (MacOS) If you don't have `make`, then you can install it via installing "Xcode Command-Line Tools", which is needed for HNN. To do this, simply run the command `xcode-select --install` and select all the default options. Make sure you restart your computer after installing this
   - (Linux) If you don't have `make` on Linux, then you should install whatever the "basic software building tools" package your distribution uses. As an example, on Ubuntu, this is `build-essential`. So, in the case of Ubuntu, you could install this using the following command: `sudo apt install build-essential`.
3. Once you have the above dependencies, you can easily create a new conda environment using the following command:

```
make create-conda-env-mpi
```

The above will create a new Conda environment named `textbook-env-mpi` which you should use for building the HTML output in this repo.
