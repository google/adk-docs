---
catalog_title: CarsXE
catalog_description: Decode VINs and license plates, and fetch vehicle specs, history, market value, and recalls
catalog_icon: /integrations/assets/carsxe.png
catalog_tags: ["tools","automotive"]
---

# CarsXE tools for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [CarsXE API](https://api.carsxe.com) gives your ADK agent access to
comprehensive vehicle data: VIN decoding, full specifications, market value,
title and ownership history, open safety recalls, lien and theft records,
license-plate decoding, and year/make/model lookups. Wrap the REST endpoints as
ADK [function tools](/tools-custom/) and your agent can answer natural-language
questions such as "What engine is in VIN 1HGBH41JXMN109186?" or "Are there any
open recalls on this car?".

## Use cases

- **Decode a VIN**: Turn a 17-character VIN into structured make, model, year,
  engine, trim, and equipment data so your agent can reason about a specific
  vehicle.

- **Look up a license plate**: Resolve a plate number and region into vehicle
  details when a VIN is not available.

- **Assess a vehicle**: Retrieve market value, full title and ownership history,
  and open safety recalls to help users make buying, selling, or servicing
  decisions.

- **Diagnose problems**: Decode OBD-II trouble codes (e.g. `P0300`) into
  human-readable definitions and likely causes.

## Prerequisites

- Python 3.9+ and a working [ADK installation](/get-started/installation/)
- The `requests` library: `pip install requests`
- A CarsXE API key — sign up at [api.carsxe.com](https://api.carsxe.com) and copy
  your key from the dashboard

## Installation

```bash
pip install google-adk requests
```

Set your API key as an environment variable:

```bash
export CARSXE_API_KEY="YOUR_API_KEY"
```

## Use with agent

Define each CarsXE endpoint as a plain Python function. ADK automatically turns
the function signature and docstring into a tool schema the model can call.

```python
import os
import requests
from google.adk.agents import Agent

CARSXE_BASE_URL = "https://api.carsxe.com"
CARSXE_API_KEY = os.environ["CARSXE_API_KEY"]


def _get(path: str, params: dict) -> dict:
    """Call a CarsXE GET endpoint with the API key attached."""
    params = {"key": CARSXE_API_KEY, **params}
    response = requests.get(f"{CARSXE_BASE_URL}{path}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def get_vehicle_specs(vin: str) -> dict:
    """Decode a VIN into full vehicle specifications.

    Args:
        vin: The 17-character Vehicle Identification Number.

    Returns:
        Vehicle attributes such as make, model, year, engine, and trim.
    """
    return _get("/specs", {"vin": vin})


def get_market_value(vin: str) -> dict:
    """Get the estimated market value of a vehicle by VIN.

    Args:
        vin: The 17-character Vehicle Identification Number.

    Returns:
        Estimated market value and valuation details.
    """
    return _get("/v2/marketvalue", {"vin": vin})


def get_vehicle_history(vin: str) -> dict:
    """Get title, ownership, accident, and odometer history for a VIN.

    Args:
        vin: The 17-character Vehicle Identification Number.

    Returns:
        Historical records including past owners, accidents, and title status.
    """
    return _get("/history", {"vin": vin})


def get_recalls(vin: str) -> dict:
    """Check for open safety recalls on a vehicle by VIN.

    Args:
        vin: The 17-character Vehicle Identification Number.

    Returns:
        A list of open safety recalls for the vehicle.
    """
    return _get("/v1/recalls", {"vin": vin})


def decode_license_plate(plate: str, country: str = "US", state: str = "") -> dict:
    """Decode a license plate into vehicle details.

    Args:
        plate: The license plate number.
        country: ISO 3166-1 alpha-2 country code (default "US").
        state: Two-letter state or province code. Required for US, AU, CA, PK.

    Returns:
        Vehicle information associated with the plate.
    """
    params = {"plate": plate, "country": country}
    if state:
        params["state"] = state
    return _get("/v2/platedecoder", params)


def get_year_make_model(year: str, make: str, model: str, trim: str = "") -> dict:
    """Look up vehicle specifications by year, make, and model (no VIN needed).

    Args:
        year: Model year, e.g. "2020".
        make: Vehicle make, e.g. "Toyota".
        model: Vehicle model, e.g. "Camry".
        trim: Optional trim level, e.g. "LE".

    Returns:
        Vehicle specifications matching the year/make/model.
    """
    params = {"year": year, "make": make, "model": model}
    if trim:
        params["trim"] = trim
    return _get("/v1/ymm", params)


def decode_obd_code(code: str) -> dict:
    """Decode an OBD-II diagnostic trouble code into a definition.

    Args:
        code: The OBD-II code, e.g. "P0300".

    Returns:
        The code definition and likely causes.
    """
    return _get("/obdcodesdecoder", {"code": code})


root_agent = Agent(
    model="gemini-flash-latest",
    name="carsxe_agent",
    instruction=(
        "You are a vehicle data assistant. Use the CarsXE tools to decode VINs "
        "and license plates and to look up specifications, market value, history, "
        "recalls, and OBD-II codes. Always cite the specific field values you "
        "retrieve."
    ),
    tools=[
        get_vehicle_specs,
        get_market_value,
        get_vehicle_history,
        get_recalls,
        decode_license_plate,
        get_year_make_model,
        decode_obd_code,
    ],
)
```

## Available tools

The example above wraps the most common CarsXE endpoints. The full API exposes
the following:

Tool | Description
---- | -----------
`get_vehicle_specs` | Decode a VIN into full vehicle specifications (`/specs`)
`get_market_value` | Estimate a vehicle's market value by VIN (`/v2/marketvalue`)
`get_vehicle_history` | Retrieve title, ownership, and accident history by VIN (`/history`)
`get_recalls` | Check open safety recalls by VIN (`/v1/recalls`)
`get_lien_theft` | Check lien and theft records by VIN (`/v1/lien-theft`)
`decode_international_vin` | Decode a non-US VIN (`/v1/international-vin-decoder`)
`decode_license_plate` | Decode a license plate into vehicle data (`/v2/platedecoder`)
`recognize_plate_image` | Recognize a plate from an image URL (`/platerecognition`)
`vin_ocr` | Extract a VIN from an image using OCR (`/v1/vinocr`)
`get_year_make_model` | Look up specs by year/make/model (`/v1/ymm`)
`get_vehicle_images` | Retrieve vehicle images by make and model (`/images`)
`decode_obd_code` | Decode an OBD-II trouble code (`/obdcodesdecoder`)

## Additional resources

- [CarsXE API documentation](https://api.carsxe.com/docs)
- [CarsXE homepage](https://www.carsxe.com/)
- [CarsXE CLI on npm](https://www.npmjs.com/package/carsxe-cli)
- [Get an API key](https://api.carsxe.com/)
