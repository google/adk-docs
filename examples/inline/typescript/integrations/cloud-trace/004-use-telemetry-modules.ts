import { getGcpExporters, maybeSetOtelProviders } from '@google/adk';

// Get GCP exporters configuration
const gcpExporters = await getGcpExporters({
  enableTracing: true,
});

// Initialize and set global OTel providers
maybeSetOtelProviders([gcpExporters]);

// ... your agent code ...