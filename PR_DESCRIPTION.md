## Description

This PR adds comprehensive documentation for implementing OpenTelemetry tracing with Vertex AI Agent Engine, addressing issue #1215.

The issue reported that documentation was insufficient to properly implement OpenTelemetry for Agent Engine, leading to blank dashboards and missing traces. The root cause was the lack of documentation about the critical initialization sequence - specifically that tracing MUST be initialized within the `AdkApp.set_up()` method.

## Changes Made

### New Documentation

- **`docs/observability/tracing-agent-engine.md`** - Comprehensive guide covering:
  - Why initialization order matters (critical section explaining the `set_up()` requirement)
  - Architecture diagram showing trace flow from agent to dashboard
  - Two implementation methods (environment variables and manual configuration)
  - Complete code examples with proper initialization patterns
  - Infrastructure configuration (Terraform, IAM)
  - Troubleshooting guide for common issues
  - Best practices for production deployments

### Updated Documentation

- **`docs/observability/index.md`** - Updated to link to the new tracing guide
- **`mkdocs.yml`** - Added navigation entry for the new tracing page

## Technical Implementation

The documentation addresses all points raised in issue #1215:

1. ✅ **Documenting the init sequence clearly**
   - Explains why `set_up()` is required
   - Shows correct vs incorrect initialization patterns
   - Provides complete working examples

2. ✅ **Documenting canonical data flows**
   - Architecture diagram showing flow from agent → Agent Engine → Cloud Trace → Vertex AI Dashboard
   - Explains span structure and hierarchy
   - Details span attributes for each operation type

3. ✅ **Architecture diagram of infrastructure configuration**
   - Visual diagram of the complete tracing pipeline
   - Terraform configuration examples
   - IAM permission requirements

4. ✅ **Reference to adk-samples**
   - Links to Agent Starter Pack in additional resources
   - References the starter pack as a reference implementation

## Key Features

### Critical Warning Section
Added a prominent warning box at the top explaining the initialization requirement:

> OpenTelemetry tracing initialization MUST occur within the `AdkApp.set_up()` method when deploying to Agent Engine. Initializing tracing outside of this lifecycle method will result in blank dashboards and missing traces.

### Two Implementation Paths

1. **Environment Variables (Recommended)** - Simple approach using `--trace_to_cloud` flag or `enable_tracing=True`
2. **Manual Configuration** - Advanced approach with full control over OpenTelemetry setup

### Comprehensive Troubleshooting

Covers common issues:
- Blank dashboard / no traces
- Incomplete traces
- Missing prompt/response content
- High trace volume / cost concerns

Each issue includes symptoms and specific solutions.

### Production Best Practices

- Sampling strategies for cost control
- Error handling patterns
- Environment-based configuration
- Custom span attributes

## Testing

- [x] Documentation follows existing ADK docs style and structure
- [x] Code examples are complete and runnable
- [x] All links are valid
- [x] Navigation is properly configured in mkdocs.yml
- [x] Markdown formatting is correct

## Related Issue

Closes #1215

## Checklist

- [x] Documentation is clear and comprehensive
- [x] Code examples follow ADK best practices
- [x] Architecture diagrams are included
- [x] Troubleshooting section addresses common issues
- [x] Links to related documentation are provided
- [x] Navigation is updated in mkdocs.yml
- [x] Follows the repository's documentation style guide
