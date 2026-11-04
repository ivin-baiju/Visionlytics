/**
 * k6 load test for Visionlytics API & ML inference endpoints.
 * Run with: k6 run scripts/load-test.k6.js
 */
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 10,
  duration: "20s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<250"],
  },
};

const BASE_URL = __ENV.API_URL || "http://127.0.0.1:4000";

export default function () {
  const healthRes = http.get(`${BASE_URL}/healthz`);
  check(healthRes, {
    "healthz status 200": (r) => r.status === 200,
  });

  const readyRes = http.get(`${BASE_URL}/readyz`);
  check(readyRes, {
    "readyz status 200": (r) => r.status === 200,
  });

  const benchRes = http.get(`${BASE_URL}/v1/ml/benchmarks`);
  check(benchRes, {
    "benchmarks status 200": (r) => r.status === 200,
  });

  sleep(0.2);
}
