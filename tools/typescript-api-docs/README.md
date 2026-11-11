# TypeScript API reference

`generate.sh` rebuilds `docs/api-reference/typescript/` from a released
`@google/adk`. It clones the matching `adk-v<version>` tag of
[google/adk-js](https://github.com/google/adk-js) into a temporary directory,
installs its dependencies, runs TypeDoc, copies the HTML into this repository
and injects the analytics tag.

**The supported way to run it is the
[Update ADK TypeScript API Reference](../../.github/workflows/update-typescript-api-docs.yaml)
workflow.** Run it from the Actions tab, leave the version empty to take npm's
`latest`, and it opens the pull request. Running the script by hand still works
and is the right thing when you are changing the script itself -- see
[Changing this script](#changing-this-script).

## What it needs

`node` 18 or newer, `npm`, and `git`. The script redirects `npm_config_cache`
into its own temporary workspace, so it leaves no global installs behind and
does not touch `~/.npm` or any adk-js clone you already have. It does not
install node for you, and it is not meant to.

## Which version is "current"

npm's `dist-tags.latest` for `@google/adk`, not the GitHub release:

```shell
curl -fsSL https://registry.npmjs.org/@google/adk | jq -r '."dist-tags".latest'
```

adk-js is a release-please monorepo with package-prefixed tags, so
`releases/latest` frequently names a different package, and even when it names
the right one the npm publish can lag the GitHub release by minutes. The
library's own tag is `adk-v<version>`; the workflow checks it exists before
building.

## Why this builds in CI

`npm ci` installs the entire adk-js dependency tree -- around 1,100 locked
packages -- and TypeDoc then renders the API surface from the installed
sources. Two consequences are worth being deliberate about.

The output depends on the environment it was built in. Node version, npm
version and whatever is installed alongside all feed into the result, so the
same tag built on two machines can produce two different diffs. A single
pinned, disposable environment removes that variable, and since the generated
HTML is committed here, "whose machine built it" should not be a question
anyone has to ask in review.

It is also a sizeable install on every run. Nobody should need a current Node
toolchain and a thousand packages on hand just to update documentation, and a
runner starts clean every time.

This is also what the rest of the repository already does: `build-docs`,
`publish-docs`, `python-tests`, `update-python-docs` and
`feature-matrix-updater` all install their dependencies from public registries
on `ubuntu-latest`. The API reference generators were the exception.

What keeps the result trustworthy is the lockfile. `npm ci` installs locked
versions and verifies a sha512 hash for essentially every tarball, so the
dependency set is the one upstream published. **Do not** work around a failed
install by editing `package-lock.json` or passing `--force`: both defeat that,
and a reference built from a dependency set nobody pinned is not one to
publish. Fix the cause, or report it upstream.

## When the build breaks

The workflow checks its own output, so read which step failed.

| Step that failed | What it means |
|---|---|
| Resolve the version | npm was unreachable, or an input that was not `X.Y.Z` |
| Check the release tag exists | `adk-v<version>` is not on google/adk-js. Usually the npm publish and the git tag are out of step; wait and retry |
| Generate the TypeScript API reference | The real build. See below |
| Check the output is real | TypeDoc exited 0 but produced too few pages, or the version or analytics tag is missing |

A failure in the generate step is almost always one of:

- **adk-js moved its docs setup.** The script runs `npm run docs:generate` and
  copies from `api-reference/typescript/` in the clone. If either the script
  name or the output path changes upstream, this needs updating in step.
- **TypeDoc failed on new source.** Read the log; it names the file.
- **A dependency would not install.** On a runner this is rare, and almost
  always something upstream published or yanked. Read the npm error; it names
  the package.

"Check the output is real" exists because the script's last act is a `find`
loop that is perfectly happy with an empty directory, so an empty or
unversioned build used to be able to exit 0.

## Changing this script

Editing anything under `tools/typescript-api-docs/` triggers the workflow on
your pull request. It runs the full build against npm's current `latest` and
checks the output, but opens no pull request. That is the intended way to test
a change here, and it is also what keeps the generator from quietly rotting
between releases -- which is how it broke last time.
