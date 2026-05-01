## Table of Contents

Firstly, please see and follow our [Code of Conduct here](./CODE_OF_CONDUCT.md).

1. [Contributing Content to the HNN Textbook](#1-contributing-content-to-the-hnn-textbook)
    - [How the Textbook Is Organized](#how-the-textbook-is-organized)
    - [Markdown Files](#markdown-files)
    - [Jupyter Notebooks](#jupyter-notebooks)
    - [Local Images](#local-images)
    - [Quick Reference Checklist](#quick-reference-checklist)
2. [Building the website locally](#2-building-the-website-locally)
3. [(Advanced) Maintainer workflow description (v3.1)](#3-advanced-maintainer-workflow-description-v31)
    - [Definitions](#definitions)
    - [Author standard-operating-procedures](#author-standard-operating-procedures)
    - [Deployment flow](#deployment-flow)
    - [Maintainer Tasks for `hnn-core` upgrades](#maintainer-tasks-for-hnn-core-upgrades)

---

# 1. Contributing Content to the HNN Textbook

This guide explains how to add or edit content in the HNN Textbook. It covers
three things: Markdown files, Jupyter notebooks, and local images.

### Create a fork of this repository

First, Go to https://github.com/jonescompneurolab/textbook , click "Fork" in the upper
right, then click "Create fork". (You only need to do this once.)

## Setting up your Fork's "Github Pages" website

Next, before you do anything else, you need to set up your fork of `textbook` to
publish to Github Pages. You only need to do this once, and it's easy.

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

The rest of Section 1 here is guidance for how to edit and organize the specific pages
you want to change or add.

## How the Textbook Is Organized

All content lives inside the `content/` directory. It is organized into numbered
**sections** (directories) and numbered **pages** (files):

```
content/
├── 00_preface.md                   ← a top-level page (no section)
├── 01_getting_started/             ← a section
│   ├── README.md                   ← section title lives here
│   ├── 01_challenge.md             ← first page in this section
│   ├── 02_template_model.md        ← second page
│   └── 03_installation.md          ← third page
├── 05_erps/
│   ├── README.md
│   ├── 01_erps_in_gui.md
│   ├── 02_hnn_core.md
│   ├── images/                     ← images used by pages in this section
│   │   ├── erp_fig_01.png
│   │   └── ...
│   └── plot_simulate_evoked.ipynb  ← a Jupyter notebook
└── ...
```

**Key rules:**

- The **numeric prefix** on directories and files (e.g. `01_`, `02_`) controls
the order pages appear in the sidebar navigation. Lower numbers come first.
- The prefix is stripped when the site is built, so `02_template_model.md`
becomes `template_model.html`.
- Each section directory **must** have a `README.md` that defines the section's
title (see below).

---

## Markdown Files

Markdown (`.md`) files are the main content format. Each file becomes one page
on the website.

### Creating a New Markdown Page

1. Pick the section directory where your page belongs (e.g.
`content/01_getting_started/`).
2. Choose a numeric prefix that places it in the right order. For example, to
add a page between `02_template_model.md` and `03_installation.md`, you would
name your file `03_new_page.md` and rename the old `03_installation.md` to
`04_installation.md`.
3. Create the file with the required metadata header and your content (see
template below).

### Markdown Page Template

Every Markdown page **must** start with a metadata block inside an HTML comment.
Here is the minimum required template:

```markdown
<!--
# Title: 1.4 My New Page Title
# Updated: 2025-06-15
#
# Contributors:
    # Your Name <your.email@example.com>
-->

## 1.4 My New Page Title

Your content goes here.
```

**What each metadata field means:**

| Field | Purpose |
| --- | --- |
| `# Title:` | The title shown in the sidebar navigation. **Required.** |
| `# Updated:` | The date you last edited this page (YYYY-MM-DD). |
| `# Contributors:` | A list of people who wrote or edited this page. |

### Creating a New Section

To create an entirely new section (a new "chapter" in the sidebar):

1. Create a new directory under `content/` with a numeric prefix, e.g.
`content/10_my_new_section/`.
2. Inside it, create a `README.md` with **only** the metadata block:

```markdown
<!--
# Title: 10. My New Section
# Updated: 2025-06-15
#
# Contributors:
    # Your Name
-->
```

1. Add your page `.md` files inside this new directory.

### Writing Content

The textbook uses standard Markdown processed by Pandoc. If you are new to using
Markdown, [you can view Github's intro to Markdown here to get
started](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).
Here are the most common things you will use:

**Headings:**

```markdown
## Section Heading
### Sub-heading
```

**Bold and italic:**

```markdown
**bold text** and *italic text*
```

**Links to other textbook pages:**

```markdown
<!-- Link to a page in the same section -->
[Template Model](template_model.html)

<!-- Link to a page in a different section -->
[Installation](../01_getting_started/installation.html)
```

Note: When linking to other pages inside your Markdown document, use the `.html`
extension (not `.md`) and drop the numeric prefix from the filename.
`02_template_model.md` is linked as `template_model.html`.

Pro-tip: You can insert HTML *itself* inside Markdown documents and it will be rendered
correctly in the final output.

**Citations (BibTeX):**

The textbook has a bibliography file (`textbook-bibliography.bib`) in the
project root. To cite a reference:

```markdown
This was first shown in a prior study [@jones_neural_2007].
```

The `[@key]` syntax will be automatically replaced with a formatted citation
during the build. Feel free to add new references to that bibliography file.

**Embedding a Jupyter notebook's output:**

To embed the rendered output of a notebook into a Markdown page, use this
special syntax on its own line:

```markdown
[[my_notebook.ipynb]]
```

The notebook file must be in the same section directory as the Markdown file. See
the Jupyter Notebooks section below for more details.

---

## Jupyter Notebooks

Jupyter notebooks (`.ipynb` files) contain executable Python code. They are
**not** displayed on the website by themselves; instead, their rendered output is
embedded inside a Markdown page using the `[[notebook.ipynb]]` syntax.

### Adding a New Notebook

1. Create your `.ipynb` file in the appropriate section directory (the same
directory as the Markdown page that will embed it).
2. Write your notebook with a mix of Markdown cells (for explanations) and code
cells (for executable code).
3. Create a companion Markdown page (or edit an existing one) that embeds the
notebook. A minimal companion page looks like this:

```markdown
<!--
# Title: 4.2 API Tutorial of ERPs Simulation
# Updated: 2025-01-29
#
# Contributors:
    # Your Name
-->

[[plot_simulate_evoked.ipynb]]
```

The `[[name.ipynb]]` line is all that is needed — the build system will execute the
notebook and insert its full rendered output into the page.

### Notebook Tips

- Notebook filenames do **not** need a numeric prefix.
- Give notebooks descriptive names, e.g. `plot_simulate_evoked.ipynb` or
`batch_simulation_notebook.ipynb`.
- The build system tracks whether notebooks have changed and only re-executes
them when needed.
- If your notebook should be skipped during certain builds (e.g. it requires special
dependencies or depends on code that is still in development), then let the Maintainers
know. when you make your Pull Request.

---

## Local Images

Images are stored in an `images/` subdirectory within the section that uses
them.

### Adding a New Image

1. If the section doesn't already have an `images/` directory, create one:

```
content/05_erps/images/
```

1. Place your image file (PNG, GIF, JPG, etc.) inside it. Use a descriptive
name with a consistent prefix matching the section:

```
erp_fig_01.png
erp_fig_02.gif
gamma_fig_01.png
```

### Referencing Images in Markdown

Use standard Markdown image syntax with a relative path:

```markdown
![Figure 1 description](images/erp_fig_01.png)
```

To center an image and control its layout, wrap it in a `<div>`:

```markdown
<div style="display:block; width:100%; margin: 0 auto;">

![Figure 1](images/erp_fig_01.png)

</div>
```

To add a caption below the image:

```markdown
<div style="display:block; width:100%; margin: 0 auto;">

![Figure 1](images/erp_fig_01.png)

</div>

<p style="text-align:justify; display: block; margin: 0 auto; width: 90%; font-size: 1em;">
Figure 1: Description of what the figure shows.
</p>
```

### Image Tips

- Always use **relative paths** from the Markdown file to the image (e.g.
`images/my_figure.png`), not absolute paths.
- Prefer PNG for static images and GIF for animations.
- Keep image file sizes reasonable for web loading.

---

## Quick Reference Checklist

When adding a new page, make sure you have:

- [ ]  A metadata comment block at the top of your `.md` file with `# Title:`,
`# Updated:`, and `# Contributors:`
- [ ]  A numeric prefix on the filename that places it in the correct order
- [ ]  If you created a new section directory, a `README.md` with the section
title metadata
- [ ]  Images placed in the section's `images/` subdirectory and referenced with
relative paths
- [ ]  Notebooks placed in the same section directory as their companion
Markdown page, embedded with `[[notebook.ipynb]]`
- [ ]  Internal links using `.html` extensions and filenames without numeric
prefixes

---

# 2. Building the website locally

This is optional.

If you want to build the final HTML files yourself so that you can inspect the output bor investigate errors, we've made this easy to do. Note that Windows is not supported. You can do this via the following:

1. First, you need to install [Anaconda](https://www.anaconda.com/download) if you haven't already. Restart any Terminal windows that you may have open after this.
2. Next, ensure that `make` is installed. You can test if `make` is installed by running the command `which make` which should then return a filename. If it returns nothing, then you need to install it.
    - (MacOS) If you don't have `make`, then you can install it via installing "Xcode Command-Line Tools", which is needed for HNN. To do this, simply run the command `xcode-select --install` and select all the default options. Make sure you restart your computer after installing this!
    - (Linux) If you don't have `make` on Linux, then you should install whatever the "basic software building tools" package your distribution uses. As an example, on Ubuntu, this is `build-essential`. So, in the case of Ubuntu, you could install this using the following command: `sudo apt install build-essential`.
3. We provide two different Anaconda environments, and you can install one, the other, or **both**:
    - You can install an environment that uses the latest "stable" (i.e. officially released) version of HNN-Core by running `make create-textbook-stable-env`. This will create a new Anaconda environment named `textbook-stable-env`.
    - You can install an environment that uses the latest "master" branch (i.e. development) version of HNN-Core by running `make create-textbook-dev-env`. This will create a new Anaconda environment named `textbook-dev-env`.
4. Once you have created and activated whichever Anaconda environment you want to use, then the way you are expected to run a build of the website is by using the command `python build.py`, along with any optional arguments you may want.
    - (Strongly recommended) To view what the optional arguments do, run `python build.py -h` to display the built-in help. Note that there are many arguments with many different values that you can pass, and the documentation is extensive.
    - A default run of `python build.py` (by itself) will **NOT re-execute any Jupyter notebooks**, and is equivalent to doing a run with the following arguments:
    ```
    python build.py \
        --build-directory=auto \
        --code-version=stable \
        --execution-type=no-execution
    ```

---

# 3. (Advanced) Maintainer workflow description (v3.1)

This is only for active developers or maintainers managing the repository as a whole, and useless to anyone else. This was built from the discussion of proposal v3.0 here https://www.notion.so/jonescompneurolab/Austin-Proposal-v3-0-2a244dbbcce680d3892aed671bf55132 .

## Definitions:

- Filetypes:
    - `MD`: Markdown files (`.md`)
    - `NB`: Jupyter notebook files (`.ipynb`)
- People:
    - `Author`: Someone "authoring" any MD or NB files, including either creation of new ones or updating existing ones. This is expected to be both the Maintainers and also other members of the Lab, including summer students and GSoC students, on occasion.
    - `Maintainer`: Someone who understands the website-building and notebook-execution code, maintains that code, and also actively maintains the content that the website is intended to publish. Maintenance includes adding files to and from the different "notebook skip" categories based on upstream changes to `hnn-core`  itself. They will also probably be "authoring" content too. Probably only Dylan or Austin (and maybe someone from CCV).
- Stable build terms:
    - `stable`: The current stable "release" of the `hnn-core` package, as used by `pip` from https://pypi.org/project/hnn-core/ .
    - `textbook-stable-env`: A Conda environment used by the Textbook repo that includes a full installation of `hnn-core`'s `stable` version as defined above. (This formerly went through several different name changes).
    - `content-build`: A "build" of the website using MD and NB files under the `content` directory to make output files (HTML pages and "notebook-output-JSON-files") that ***go in the `content` directory.*** Builds using  `textbook-stable-env` output their website build to this directory by default (unless overridden by the user's arguments to `build.py` ).
- Dev build terms:
    - `master`: The `master` (aka development) branch of the `hnn-core` source code at https://github.com/jonescompneurolab/hnn-core as of its latest commit.
    - `custom`: A custom commit of hnn-core for use in a `dev-build`, usually from someone's fork.
    - `textbook-dev-env`: A Conda environment used by the Textbook repo that includes a full installation of either `hnn-core`'s `master` branch or a `custom` branch. (This formerly went through several different name changes).
    - `dev-build`: A "build" of the website using MD and NB files under the `content` directory to make output files (HTML pages and "notebook-output-JSON-files") that ***go in the `dev` directory.*** Builds using  `textbook-dev-env`  (including `--code-version` both `master` and `custom`) output their website build to this directory by default (unless overridden by the user's arguments to `build.py` ).
        - On Pull Requests, the website build in `dev` will be generated automatically into the `dev` directory. The build itself *may* (dependency on recency) be directly viewable by all in the browser by accessing the `dev` variant of the HTML files hosted by Github Pages for the corresponding fork.
        - When a Pull Request is merged into `main`, no `dev` folder will be included in the merge commit or rebase, and no `dev` build will be built in the deployment action.
- Github Actions:
    - `deploy.yml`: This is the single Action used for all deployment. It runs on every push to any branch in both the upstream repository and forks. It uses conditional steps (based on `github.repository`) to handle the two scenarios:
        - For **both** upstream and forks: Creates `textbook-stable-env` and performs a `stable` build (into `content`) using `--execution-type updated-unskipped-notebooks`. For the upstream `main` branch this build fails on error; for forks it continues on error.
        - **Upstream-only** (`jonescompneurolab/textbook` `main` branch): Deploys the built content to the official GitHub Pages website.
        - **Fork-only**: Additionally creates `textbook-dev-env` and performs a `master` build into `dev/`, then deploys both the stable `content` and `dev` output to the fork's GitHub Pages websites.

## Author standard-operating-procedures:

If an Author wants to add new or change existing MD or NB content, then they make their changes and push a Pull Request to `textbook` from their fork. Simple.

- The ONLY exception is if the Author wants to use a NB that requires *very* new code changes to `hnn-core` that are not yet merged into `master`(for example, if their NB relies on code that is currently only present in a Pull Request to `hnn-core`). In this case, the Author should explicitly tell the Maintainers that this is the case.

## Notes for Maintainers:

Due to the way we use Github Actions, for individual PRs, both a `stable` and `master`
build should be automatically built for each fork-branch that makes a PR. However, these
builds will NOT appear on the actual page for the Pull Request. Instead, you must go to
the actual fork's "Actions" tab to view the build progress (example:
https://github.com/asoplata/textbook/actions ). This is currently required in order to
run the builds "from" the fork directly, so that they can be published on that same
fork's Github Pages.

## Deployment flow:

Maintainers are dealing with up to four possible situations here:

### A. `jonescompneurolab/textbook`'s `main` branch:

Ideally, the only way that `main` branch is changed (except in cases of emergency) is via the the "official deployment", which is conducted by `deploy.yml` after a Pull Request is merged. The below describes effects of the `deploy.yml` Action.

- How it runs:
    - Execution: always set to `--execution-type updated-unskipped-notebooks`.
    - Version: `--code-version` is always using the default, which is `stable`.
    - Env: `textbook-stable-env`
- How it affects files/folders:
    - This produces a deployment commit onto the `gh-pages` branch which is what *actually* gets published to the final website.
    - This only needs the `content` and various asset files, builds only to `content`, and should not produce any `dev` files/folders.
    - This should have Github Action step to specifically add any existing `dev` content to the `.gitignore` such that any leftover `dev` content from a Pull Request is excluded.
- Failure modes:
    - Ideally, this should not have any, and hopefully never fail.

### B. `<fork>/textbook`'s PR-branch (three possible situations):

- *B.1.* For Fork-PRs, the `deploy.yml` Action is run. The first phase of this is the Action performing a `stable`-style build, identical to what `deploy.yml` does on the `main` branch.
    - How it runs:
        - Execution: `--execution-type updated-unskipped-notebooks`, same as before
        - Version: `--code-version stable`, same as before
        - Env: `textbook-stable-env`, same as before
    - How it affects files/folders:
        - This only needs the `content` and various asset files. It will change `.gitignore` so that it can track HTML files, enabling future Action-produced HTML output to be added to a future commit in the `gh-pages` branch. It will then produce output HTML pages and notebook-JSON-output files in `content`. It will then create a commit with all the output on the `gh-pages` branch. From the Fork-PR, this will be deployed to `<username>.github.io/textbook/content/preface.html` (during the final "Deploy to GitHub Pages (Fork)" step of `deploy.yml`).
            - Note: *Only the most recent* `stable` build of the fork will be deployed to `<username>.github.io/textbook/content/preface.html`, such as https://asoplata.github.io/textbook/content/preface.html . In other words, if a user has two PRs open, then their fork-specific deployment will *only* reflect the PR that had the most *recent* successful build (this will need to be communicated to Authors if they're doing multiple PRs).

    - Failure modes:
        - *B.1.1*: If a new or updated notebook from the PR breaks this `stable` build, then the Maintainers respond accordingly:
            - *B.1.1.1*: We first assume it's a bug in the notebook itself. Either we or the Author fix the bug in the PR, and the `stable` build is re-run automatically (thus using the build as a "test").
            - *B.1.1.2*: If it's a *new* notebook and relies on code that is only available in `master` but not `stable`, then we add the notebook to the `skip_if_stable` category.
            - *B.1.1.3*: If it's an *existing* notebook and the code changes rely on code that is only available in `master` but not `stable`, then we do the following:
                1. Retain the prior (`stable`-compatible version) version of the notebook (e.g. `<name>.ipynb`) from before the PR.
                2. Rename the version of the *changed* notebook to `master_only_<name>.ipynb`. It will be stored and accessible online, but not "published" and displayed in a webpage.
                3. Add `master_only_<name>.ipynb` to `skip_if_stable`.
        - *B.1.2*: If the problem comes from a notebook that is *not* changed in the PR, then the Maintainers know that something has broken upstream. This means there is a new bug between an existing notebook and `stable`. (Ideally this should never happen, but it should be fixed in a new, different PR.)

- *B.2.* For Fork-PRs, next is the second phase of `deploy.yml`. This is when the Action performs a `master` build into `dev`, independent of the output of the `stable` build in the first phase.
    - How it runs:
        - Execution: `--execution-type updated-unskipped-notebooks`, same as before
        - Version: UNLIKE before, `--code-version` is set to `master`
        - Env: UNLIKE before, `textbook-dev-env`
    - How it affects files/folders:
        - This only needs the `content` and various asset files. It will change `.gitignore` so that it can track HTML files and all files under `dev/`, enabling future Action-produced HTML output (both `content` and `dev`) to be added to a future commit in the `gh-pages` branch. It will produce output HTML pages and notebook-JSON-output files in `dev`. It will then create a commit with all the output on the `gh-pages` branch. From the Fork-PR, this will be deployed to `<username>.github.io/textbook/dev/preface.html` (during the final "Deploy to GitHub Pages (Fork)" step of `deploy.yml`).
            - Note: *Only the most recent* `master` build of the fork will be deployed to `<username>.github.io/textbook/dev/preface.html`, such as https://asoplata.github.io/textbook/dev/preface.html . In other words, if a user has two PRs open, then their fork-specific deployment will *only* reflect the PR that had the most *recent* successful build (this will need to be communicated to Authors if they're doing multiple PRs).
    - Failure modes:
        - *B.2.1*: If a new or updated notebook from the PR breaks this `master` build, then the Maintainers respond accordingly:
            - *B.2.1.1*: We first assume it's a bug in the notebook itself. Either we or the Author fix the bug in the PR, and the `master` build is re-run automatically (thus using the build as a "test").
            - *B.2.1.2*: If it's a new or existing notebook that is compatible with only `stable` but not `master`, then the notebook is breaking due to a non-backwards-compatible change in `master`. The notebook code needs to be changed so that there is a version compatible with `master` (and therefore the upcoming release).
                1. If there's a way to change the notebook to be compatible with both `stable` and `master`, then great, do that. (I mean cleanly, NOT using `if hnn_core.__version__ < XXX`).
                2. If not, then we need to do the following:
                    1. For the PR version of the notebook (compatible with `stable` but not `master`), add it to `skip_if_dev`.
                    2. Make a second version of the notebook that is compatible with `master` (and does *not* need to be compatible with `stable`).
                    3. Name this second, new notebook to `master_only_<name>.ipynb`. It will be stored and accessible online, but not "published" and displayed in a webpage.
                    4. Add `master_only_<name>.ipynb` to `skip_if_stable`.
        - *B.2.2*: If the problem comes from a notebook that is *not* changed in the PR, then the Maintainers know that something has broken upstream. In this case, we follow the same procedure as *B.2.1.2.*

- *B.3.* If a Fork-PR's notebook fails BOTH `stable` and `master` builds, then the following Failure Modes apply:
    - *B.3.1.* It's probably a bug. Fix it! (Hopefully it's a bug with the notebook, and not our Python build code…)
    - *B.3.2.* If it's not a bug, then it's probably because the notebook depends on a "`custom`" code change that is so new that it's not yet merged into master. In this case, the Maintainers should do the following:
        1. Include `[no ci]` in all future commit messages in order both not waste computation and to prevent overwriting of existing `dev` build output.
        2. Manually remove `dev/` from `.gitignore` in order to be able to push its output files to the PR branch. This will probably cause all CI runs to fail (which we want, in this case).
        3. Run a local `--code-version=custom --custom-owner-commit=<username>:<abc123>` build that builds into `dev` and uses the corresponding owner username/commit.
        4. Locally inspect the contents of the `dev` folder (if the Author ran `custom`) to inspect the output.
            - Note that because `[no ci]` will exclude the publishing of the fork's `dev` content, this PR's `dev` folder will *not* be viewable directly via Github pages.
        5. Rename the problem notebook to `custom_only_<name>.ipynb`
        6. Add `custom_only_<name>.ipynb` to both `skip_if_stable` and `skip_if_dev`.
        7. DON'T FORGET to re-add `dev/` to `.gitignore`.

## Maintainer Tasks for `hnn-core` upgrades

Finally, whenever there's a new HNN-core release, the Maintainers need to open a PR that does the following:

1. Possibly rename (aka "promote") any `custom_only_<name>.ipynb` notebooks based on:
    1. No rename if the PR they need is still open.
    2. Rename to `master_only_<name>.ipynb` if the commit they need is in `master` but was NOT included in the latest `stable` release. Then, remove the notebook from `skip_if_dev` but not `skip_if_stable`. (This probably will never happen).
    3. Overwrite their originals at `<name>.ipynb` if the commit they need was merged into `master` and is included in the latest `stable` release. Remove the notebook from both `skip_if_dev` and `skip_if_stable`.
2. Rename (aka "promote") all `master_only_<name>.ipynb` notebooks to overwrite their originals at `<name>.ipynb`. Remove them from `skip_if_stable`.
3. Then, do a comprehensive run of the latest `stable` and `master`. This includes the important step of generating output for the CPU-heavy notebooks we usually skip. Do the following:
    1. Manually remove any Optimization (and other CPU-heavy notebooks) from the appropriate `skip` categories.
    2. Then run `--execution-type=all-unskipped-notebooks` execution, for both `stable` and `master`. Check to see if everything executes and builds correctly.
    3. Delete the `dev` output (we don't need it).
    4. Retain and **push** your new version of the `content` directory. This is needed in order to properly populate the published webpages for CPU-heavy notebooks with output content.
    5. Re-add CPU-heavy notebooks back to the appropriate `skip` categories.
