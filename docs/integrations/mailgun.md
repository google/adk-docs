---
catalog_title: Mailgun
catalog_description: Send emails, track delivery metrics, and manage mailing lists
catalog_icon: /integrations/assets/mailgun.png
catalog_tags: ["mcp"]
---

# Mailgun MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Mailgun MCP Server](https://github.com/mailgun/mailgun-mcp-server) connects
your ADK agent to [Mailgun](https://www.mailgun.com/), a transactional email
service. This integration gives your agent the ability to send emails, track
delivery metrics, manage domains and templates, and handle mailing lists using
natural language.

## Use cases

- **Send and Manage Emails**: Compose and send transactional or marketing emails,
  retrieve stored messages, and resend messages through conversational commands.

- **Monitor Delivery Performance**: Fetch delivery statistics, analyze bounce
  classifications, and review suppression lists to maintain sender reputation.

- **Manage Email Infrastructure**: Verify domain DNS configuration, configure
  tracking settings, create email templates, and set up inbound routing rules.

## Prerequisites

- Create a [Mailgun account](https://www.mailgun.com/)
- Generate an API key from the
  [Mailgun Dashboard](https://app.mailgun.com/settings/api_security)

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        --8<-- "examples/inline/python/integrations/mailgun/001-use-with-agent.py"
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        --8<-- "examples/inline/typescript/integrations/mailgun/002-use-with-agent.ts"
        ```

## Available tools

### Messaging

Tool | Description
---- | -----------
`send_email` | Send an email with support for HTML content and attachments
`get_stored_message` | Retrieve a stored email message
`resend_message` | Resend a previously sent message

### Domains

Tool | Description
---- | -----------
`get_domain` | View details for a specific domain
`verify_domain` | Verify DNS configuration for a domain
`get_tracking_settings` | View tracking settings (click, open, unsubscribe)
`update_tracking_settings` | Update tracking settings for a domain

### Webhooks

Tool | Description
---- | -----------
`list_webhooks` | List all event webhooks for a domain
`create_webhook` | Create a new event webhook
`update_webhook` | Update an existing webhook
`delete_webhook` | Delete a webhook

### Routes

Tool | Description
---- | -----------
`list_routes` | View inbound email routing rules
`update_route` | Update an inbound routing rule

### Mailing lists

Tool | Description
---- | -----------
`create_mailing_list` | Create a new mailing list
`manage_list_members` | Add, remove, or update mailing list members

### Templates

Tool | Description
---- | -----------
`create_template` | Create a new email template
`manage_template_versions` | Create and manage template versions

### Analytics and stats

Tool | Description
---- | -----------
`query_metrics` | Query sending and usage metrics for a date range
`get_logs` | Retrieve email event logs
`get_stats` | View aggregate statistics by domain, tag, provider, device, or country

### Suppressions

Tool | Description
---- | -----------
`get_bounces` | View bounced email addresses
`get_unsubscribes` | View unsubscribed email addresses
`get_complaints` | View complaint records
`get_allowlist` | View allowlist entries

### IPs

Tool | Description
---- | -----------
`list_ips` | View IP assignments
`get_ip_pools` | View dedicated IP pool configuration

### Bounce classification

Tool | Description
---- | -----------
`get_bounce_classification` | Analyze bounce types and delivery issues

## Configuration

Variable | Required | Default | Description
-------- | -------- | ------- | -----------
`MAILGUN_API_KEY` | Yes | — | Your Mailgun API key
`MAILGUN_API_REGION` | No | `us` | API region: `us` or `eu`

## Additional resources

- [Mailgun MCP Server Repository](https://github.com/mailgun/mailgun-mcp-server)
- [Mailgun MCP Integration Guide](https://www.mailgun.com/resources/integrations/mcp-server/)
- [Mailgun Documentation](https://documentation.mailgun.com/)
