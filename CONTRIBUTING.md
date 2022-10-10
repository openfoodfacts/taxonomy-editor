# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at <https://github.com/openfoodfacts/taxonomy-editor/issues>.

If you are reporting a bug, please include:

- Your operating system name and version, or the browser you used.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it. Issues tagged with "good first issue" are suitable for newcomers.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Add tests

We need more test to augment our coverage.
Feel free to either add unit or integration tests.

### Write Documentation

Taxonomy Editor needs a lot of documentation,
whether in docs/ folder or in docstrings.

### Submit Feedback

The best way to send feedback is to file an issue at
<https://github.com/openfoodfacts/taxonomy-editor/issues>.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions are welcome.

## Get Started!

Ready to contribute code? Here's how to set up Taxonomy Editor for local development.

1.  Fork the taxonomy-editor repo on GitHub.
2.  Clone your fork locally:

    ```
    git clone git@github.com:your_name_here/taxonomy-editor.git
    ```
3. Follow [install documentation](./docs/explanations/docker-compose-setup.md)

4. code!

5. TODO: add explanations about linting / checks / tests when we have automated them.

6.  Commit your changes and push your branch to GitHub:

    ```
    git status
    git add files-you-have-modified
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

    In brief, commit messages should follow these conventions:

    > - Always start using 
        [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) 
        prefix, e.g. "fix: ..." or "feat: ..."
    > - Always contain a subject line which briefly describes the changes made. For example "fix: fixed typo in CONTRIBUTING.md".
    > - Subject lines should not exceed 50 characters, but you can add more line after
    > - The commit body should contain context about the change - how the code worked before,
        how it works now and why you decided to solve the issue in the way you did.

    More tips at <https://chris.beams.io/posts/git-commit>

7.  Submit a pull request through the GitHub website (see below).

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. Please name your PR's using Conventional Commits e.g. "fix: ..." or "feat: ..."
2. You don't have to anything to the CHANGELOG.md yourself, this is done automatically
3. Please ensure to add a before/after screenshot when doing a PR that has visual impacts

1. if possible, the pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring.


This contributing page was adapted from [Pyswarms documentation](https://github.com/ljvmiranda921/pyswarms/blob/master/CONTRIBUTING.rst).