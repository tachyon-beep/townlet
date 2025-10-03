import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 50,
  duration: "1m",
  thresholds: {
    websocket_response_time: ["p(95)<250"],
    http_req_failed: ["rate<0.01"]
  }
};

export default function () {
  const res = http.get(__ENV.SPECTATOR_URL ?? "http://localhost:8080/");
  check(res, {
    "status is 200": (r) => r.status === 200
  });
  sleep(1);
}
