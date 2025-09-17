#!/usr/bin/env bash
set -euo pipefail

ALB_DNS="${1:-}"
DURATION="${2:-60}" # default 60 seconds
COOKIE_FILE="cookies.txt"

if [[ -z "$ALB_DNS" ]]; then
  echo "Usage: $0 <ALB_DNS> [DURATION_SECONDS]"
  exit 1
fi

echo "Testing sticky sessions for $DURATION seconds against ALB at $ALB_DNS"

# initial request to obtain cookie
curl -c "$COOKIE_FILE" -s "http://$ALB_DNS/" > /dev/null || true

START_TS=$(date +%s)

while true; do
  NOW_TS=$(date +%s)
  ELAPSED=$(( NOW_TS - START_TS ))

  # if we've reached or passed the desired duration, break
  if (( ELAPSED >= DURATION )); then
    echo "==> Reached ${DURATION} seconds (elapsed=${ELAPSED}s)."
    break
  fi

  # Print elapsed/target time and make request with cookie
  printf "[elapsed %02ds / %02ds] " "$ELAPSED" "$DURATION"
  curl -b "$COOKIE_FILE" -s "http://$ALB_DNS/sticky" || true
done

# send 20 extra requests right after duration reached to demonstrate that after the cookie expires, the sticky session is lost
echo "Sending 20 additional requests..."
for ((j=1; j<=20; j++)); do
  printf "[extra %02d/20] " "$j"
  curl -b "$COOKIE_FILE" -s "http://$ALB_DNS/sticky" || true
done

rm -f "$COOKIE_FILE"
