# How to contribute

Thank you for your interest in contributing! We appreciate your willingness to
share your patches and improvements with the project.

## Getting Started

Before you contribute, please take a moment to review the following:

### 1. Sign our Contributor License Agreement

Contributions to this project must be accompanied by a
[Contributor License Agreement](https://cla.developers.google.com/about) (CLA).
You (or your employer) retain the copyright to your contribution; this simply
gives us permission to use and redistribute your contributions as part of the
project.

If you or your current employer have already signed the Google CLA (even if it
was for a different project), you probably don't need to do it again.

Visit <https://cla.developers.google.com/> to see your current agreements or to
sign a new one.

### 2. Review Community Guidelines

We adhere to [Google's Open Source Community Guidelines](https://opensource.google/conduct/).
Please familiarize yourself with these guidelines to ensure a positive and
collaborative environment for everyone.

## Contribution Workflow

### Finding Something to Work On

Check the [GitHub Issues](https://github.com/google/adk-docs/issues) for bug
reports or feature requests. Feel free to pick up an existing issue or open
a new one if you have an idea or find a bug.

### Development Setup

1.  **Clone the repository:**

    ```shell
    git clone git@github.com:google/adk-docs.git
    cd adk-docs
    ```

2.  **Create and activate a virtual environment:**

    ```shell
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```shell
    pip install -r requirements.txt
    ```

4.  **Run the local development server:**

    ```shell
    mkdocs serve
    ```

    This command starts a local server, typically at `http://127.0.0.1:8000/`.

    The site will automatically reload when you save changes to the documentation files.
    For more details on the site configuration, see the mkdocs.yml file.

### Code Reviews

All contributions, including those from project members, undergo a review process.

1.  **Create a Pull Request:** We use GitHub Pull Requests (PRs) for code review.
    Please refer to GitHub Help if you're unfamiliar with PRs.
2.  **Review Process:** Project maintainers will review your PR, providing feedback
    or requesting changes if necessary.
3.  **Merging:** Once the PR is approved and passes any required checks, it will be
    merged into the main branch.

Consult [GitHub Help](https://help.github.com/articles/about-pull-requests/) for
more information on using pull requests. We look forward to your contributions!
