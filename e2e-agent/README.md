# E2E Testing for Athens & SAP-Python

## Setup

```bash
npm install
npx playwright install --with-deps chromium
cp .env.example .env.e2e
# Edit .env.e2e with real credentials
```

## Configuration

Edit `.env.e2e` with valid test credentials:

```bash
# Athens
ATHENS_BASE_URL=https://prozeal.athenas.co.in
ATHENS_TEST_USERNAME=your_actual_username
ATHENS_TEST_PASSWORD=your_actual_password

# SAP-Python
SAP_BASE_URL=https://sap.athenas.co.in
SAP_TEST_EMAIL=your_actual_email
SAP_TEST_PASSWORD=your_actual_password
SAP_LOGIN_MODE=company  # master | company | service
```

## Run Tests

```bash
# Run all E2E tests
npm run test:all

# Run individual tests
npm run test:athens
npm run test:sap

# View HTML report
npm run report
```

## Test Coverage

- **Athens**: Login with username/password, verify token in localStorage, check dashboard title
- **SAP**: Login with email/password (supports 3 modes), verify correct dashboard URL

## Troubleshooting

```bash
# Check screenshots/videos on failure
ls test-results/

# View detailed trace
npx playwright show-trace test-results/*/trace.zip

# Inspect login forms
node inspect-login.js
```

## How It Works

- Tests run headless on VPS with Chromium
- Each test performs full login flow (no session reuse)
- Screenshots, videos, and traces captured on failure
- Retries once automatically on failure
