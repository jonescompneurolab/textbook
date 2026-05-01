# HNN Textbook Source Code

## How to contribute webpages or Jupyter notebooks

This repository ( https://github.com/jonescompneurolab/textbook ) is how we are
developing our new HNN Textbook website ( published here
https://jonescompneurolab.github.io/textbook/content/preface.html ). We've finished
building the core functionality to power the website, and we are now ready to begin
accepting changes and additions from lab members. This new Textbook website is intended
to be the **primary** resource for users to learn both the underlying scientific basics
of HNN and how to use the HNN software itself (both the Python API and the GUI). All lab
members (and non-lab members) are welcome to contribute! This is where we will be making
changes as we perform a "Pedagogy Update" over 2026.

### Step 1. Create a fork of this repository

Go to https://github.com/jonescompneurolab/textbook , click "Fork" in the upper right,
then click "Create fork". (You only need to do this once.)

### Step 2. Setup Github Pages

Next, before you do anything else, you need to set up your fork of `textbook` to
publish to Github Pages. (You only need to do this once.)

1. Go to the page for your fork of the `textbook` repository.
2. Click the dropdown that says `main` on the left.
3. If you don't see an entry for a branch named `gh-pages`, then you need to create
   one. You can do this easily by typing in `gh-pages` in the textbox, then clicking
   where it says "Create branch gh-pages from main". The branch should now be created.
4. Go to the "Settings" tab of your fork's repository.
5. On the left-hand side, in the "Code and automation" section, click the section named
   "Pages".
6. If you see something at the top like "Your site is live at (URL)", then you're done,
   and you don't need to do step 7.
7. If you don't see that at the top, then under the "Build and deployment" section, do
   the following:

    a. Make sure the "Source" option says "Deploy from a branch" (it probably will by
    default).
    b. Under "Branch", click the dropdown and change it to `gh-pages`.
    c. Hit the "Save" button.
    d. You should done now.

### Step 3. Add or edit webpages (Markdown) and Jupyter Notebooks!

Now you're ready to add or change webpages on the website (using your fork)!

- "Short" version: You can add or edit Markdown (`.md`) and Jupyter Notebook (`.ipynb`)
  files inside the `content` directory. All files are organized according to a
  `content/<section>/<page>` layout, where Markdown files produce pages, and Markdown
  files determine where the Jupyter notebooks are displayed. You can add images and
  display images by putting them in `content/<section>/images` and then referencing them
  appropriately. You do **not** need to install `hnn-core` in order to make your
  changes, *you only need to change the Markdown files (and, optionally, Jupyter
  Notebook and image files)*. We prefer that you contribute changes by "forking" this
  repository to your personal Github account, making your changes on a new branch, and
  then making a "Pull Request" to this repository. If you don't know how to use Github
  and `git`, then you can also send the files containing your changes directly to Austin
  and he’ll make the changes for you. You can run a local "build" of the website to
  inspect what the output looks like (see the [Contributing Guide](CONTRIBUTING.md)),
  but that is optional.

- Long version: We have a more comprehensive [Contributing Guide here](CONTRIBUTING.md).
