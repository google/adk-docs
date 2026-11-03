# Java API reference

`generate.sh` rebuilds `docs/api-reference/java/` from a released adk-java. It
clones the matching `v<version>` tag of
[google/adk-java](https://github.com/google/adk-java) into a temporary
directory, builds an aggregate Javadoc JAR with that repository's own Maven
wrapper, extracts it here and injects the analytics tag.

**The supported way to run it is the
[Update ADK Java API Reference](../../.github/workflows/update-java-api-docs.yaml)
workflow.** Run it from the Actions tab, leave the version empty to take the
latest adk-java release, and it opens the pull request. Running the script by
hand still works and is the right thing when you are changing the script
itself -- see [Changing this script](#changing-this-script).

## What it needs

A JDK, `jar`, and `git`. Maven itself is not required: the script uses
adk-java's `./mvnw` wrapper, so the build uses the Maven version that release
was built with rather than whatever happens to be installed.

**Which JDK matters to the output.** adk-java compiles against release 17 and
that does not change, but the Javadoc tool doing the rendering is whichever
one your JDK ships, and it stamps its own version into every page it writes.
CI pins JDK 26 in
[the workflow](../../.github/workflows/update-java-api-docs.yaml); build on
anything else and every file will differ from what is committed. The workflow
asserts the two things that used to be wrong here -- that the pages were
rendered by the JDK it pinned, and that the copyright footer is not the 1980
one described below.

## Which version is "current"

The GitHub release on `google/adk-java`:

```shell
gh api repos/google/adk-java/releases/latest --jq .tag_name
```

Note this differs from the TypeScript reference, where npm is authoritative.
Maven Central (`com.google.adk:google-adk`) can lag the GitHub release, so
treat it as a cross-check rather than the source. The in-repo version is in
the `<title>` of `docs/api-reference/java/index.html`, which reads
"Maven Parent POM X.Y.Z API".

## What this does not cover

Only the generated reference under `docs/api-reference/java/`. The
`com.google.adk` coordinates quoted in prose and in `examples/java/**/pom.xml`
are hand-maintained and are a separate change -- the workflow deliberately
restricts its pull request to the reference directory so the two do not get
mixed together in review.

## Why this builds in CI

The build compiles adk-java from source and resolves its full Maven
dependency set. That makes the output a function of the environment it was
built in -- JDK vendor and version, and what Maven happened to resolve on the
day -- so the same tag built on two machines can produce two different diffs.
The generated HTML is committed to this repository, so that difference lands
in review, and "whose machine built it" should not be a question anyone has to
ask.

It is also not a small build. Nobody should need a JDK and a warm Maven cache
on hand to update documentation, and a runner starts clean every time.

This is also what the rest of the repository already does: `build-docs`,
`publish-docs`, `python-tests`, `update-python-docs` and
`feature-matrix-updater` all install their dependencies from public registries
on `ubuntu-latest`. The API reference generators were the exception.

## The copyright footer

Javadoc's default footer is
"Copyright {inceptionYear}-{currentYear} {organizationName}. All rights
reserved.", filled in from the pom. adk-java sets neither `<inceptionYear>`
nor a project-level `<organization>` -- the only `<organization>` in it sits
inside `<developers>`, which is a different field the plugin does not read --
so the footer collapsed to "Copyright &#169; 1980. All rights reserved.": no
owner, and the ZIP epoch instead of a year.

`generate.sh` now passes `-Dbottom` explicitly. The year is the year of the
release being documented, read from the tag it checked out, rather than the
year the build runs. That matters because these pages are committed here: a
footer that followed the wall clock would rewrite every file the first time
somebody rebuilt an older version.

If adk-java later sets `<inceptionYear>` and a project-level
`<organization>`, this override can go.

## When the build breaks

The script and the workflow both check their own output, so read which step
failed.

| Step that failed | What it means |
|---|---|
| Resolve the version | GitHub was unreachable, or an input that was not `X.Y.Z` |
| Check the release tag exists | `v<version>` is not on google/adk-java |
| Generate the Java API reference | The real build. See below |
| Check the output is real | The Javadoc came out but looks wrong: too few pages, `META-INF` published, or the analytics tag missing |

Inside the generate step, the script fails deliberately in three places worth
recognising:

- **`Expected exactly one javadoc jar`** -- the aggregate build produced none
  or several. Usually adk-java changed its module layout or its artifact id.
- **`index.html renders 'X' but 'Y' was requested`** -- the Javadoc built, but
  for a different version than asked for. Normally a tag that does not contain
  what its name suggests.
- **A Maven failure.** Read the log; it names the module and the dependency.

## Changing this script

Editing anything under `tools/java-api-docs/` triggers the workflow on your
pull request. It runs the full build against the current release and checks
the output, but opens no pull request. That is the intended way to test a
change here, and it is what keeps the generator from quietly rotting between
releases.
