#!/usr/bin/env bash

set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
WEB_BASE_URL="${WEB_BASE_URL:-http://127.0.0.1:3000}"

check_status() {
  local url="$1"
  local expected="$2"
  local tmp
  tmp="$(mktemp)"

  curl -i -sS "$url" >"$tmp"

  local status
  status="$(head -n 1 "$tmp" | awk '{print $2}')"

  if [[ "$status" != "$expected" ]]; then
    echo "Expected $expected from $url but got $status" >&2
    cat "$tmp" >&2
    rm -f "$tmp"
    exit 1
  fi

  echo "OK $status $url"
  rm -f "$tmp"
}

check_body_contains() {
  local url="$1"
  local expected="$2"
  local tmp
  tmp="$(mktemp)"

  curl -i -sS "$url" >"$tmp"

  if ! grep -q "$expected" "$tmp"; then
    echo "Expected response from $url to contain: $expected" >&2
    cat "$tmp" >&2
    rm -f "$tmp"
    exit 1
  fi

  echo "OK body $url contains $expected"
  rm -f "$tmp"
}

check_redirect() {
  local url="$1"
  local expected_location="$2"
  local tmp
  tmp="$(mktemp)"

  curl -i -sS "$url" >"$tmp"

  local status
  status="$(head -n 1 "$tmp" | awk '{print $2}')"
  local location
  location="$(awk 'tolower($1) == "location:" {print $2}' "$tmp" | tr -d '\r')"

  if [[ "$status" != "307" ]]; then
    echo "Expected 307 from $url but got $status" >&2
    cat "$tmp" >&2
    rm -f "$tmp"
    exit 1
  fi

  if [[ "$location" != "$expected_location" ]]; then
    echo "Expected redirect to $expected_location from $url but got $location" >&2
    cat "$tmp" >&2
    rm -f "$tmp"
    exit 1
  fi

  echo "OK 307 $url -> $location"
  rm -f "$tmp"
}

echo "Verifying ResumeOS runtime..."
check_status "${API_BASE_URL}/health" "200"
check_status "${API_BASE_URL}/auth/google/status" "200"
check_body_contains "${API_BASE_URL}/auth/google/status" '"configured":true'
check_status "${WEB_BASE_URL}/auth" "200"
check_redirect "${WEB_BASE_URL}/app/resumes" "/auth"
check_redirect "${WEB_BASE_URL}/app/settings" "/auth"
check_redirect "${WEB_BASE_URL}/app/resumes/runtime-check" "/auth"
echo "Runtime verification passed."
