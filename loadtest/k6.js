// Load test for the RealTime RecSys API (requires the Day 3 endpoints: POST /events, GET /recommendations).
//
// Each virtual user (VU) is one shopping session: it sends an event, asks for
// recommendations and "thinks" for 1 second. ~1,000 VUs -> ~2,000 requests/s.
//
//   Smoke test against the local API (uvicorn on your machine):
//     docker compose --profile loadtest run --rm k6
//   Full load profile against AWS (Day 8):
//     docker compose --profile loadtest run --rm -e PROFILE=load -e BASE_URL=https://<api-id>.execute-api.us-east-1.amazonaws.com k6
//   With k6 installed locally:
//     k6 run -e BASE_URL=http://localhost:8000 loadtest/k6.js

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = (__ENV.BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
const PROFILE = __ENV.PROFILE || 'smoke';

// Replace with ids from your artifacts/popular.json. Unknown ids still work:
// the API falls back to popular products.
const PRODUCT_IDS = [1004856, 1005115, 1004767, 1005160, 1002544, 1003461];
const EVENT_TYPES = ['view', 'view', 'view', 'view', 'cart', 'purchase']; // views dominate real traffic

const PROFILES = {
  smoke: [{ duration: '30s', target: 5 }],
  load: [
    { duration: '5m', target: 1000 }, // ramp-up
    { duration: '10m', target: 1000 }, // sustained
    { duration: '1m', target: 0 }, // ramp-down
  ],
};

if (!PROFILES[PROFILE]) {
  throw new Error(`Unknown PROFILE "${PROFILE}". Use one of: ${Object.keys(PROFILES).join(', ')}`);
}

export const options = {
  stages: PROFILES[PROFILE],
  thresholds: {
    http_req_failed: ['rate<0.001'], // error rate < 0.1%
    'http_req_duration{endpoint:recommendations}': ['p(95)<150', 'p(99)<200'],
  },
};

const pick = (items) => items[Math.floor(Math.random() * items.length)];

export default function () {
  const sessionId = `vu-${__VU}`;

  const event = { session_id: sessionId, product_id: pick(PRODUCT_IDS), event_type: pick(EVENT_TYPES) };
  const eventResponse = http.post(`${BASE_URL}/events`, JSON.stringify(event), {
    headers: { 'Content-Type': 'application/json' },
    tags: { endpoint: 'events' },
  });
  check(eventResponse, { 'event accepted (202)': (r) => r.status === 202 });

  const recommendationsResponse = http.get(`${BASE_URL}/recommendations?session_id=${sessionId}&k=10`, {
    tags: { endpoint: 'recommendations' },
  });
  check(recommendationsResponse, { 'recommendations ok (200)': (r) => r.status === 200 });

  sleep(1); // think time between user actions
}
