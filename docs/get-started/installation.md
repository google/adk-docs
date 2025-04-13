# Installing ADK

## Create & activate virtual environment

We recommend creating a virtual Python environment using
[venv](https://docs.python.org/3/library/venv.html):

```shell
python -m venv .venv
```

Now, you can activate the virtual environment using the appropriate command for
your operating system and environment:

```
# Mac / Linux
source .venv/bin/activate

# Windows CMD:
.venv\Scripts\activate.bat

# Windows PowerShell:
.venv\Scripts\Activate.ps1
```

### Install ADK

```bash
pip install google-adk
```

(Optional) Verify your installation:

```bash
pip show google-adk
```

## Next steps

* Try creating your first agent with the [**Quickstart**](quickstart.md)
