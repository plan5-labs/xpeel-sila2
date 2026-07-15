#!/usr/bin/env bash
#
# Grant execute permission if needed:
#   chmod +x launch.sh
#
# Usage: Place this script and app.env in the same directory, then run ./launch.sh
#
# - If app.env does not exist, print on error message and exit.
# - Mapping:
#   IP_ADDRESS  -> -a <IP_ADDRESS>        (default: 127.0.0.1 if unset)
#   PORT        -> -p <PORT>              (default: 50052 if unset)
#   SERVER_UUID -> -server-uuid <UUID>    (omit the whole option if unset)
#   ENABLE_TLS  -> If set to FALSE, add --insecure
#   CERT_FILE   -> Only when ENABLE_TLS is TRUE, add -c <CERT_FILE>
#                  (omit if unset or ENABLE_TLS is not TRUE)
#   PRIVATE_KEY -> Only when ENABLE_TLS is TRUE, add -k <PRIVATE_KEY>
#                  (omit if unset or ENABLE_TLS is not TRUE)
#

set -eu

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/app.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: app.env not found: $ENV_FILE" >&2
  exit 1
fi

source "$ENV_FILE"

# Build argument array.
args=( python -m automated_plate_seal_remover_controller )

# Append IP address if IP_ADDRESS is provided.
if [[ -n "${IP_ADDRESS:-}" ]]; then
  args+=( -a "$IP_ADDRESS" )
fi

# Append Port number if PORT is provided.
if [[ -n "${PORT:-}" ]]; then
  args+=( -p "$PORT" )
fi

# Append UUID if SERVER_UUID is provided.
if [[ -n "${SERVER_UUID:-}" ]]; then
  args+=( --server-uuid "$SERVER_UUID" )
fi

# Append insecure option if ENABLE_TLS is FALSE.
if [[ "${ENABLE_TLS:-}" == "FALSE" ]]; then
  args+=( --insecure )
fi

# Append certification file if ENABLE_TLS is TRUE and CERT_FILE is provided.
if [[ "${ENABLE_TLS:-}" == "TRUE" && -n "${CERT_FILE:-}" ]]; then
  args+=( -c "$CERT_FILE" )
fi

# Append certification file if ENABLE_TLS is TRUE and PRIVATE_KEY is provided.
if [[ "${ENABLE_TLS:-}" == "TRUE" && -n "${PRIVATE_KEY:-}" ]]; then
  args+=( -k "$PRIVATE_KEY" )
fi

# Execute
exec "${args[@]}"
