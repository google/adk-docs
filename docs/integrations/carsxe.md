---
catalog_title: CarsXE
catalog_description: Decode VINs and license plates, and fetch vehicle specs, market value, history, and recalls
catalog_icon: /integrations/assets/carsxe.png
catalog_tags: ["mcp"]
---

# CarsXE MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [CarsXE MCP server](https://github.com/carsxe/carsxe-mcp-server) connects your
ADK agent to the [CarsXE](https://carsxe.com/) vehicle data platform. It
exposes CarsXE's APIs — VIN decoding and full specifications, license-plate
decoding, market value, title and ownership history, safety recalls, lien and
theft records, OBD-II code decoding, and image lookups — as MCP tools your agent
can call with natural language such as "Decode VIN 1HGBH41JXMN109186" or "Are
there open recalls on this car?".

The server is hosted at `https://mcp.carsxe.com/mcp` over streamable HTTP, so no
local install is required — the agent connects to the remote endpoint directly.

## Use cases

- **Decode a VIN or plate**: Turn a 17-character VIN or a license plate into
  structured make, model, year, engine, trim, and equipment data so the agent
  can reason about a specific vehicle.

- **Assess a vehicle**: Retrieve market value, full title and ownership history,
  and open safety recalls to support buying, selling, and servicing decisions.

- **Diagnose problems**: Decode OBD-II trouble codes (e.g. `P0300`) into
  human-readable definitions and likely causes.

- **Read vehicle images**: Extract a VIN or plate from a photo, and fetch
  vehicle images by make and model.

## Prerequisites

- A working [ADK installation](/get-started/installation/)
- A CarsXE API key — sign up at
  [api.carsxe.com](https://api.carsxe.com/dashboard/developer) and copy your key

## Use with agent

The agent connects to the hosted CarsXE MCP server over streamable HTTP and
authenticates with your API key via the `X-API-Key` header.

=== "Python"

    ```python
    --8<-- "examples/inline/python/integrations/carsxe/001-use-with-agent.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/integrations/carsxe/002-use-with-agent.ts"
    ```

## Available tools

Tool | Description
---- | -----------
`get-vehicle-specs` | Decode a VIN into full vehicle specifications (make, model, year, engine, trim, equipment)
`decode-vehicle-plate` | Decode a license plate into vehicle data
`get-market-value` | Estimate a vehicle's market value by VIN
`get-vehicle-history` | Retrieve title, ownership, accident, and odometer history by VIN
`get-vehicle-recalls` | Check open safety recalls by VIN
`get-lien-theft` | Check lien and theft records by VIN
`international-vin-decoder` | Decode a non-US (international) VIN
`vin-ocr` | Extract a VIN from an image using OCR
`recognize-plate-image` | Recognize a license plate from an image
`get-year-make-model` | Look up specifications by year, make, and model
`get-vehicle-images` | Retrieve vehicle images by make and model
`decode-obd-code` | Decode an OBD-II diagnostic trouble code

## Additional resources

- [CarsXE MCP server repository](https://github.com/carsxe/carsxe-mcp-server)
- [CarsXE API documentation](https://api.carsxe.com/docs)
- [CarsXE homepage](https://carsxe.com/)
- [Get a CarsXE API key](https://api.carsxe.com/dashboard/developer)
