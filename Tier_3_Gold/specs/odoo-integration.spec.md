# Specification: Odoo Integration (Gold Tier)

## MCP Server Definition

```yaml
Name: odoo-mcp
Type: Model Context Protocol Server (Odoo JSON-RPC)
Language: Python or Node.js
Status: Ready for Implementation
Dependencies: Odoo Community 19+, odoorpc or odoo-bin-xmlrpc
Timeline: Week 10 (during CEO briefing implementation)
SLO: 99.5% uptime, <1000ms latency p95
```

## Purpose

MCP server that exposes Odoo Community Edition accounting capabilities for autonomous financial management:
- Retrieve invoices and payment status
- Query customer data and transaction history
- Generate financial reports
- Track expenses and cash flow
- Calculate business metrics

## Architecture

```
Claude Code (Client)
        ↓
odoo-mcp Server (localhost:3002)
        ↓
Odoo JSON-RPC API
        ↓
Odoo Community Database (Self-Hosted)
```

## Setup Requirements

### Self-Hosted Odoo Community

**Installation** (Docker recommended):
```bash
docker run -d \
  -p 8069:8069 \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=odoo \
  --name odoo \
  odoo:19
```

**Access**: http://localhost:8069

**Initial Setup**:
1. Create database on first login
2. Create user account (default: admin/admin)
3. Install Accounting module (Invoices & Payments)
4. Create sample customers and products (if needed)

### Environment Variables

```bash
# .env
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=<secure-password>
ODOO_TIMEOUT=30
```

## Tools

### 1. get_invoices

**Purpose**: Retrieve invoices with optional filtering

**Inputs**:
- `status` (string, optional): "draft", "posted", "paid", "all" (default: "posted")
- `customer_id` (int, optional): Filter by customer
- `date_from` (string, optional): ISO date (e.g., "2026-01-01")
- `date_to` (string, optional): ISO date (e.g., "2026-12-31")
- `limit` (int, optional): Max results (default: 50, max: 500)

**Output**:
```json
{
  "status": "success",
  "count": 24,
  "invoices": [
    {
      "id": 1,
      "number": "INV-2026-001",
      "customer": "Acme Corp",
      "date": "2026-02-15",
      "amount": 5000.00,
      "currency": "USD",
      "status": "posted",
      "due_date": "2026-03-15",
      "paid_date": null,
      "amount_paid": 0.00,
      "amount_due": 5000.00
    }
  ]
}
```

**Use Cases**:
- Find overdue invoices (for CEO briefing)
- Calculate weekly revenue
- Identify payment status
- Verify customer transaction history

### 2. get_customers

**Purpose**: Retrieve customer data with transaction history

**Inputs**:
- `limit` (int, optional): Max results (default: 20, max: 100)
- `active_only` (boolean, optional): Exclude inactive customers (default: true)
- `sale_amount_min` (float, optional): Min lifetime sales (e.g., 1000)
- `last_sale_days` (int, optional): Last N days of sales

**Output**:
```json
{
  "status": "success",
  "count": 47,
  "customers": [
    {
      "id": 15,
      "name": "Acme Corp",
      "email": "contact@acme.com",
      "phone": "+1-555-0100",
      "city": "New York",
      "country": "USA",
      "lifetime_sales": 125000.00,
      "total_invoices": 12,
      "paid_invoices": 10,
      "unpaid_amount": 15000.00,
      "last_invoice_date": "2026-02-26",
      "last_payment_date": "2026-02-20",
      "credit_limit": 50000.00,
      "credit_used": 35000.00
    }
  ]
}
```

**Use Cases**:
- Identify top customers
- Check credit limits
- Monitor payment behavior
- Generate customer health report

### 3. get_revenue

**Purpose**: Calculate revenue metrics for time period

**Inputs**:
- `date_from` (string, required): ISO date
- `date_to` (string, required): ISO date
- `status` (string, optional): "posted" or "paid" (default: "posted")
- `by_customer` (boolean, optional): Break down by customer (default: false)

**Output**:
```json
{
  "status": "success",
  "period": {
    "from": "2026-02-20",
    "to": "2026-02-26"
  },
  "summary": {
    "total_revenue": 48500.00,
    "invoice_count": 20,
    "average_invoice": 2425.00,
    "currency": "USD"
  },
  "payment_breakdown": {
    "paid": 42000.00,
    "pending": 6500.00,
    "percentage_paid": 86.5
  },
  "by_customer": [
    {
      "customer": "Acme Corp",
      "amount": 15000.00,
      "invoices": 3
    }
  ]
}
```

**Use Cases**:
- CEO briefing revenue section
- Weekly performance tracking
- Sales forecasting
- Customer concentration analysis

### 4. get_expenses

**Purpose**: Retrieve expense data and categorization

**Inputs**:
- `date_from` (string, required): ISO date
- `date_to` (string, required): ISO date
- `category` (string, optional): "all", "payroll", "marketing", "operations"
- `limit` (int, optional): Max results (default: 50)

**Output**:
```json
{
  "status": "success",
  "period": {
    "from": "2026-02-01",
    "to": "2026-02-26"
  },
  "summary": {
    "total_expenses": 12500.00,
    "by_category": {
      "payroll": 8000.00,
      "marketing": 2500.00,
      "operations": 2000.00
    }
  },
  "details": [
    {
      "date": "2026-02-20",
      "description": "Salary distribution",
      "category": "payroll",
      "amount": 8000.00,
      "vendor": "Internal"
    }
  ]
}
```

**Use Cases**:
- Budget tracking
- Expense analysis
- Cash flow planning
- Cost optimization suggestions

### 5. create_invoice

**Purpose**: Create new invoice (with HITL approval)

**Inputs**:
- `customer_id` (int, required): Odoo customer ID
- `date` (string, required): ISO date
- `items` (array, required): Line items
  - `product_id` (int): Odoo product ID
  - `quantity` (float): Units
  - `price_unit` (float): Price per unit
  - `description` (string): Item description
- `due_date` (string, optional): Payment due date
- `notes` (string, optional): Internal notes

**Output**:
```json
{
  "status": "created",
  "invoice_id": 125,
  "invoice_number": "INV-2026-025",
  "customer": "New Customer Inc",
  "total": 5000.00,
  "url": "http://localhost:8069/web#id=125&model=account.move"
}
```

**HITL Integration**: Called AFTER user approval from `/Pending_Approval`

**Error Handling**:
- Customer not found (404): Return list of valid customer IDs
- Invalid product (400): Return list of valid products
- Missing fields (400): Validation error with details

### 6. get_balance

**Purpose**: Get current account balance and cash flow

**Inputs**:
- `account_type` (string, optional): "bank", "receivable", "payable", "all"
- `include_forecast` (boolean, optional): Include 30-day forecast (default: true)

**Output**:
```json
{
  "status": "success",
  "date": "2026-02-26",
  "summary": {
    "cash_on_hand": 52340.50,
    "accounts_receivable": 45230.00,
    "accounts_payable": 8500.00,
    "net_position": 89070.50
  },
  "accounts": [
    {
      "name": "Bank Account",
      "balance": 52340.50,
      "currency": "USD"
    },
    {
      "name": "Petty Cash",
      "balance": 500.00,
      "currency": "USD"
    }
  ],
  "forecast_30_days": {
    "projected_inflows": 125000.00,
    "projected_outflows": 45000.00,
    "projected_balance": 132340.50
  }
}
```

**Use Cases**:
- Check available cash
- Plan payments
- Forecast cash flow
- Monitor financial health

### 7. generate_report

**Purpose**: Generate financial report (P&L, Balance Sheet, etc.)

**Inputs**:
- `report_type` (string, required): "profit_loss", "balance_sheet", "cash_flow"
- `date_from` (string, required): ISO date
- `date_to` (string, required): ISO date
- `format` (string, optional): "json", "pdf" (default: "json")

**Output** (JSON):
```json
{
  "status": "success",
  "report_type": "profit_loss",
  "period": {
    "from": "2026-01-01",
    "to": "2026-02-26"
  },
  "data": {
    "revenue": 250000.00,
    "cost_of_goods": 125000.00,
    "gross_profit": 125000.00,
    "operating_expenses": 45000.00,
    "net_income": 80000.00
  },
  "file_url": "http://localhost:8069/download/report-2026-01-01-to-2026-02-26.pdf"
}
```

**Use Cases**:
- Monthly financial reporting
- Tax preparation
- Investor reporting
- Business analysis

## Error Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| 401 | Auth failed | Check credentials in .env |
| 404 | Resource not found | Use list tools to find valid IDs |
| 429 | Rate limited | Exponential backoff (max 5 retries) |
| 500 | Odoo server error | Retry after 60 seconds |
| 503 | Service unavailable | Retry after 120 seconds |

## Rate Limiting

- **Quota**: 1000 requests/minute (Odoo default)
- **Burst**: No burst limit
- **Strategy**: Exponential backoff on errors
- **Caching**: Cache read-only responses for 5 minutes

## Logging & Auditing

**Every call logged** in `/Logs/odoo-mcp.json`:
```json
{
  "timestamp": "2026-02-26T14:30:00Z",
  "tool": "get_revenue",
  "request": {
    "date_from": "2026-02-20",
    "date_to": "2026-02-26"
  },
  "response": {
    "total_revenue": 48500.00,
    "invoice_count": 20
  },
  "latency_ms": 245,
  "status": "success",
  "error": null
}
```

## Security

- ✅ OAuth not available (Odoo uses session tokens)
- ✅ Credentials in .env (never in code)
- ✅ HTTPS recommended (for production)
- ✅ Scoped read-mostly permissions (no mass delete)
- ✅ Audit logging 100%
- ✅ No PII in response summaries

## Deployment

```bash
# Install Odoo (if not already running)
docker run -d \
  -p 8069:8069 \
  --name odoo \
  odoo:19

# Configure .env
echo "ODOO_URL=http://localhost:8069" >> .env
echo "ODOO_DATABASE=odoo" >> .env
echo "ODOO_USERNAME=admin" >> .env
echo "ODOO_PASSWORD=<password>" >> .env

# Start odoo-mcp server
node Tier_3_Gold/src/mcp/odoo-mcp/index.js

# Verify
curl -X POST http://localhost:3002/tools/get_balance \
  -H "Content-Type: application/json" \
  -d '{"account_type":"bank"}'
```

## Configuration in Claude Code

**mcp.json**:
```json
{
  "mcpServers": {
    "odoo-mcp": {
      "command": "node",
      "args": ["./Tier_3_Gold/src/mcp/odoo-mcp/index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DATABASE": "odoo",
        "ODOO_USERNAME": "${ODOO_USERNAME}",
        "ODOO_PASSWORD": "${ODOO_PASSWORD}"
      },
      "description": "Odoo Community accounting integration for financial reports"
    }
  }
}
```

## Known Limitations

| Limitation | Workaround |
|-----------|-----------|
| No native webhooks | Use polling (CEO briefing runs nightly) |
| PDF generation slow (>5s) | Cache PDFs, generate async |
| Customization requires dev skills | Use standard Odoo modules |
| No API for chart of accounts | Query via SQL (advanced) |

---

**Created**: 2026-02-26 | **Status**: Ready for implementation | **Tier**: Gold | **Integration**: Odoo Community 19+
