# MicroProjects Contributing Guide
Welcome to MicroProjects.  
Thanks for taking time to contribute to MicroProjects! To streamline the process of contributing, we have some guidelines that you should follow. This guideline is steered towards begineers to Open Source.

# Table of Content
- [MicroProjects Contributing Guide](#microprojects-contributing-guide)
- [Table of Content](#table-of-content)
- [My First Contribution](#my-first-contribution)
    - [Getting Started](#getting-started)
    - [Cloning Git Repository](#cloning-git-repository)
    - [Identify Problem to solve](#identify-problem-to-solve)
        - [Find a new bug or want a new Feature](#find-a-new-bug-or-want-a-new-feature)
        - [Fix already opened Issues / feature requests](#fix-already-opened-issues--feature-requests)
        - [Want a new MircoProject](#want-a-new-mircoproject)
    - [Code It Up](#code-it-up)
    - [How to test/run](#how-to-testrun)
        - [Installing using pip](#installing-using-pip)
        - [Running Python scripts](#running-python-scripts)
    - [Get ready to share](#get-ready-to-share)
    - [Voila, done](#voila-done)


# My First Contribution
This guide is broken in sections, so you can skip some preliminary _stuff_ if you are already familiar with them.  


## Getting Started
This guide assumes that you are already familiar with `Python`, know how to install packages from PyPI and have a working `git`.

## Cloning Git Repository
First, you need to get the source-code on your local machine (or favourite cloud Application).
1. Go to the [fork page of MicroProjects](https://github.com/nyx-4/MicroProjects/fork), uncheck `Copy the main branch only` and then click **Create fork**.  
    ![Fork page of MicroProjects with (Copy main branch only) unchecked](https://github.com/user-attachments/assets/0ff51ab7-1d33-4dfb-9789-cf25f09828d6)
2. This will bring you to forked repository, copy the URL of this repository.  
   ![Forked page with URL selected and copied](https://github.com/user-attachments/assets/b6b12035-8e4e-4bef-8528-22bf57972c04)
3. Open the Terminal (Git Bash or WSL or PowerShell on Windows, any Terminal on MacOS/Linux/BSD), navigate to the directory (or Folder) where you want to clone and write `git clone URL`. For me, it is `git clone https://github.com/Nyx-50/MicroProjects`.
4. Install Python dependencies listed in `requirements.txt`
5. Open the directory named `MicroProjects` in your favourite code editor. For [VS Code](https://code.visualstudio.com/), it is `code MicroProjects`.

## Identify Problem to solve
Next identify a problem worth solving and open an issue (or feature request). This [Codecademy - YouTube](https://youtu.be/635dv9i3RhM) video may help visual listeners.

### Find a new bug or want a new Feature
Then open an [issue](https://github.com/nyx-4/MicroProjects/issues/new/choose). Make sure to add enough information about bug/feature and respond to queries of other in respectful manner.

### Fix already opened Issues / feature requests
If you can fix the already opened issues or add some new features, claim the issue explicitly. If you see that some issue is stale, you can also re-claim that issue or collaborate on that issue.

### Want a new MircoProject
If you want to add a new MicroProject or want someelse to add a new MicroProject, then write a comprehensive [Project Proposal](https://github.com/nyx-4/MicroProjects/issues?q=is%3Aissue%20label%3A%22Project%20Proposal%22). We will try our best to add that MicroProject ASAP.

## Code It Up
After claiming the issue, write the code. You have to follow certain conventions while coding.
1. The coding style is as detailed by [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/). I use ruff as Python formatter.
2. Use function and variable type annonatation as detailed in [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
3. Use docstring documentation for all functions. Use `Attributes` for class, `Parameters` and `Returns` by function. Follow the style as in `ngit` MicroProject.
4. Add clear tests using pytests, tests edge-cases and other behaviour. Make sure to write tests for exported functions, its okay to fail tests during development cycle.

## How to test/run
As MicroProjects is shipped as a Python Package, there are two ways to test it.

### Installing using pip
Use this to test overall CLI behaviour.
1. Install using pip in editable form for debugging or testing purpose using `pip install -e .` in MicroProjects root directory.
2. In terminal, use the provided command to run the setup. You can find the CLI command in respective `README` and `pyproject.toml` under `[project.scripts]`.
3. To test the CLI behaviour and expected output, we use [check50](https://cs50.readthedocs.io/projects/check50/en/latest/index.html). See the [Installation](https://cs50.readthedocs.io/projects/check50/en/latest/#installation), [Developing locally](https://cs50.readthedocs.io/projects/check50/en/latest/check_writer/#developing-locally) and [Getting started with Python checks](https://cs50.readthedocs.io/projects/check50/en/latest/check_writer/#getting-started-with-python-checks).

### Running Python scripts
Use this to test individual function.

## Get ready to share
After you have made your changes, open a Pull Request and be helpful.
1. Commit your changes by `git commit -am "A helpful message here."`
2. Push your changes to GitHub by `git push`.
3. Open the forked GitHub and click **Contribute** then click **Open Pull Request**.
   ![Click on (Contribute) and then (Open Pull Request)](https://github.com/user-attachments/assets/207d8494-7f9f-477d-b56a-fd4198b0157e)
4. Add a helpful title, Use [Closing keywords](https://docs.github.com/articles/closing-issues-using-keywords) in the description to automatically close issues. Then click **Create pull Request**.
   ![Add title, description and click (Create Pull Request)](https://github.com/user-attachments/assets/4e428e45-58cd-4606-b0ed-3e93d41bee22)
5. A merge request have been opened, respond to the reviews of your PR and wait for some Maintainer to **Merge your Pull Request**.


## Voila, done
And that was all it takes to contribute to Open Source.
