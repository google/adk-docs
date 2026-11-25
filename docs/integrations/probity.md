---
catalog_title: Probity ADK evidence gate
catalog_description: Verify a finite ADK plugin execution reference before publishing its retained report
catalog_icon: /integrations/assets/probity.png
catalog_tags: ["observability"]
---

# Probity evidence admission for ADK

[Probity's ADK reference](https://github.com/probityai/agent-evidence-observer/tree/c774e0711e4a30c31cdfb184c1e4495a249fbdd0/interop/adk-ticket-2026-10-02)
records model, tool and plugin callbacks alongside a protected ticket service's
signed effect records. A separately installed reader checks the retained
reference before a publication job may publish its admission receipt.

This integration supports a **fixed twelve-case synthetic reference**. It does
not admit arbitrary ADK application traces or measure model quality. The
producer and effect service share one operator; the signed records do not
establish independent effect custody.

## Use cases

- **Test callback and effect boundaries:** Preserve exhausted retries, errors
  after a committed effect, first/last plugin ordering and incomplete capture.
- **Maintain compatibility:** Run the unchanged reference against independently
  selected current SDK source and authenticate the installed source population.
- **Gate publication:** Require two identical decisions from an installed reader
  before uploading the bounded reference's report.

## Prerequisites

- Linux, Git and Python **3.13.15** for the selected execution profile.
- Access to public source repositories and Python package dependencies during
  installation. Native execution uses a local synthetic HTTP service and no
  provider inference, account or API key.
- A trusted interpreter, dependency installation, Python site initialization and
  working directory. The bootstrap checks selected package source bytes and
  refuses cached bytecode, linked package entries and alternate native modules
  before importing the SDK or reader.

The current-source profile selects ADK commit
`e94c2e726a269e0f04e2e4b202f5c131c80c20de`, whose installed version is `2.11.0`.
Version alone does not identify that source. It preserves the original
`probity-google-adk-ticket-v0` reader grammar and package versions. This is normal
source installation and compatibility testing; no registry release or package
upgrade is implied.

## Installation

Install the immutable original reader wheels and the selected current SDK in
separate environments. This source-installed integration has no PyPI release.
The dependency locks contain hashes; the bootstrap also selects both normally
built wheel digests, all 32 reader/Observer Python modules and all 778 SDK Python
Gitblob identities before native imports.

```bash
set -euo pipefail
export SOURCE_DATE_EPOCH=946684800
export PYTHONDONTWRITEBYTECODE=1
git clone https://github.com/probityai/agent-evidence-observer.git probity-adk
cd probity-adk
git checkout 75176f8696d7b58f20befd95dba8d0bc641ef604
git worktree add selected-reference c774e0711e4a30c31cdfb184c1e4495a249fbdd0
git worktree add selected-observer 4a50e61471355611121a578f3a4c22daa931d419
git clone https://github.com/google/adk-python.git selected-adk
git -C selected-adk checkout e94c2e726a269e0f04e2e4b202f5c131c80c20de
profile="$PWD/interop/adk-current-consumer-2026-10-03"
python3.13 -m venv "$PWD/producer-env"
python3.13 -m venv "$PWD/reader-env"
"$PWD/producer-env/bin/python" -m pip install --no-compile --require-hashes \
  -r "$profile/requirements.lock" -r "$profile/build.lock"
"$PWD/producer-env/bin/python" -m pip wheel --no-deps --no-build-isolation \
  "$PWD/selected-observer" \
  "$PWD/selected-reference/interop/adk-ticket-2026-10-02" --wheel-dir "$PWD/wheels"
"$PWD/producer-env/bin/python" -m pip install --no-compile --no-deps "$PWD/wheels/"*.whl
"$PWD/producer-env/bin/python" -m pip install --no-compile --no-deps \
  --no-build-isolation --force-reinstall "$PWD/selected-adk"
"$PWD/reader-env/bin/python" -m pip install --no-compile --require-hashes \
  -r "$profile/requirements-reader.lock"
"$PWD/reader-env/bin/python" -m pip install --no-compile --no-deps "$PWD/wheels/"*.whl
```

## Execute and admit the reference

The bootstrap declares all twelve cases, a unique run identity and the
25-model/18-tool callback and 120-second execution bounds before native imports.
It retains the host's full plan outside the packet before the first effect,
then independently selects captured original bytes for the consumer policy.

```bash
"$PWD/producer-env/bin/python" -I -B "$profile/bootstrap.py" \
  --producer "$PWD/producer-env/bin/python" \
  --reader "$PWD/reader-env/bin/python" \
  --wheels "$PWD/wheels" \
  --sdk-checkout "$PWD/selected-adk" \
  --output "$PWD/current-run"
```

A successful command writes `current-run/publication/publication-receipt.json`
only after both actual installed gate calls succeed with identical literal
output. It also retains raw native artifacts, selected source bytes, external
policy, stdout/stderr and each invocation's exit/timeout status. Task failure,
publication admission and completeness remain separate: a retained error after
a committed effect is evidence to preserve, not a successful task to invent.

## Use in a recurring publication job

Place the command above before an upload step, with ordinary shell failure
handling enabled. Use a new output directory for each run. Upload only when the
command succeeds. The maintained `publish_reference.py` sample can also consume
an existing retained reference with separately selected policy bytes, policy
SHA-256, absolute reader/interpreter paths and an output path outside the packet.

The owned workflow is a runnable reference placement. A consuming project's
merged recurring job and actual successful runs are separate evidence of
adoption; this page does not assert them.

## Resources

- [Current source selection and installed consumer](https://github.com/probityai/agent-evidence-observer/tree/75176f8696d7b58f20befd95dba8d0bc641ef604/interop/adk-current-consumer-2026-10-03)
- [Unchanged original ADK reference](https://github.com/probityai/agent-evidence-observer/tree/c774e0711e4a30c31cdfb184c1e4495a249fbdd0/interop/adk-ticket-2026-10-02)
- [Selected native ADK source](https://github.com/google/adk-python/tree/e94c2e726a269e0f04e2e4b202f5c131c80c20de)
