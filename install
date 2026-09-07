#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# AuraPACS installer.
#
# This file is PUBLIC. Put it on the website, hand it to anyone, print it in a
# brochure. It contains no keys, no credentials and no application code, and
# there is nothing in it worth stealing.
#
# What it does:
#   1. works out a stable fingerprint for this machine (the Site ID)
#   2. asks for the activation code the customer got from Elevate Aura
#   3. exchanges code + Site ID for a signed licence and a short-lived
#      download token
#   4. pulls the encrypted application bundle and installs it
#
# The activation code is inert until Elevate Aura has confirmed payment, so a
# prospect can get this far on their own hardware before any money moves and
# still cannot run the software.
#
#   curl -fsSL https://elevateaura.co.in/install | sudo bash
# ============================================================================

LICENSE_SERVER="${LICENSE_SERVER_URL:-https://license.elevateaura.co.in}"
INSTALL_DIR="${INSTALL_DIR:-/opt/aurapacs}"
DATA_DIR_DEFAULT="${DATA_DIR:-/data}"

bold()  { printf '\033[1m%s\033[0m\n' "$*"; }
warn()  { printf '\033[33m%s\033[0m\n' "$*" >&2; }
die()   { printf '\033[31m%s\033[0m\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "Run this with sudo: curl -fsSL .../install | sudo bash"

echo
bold "================ AuraPACS installer ================"
echo

# ---------------------------------------------------------------------------
# Site ID
#
# Derived from /etc/machine-id, which is written when the operating system is
# installed and survives reboots and upgrades. The same value is computed
# independently inside the licensing container from the same file, so the
# licence can be checked against the machine on every start rather than only
# once at activation.
#
# This must produce a byte-identical result to modules/licensing/siteid.py.
# Both sides are blake2s-64 over the namespace plus the machine-id, rendered
# in the same 26-symbol alphabet, least significant symbol first.
# ---------------------------------------------------------------------------
MACHINE_ID=""
for f in /etc/machine-id /var/lib/dbus/machine-id; do
  if [ -r "$f" ]; then MACHINE_ID="$(tr -d '[:space:]' < "$f")"; [ -n "$MACHINE_ID" ] && break; fi
done
[ -n "$MACHINE_ID" ] || die "Cannot read /etc/machine-id. This machine has no stable identity; contact Elevate Aura."

command -v python3 >/dev/null 2>&1 || { echo "==> Installing python3 ..."; (apt-get update -qq && apt-get install -y -qq python3) >/dev/null 2>&1 || die "python3 is required."; }

SITE_ID="$(MID="$MACHINE_ID" python3 - <<'PY'
import hashlib, os
mid = os.environ["MID"]
d = hashlib.blake2s(b"aurapacs.site.v1" + mid.encode(), digest_size=8).digest()
a = "234679ACDEFGHJKMNPQRTUVWXY"
n = int.from_bytes(d, "big"); out = []
for _ in range(8):
    n, r = divmod(n, len(a)); out.append(a[r])
print("AURA-SITE-" + "".join(out))
PY
)"

echo "  This machine's Site ID:  $(bold "$SITE_ID")"
echo
echo "  Give this Site ID to Elevate Aura along with your payment reference."
echo "  They will confirm the payment and read you an activation code."
echo

# ---------------------------------------------------------------------------
# Activation
# ---------------------------------------------------------------------------
ACTIVATION_CODE="${AURAPACS_ACTIVATION_CODE:-}"
if [ -z "$ACTIVATION_CODE" ]; then
  if [ -t 0 ]; then
    read -rp "Activation code (AURA-XXXX-XXXX-XXXX): " ACTIVATION_CODE
  else
    # Piped from curl, so stdin is the script. Read from the terminal instead.
    read -rp "Activation code (AURA-XXXX-XXXX-XXXX): " ACTIVATION_CODE < /dev/tty
  fi
fi
[ -n "$ACTIVATION_CODE" ] || die "An activation code is required."

read -rp "Storage folder for scans [$DATA_DIR_DEFAULT]: " IN < /dev/tty || IN=""
DATA_DIR="${IN:-$DATA_DIR_DEFAULT}"

# The names staff will actually type into a browser. The control plane cannot
# guess a LAN address, so the certificate it issues is only correct if these
# are sent with the activation request.
LAN_IPS="$(hostname -I 2>/dev/null || true)"
LAN_HOST="$(hostname 2>/dev/null || echo aurapacs)"
echo "  This server answers on: ${LAN_IPS:-unknown}"
read -rp "Hostname staff will use in the browser [${LAN_HOST}.local]: " IN < /dev/tty || IN=""
LAN_NAME="${IN:-${LAN_HOST}.local}"

echo
echo "==> Activating with $LICENSE_SERVER ..."
REQ=$(ACT="$ACTIVATION_CODE" SID="$SITE_ID" HN="$LAN_HOST" NAME="$LAN_NAME" IPS="$LAN_IPS" python3 -c '
import json, os
ips = [i for i in os.environ.get("IPS","").split() if i and not i.startswith("127.")]
names = [n for n in {os.environ["NAME"], os.environ["HN"]} if n]
print(json.dumps({"activation_code": os.environ["ACT"], "site_id": os.environ["SID"],
                  "hostname": os.environ["HN"], "version": "installer-1",
                  "lan_hostnames": names, "lan_ips": ips}))')

HTTP_BODY=$(mktemp); trap 'rm -f "$HTTP_BODY"' EXIT
CODE=$(curl -sS -o "$HTTP_BODY" -w '%{http_code}' -X POST "$LICENSE_SERVER/activate" \
        -H "Content-Type: application/json" -d "$REQ" || echo "000")

if [ "$CODE" != "200" ]; then
  # The server's message is written for the customer, so show it as-is rather
  # than a generic failure. It distinguishes "not paid yet" from "wrong code"
  # from "already in use elsewhere", and each needs a different phone call.
  MSG=$(python3 -c '
import json,sys
try: print(json.load(open(sys.argv[1])).get("detail","")) 
except Exception: print("")' "$HTTP_BODY" 2>/dev/null || true)
  echo
  case "$CODE" in
    000) die "Could not reach $LICENSE_SERVER. Check this machine has internet access." ;;
    429) die "Too many attempts. Wait five minutes and try again." ;;
    *)   die "Activation failed. ${MSG:-The server rejected this activation code.}" ;;
  esac
fi

pyget(){ python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))'"$1"')' "$HTTP_BODY"; }
CLIENT=$(pyget '["client_id"]')
CUSTOMER=$(pyget '.get("customer","")')
CENTRE=$(pyget '.get("centre","")')
DLTOK=$(pyget '["download_token"]')
PROFILE=$(pyget '.get("profile","clinic")')
SEATS=$(pyget '.get("seats",5)')

echo "    Activated."
echo "      Customer : $CUSTOMER"
echo "      Centre   : $CENTRE"
echo "      Seats    : $SEATS"
echo

command -v docker >/dev/null 2>&1 || { echo "==> Installing Docker ..."; curl -fsSL https://get.docker.com | sh; }

echo "==> Downloading the application ..."
mkdir -p "$INSTALL_DIR"
curl -fsS "$LICENSE_SERVER/download?token=$DLTOK" -o "$INSTALL_DIR/aurapacs.tar.gz" \
  || die "Download failed. The download link is valid for a few minutes only; re-run this installer."
tar xzf "$INSTALL_DIR/aurapacs.tar.gz" -C "$INSTALL_DIR" --strip-components=1
rm -f "$INSTALL_DIR/aurapacs.tar.gz"

# The licence and the public key that verifies it. The licence is written
# 0600: it is not a secret in the cryptographic sense, since it is signed and
# machine-bound, but there is no reason for every user on the box to read the
# customer's commercial terms.
mkdir -p "$INSTALL_DIR/secrets" "$DATA_DIR"
python3 -c '
import json,sys
d=json.load(open(sys.argv[1]))
open(sys.argv[2],"w").write(d["license_token"])
open(sys.argv[3],"w").write(d["public_key_pem"])
' "$HTTP_BODY" "$INSTALL_DIR/secrets/license.token" "$INSTALL_DIR/secrets/public.pem"
chmod 600 "$INSTALL_DIR/secrets/license.token"
chmod 644 "$INSTALL_DIR/secrets/public.pem"

# ---------------------------------------------------------------------------
# Certificate for a site that will have no internet after today.
#
# Issued once, at activation, because this is the only moment the clinic and
# the control plane are connected. Ten years, so nothing ever expires in a
# server room nobody visits. The authority is installed here and printed for
# the workstations, because a certificate nobody trusts produces exactly the
# browser warning it was meant to remove.
# ---------------------------------------------------------------------------
HAS_TLS=$(python3 -c '
import json,sys
d=json.load(open(sys.argv[1])); print("yes" if d.get("tls") else "no")' "$HTTP_BODY")

# Does this machine actually have a route out, right now? Asked rather than
# assumed, because "it is on the LAN" says nothing about it: plenty of clinic
# server rooms are wired to a switch that reaches the scanners and nothing
# else. This decides only whether we ALSO chase a publicly trusted
# certificate. The site certificate above is installed either way, so a wrong
# answer here degrades to one extra trust step, never to an outage.
if curl -fsS --max-time 8 -o /dev/null "$LICENSE_SERVER/health" 2>/dev/null; then
  SITE_ONLINE=yes
else
  SITE_ONLINE=no
fi

if [ "$HAS_TLS" = "yes" ]; then
  echo "==> Installing the site certificate ..."
  mkdir -p "$INSTALL_DIR/certs"
  python3 -c '
import json,sys
d=json.load(open(sys.argv[1]))["tls"]
open(sys.argv[2],"w").write(d["ca_pem"])
open(sys.argv[3],"w").write(d["cert_pem"])
open(sys.argv[4],"w").write(d["key_pem"])
print(" ".join(d.get("names",[])))
' "$HTTP_BODY" "$INSTALL_DIR/certs/site-ca.pem" "$INSTALL_DIR/certs/site.crt" "$INSTALL_DIR/certs/site.key" > /tmp/aura_names
  chmod 600 "$INSTALL_DIR/certs/site.key"
  chmod 644 "$INSTALL_DIR/certs/site.crt" "$INSTALL_DIR/certs/site-ca.pem"

  # Trust it on the server itself, so anything running locally stops
  # complaining. Debian and RHEL keep these in different places.
  if [ -d /usr/local/share/ca-certificates ]; then
    cp "$INSTALL_DIR/certs/site-ca.pem" /usr/local/share/ca-certificates/aurapacs-site-ca.crt
    update-ca-certificates >/dev/null 2>&1 || warn "  could not update the system trust store"
  elif [ -d /etc/pki/ca-trust/source/anchors ]; then
    cp "$INSTALL_DIR/certs/site-ca.pem" /etc/pki/ca-trust/source/anchors/aurapacs-site-ca.pem
    update-ca-trust extract >/dev/null 2>&1 || warn "  could not update the system trust store"
  fi

  # Caddy serves the issued certificate instead of trying to reach the
  # internet for one. auto_https off is essential: left on, Caddy would sit
  # there retrying ACME forever on a machine with no route out.
  if [ -f "$INSTALL_DIR/prod/Caddyfile.lan" ]; then
    cp "$INSTALL_DIR/prod/Caddyfile.lan" "$INSTALL_DIR/prod/Caddyfile"
  fi

  {
    echo "AURAPACS_TLS=site"
    echo "SITE_CERT_DIR=$INSTALL_DIR/certs"
    # The agent replaces the site certificate with a publicly trusted one when
    # it can, and leaves it strictly alone when it cannot. Off entirely at a
    # site with no route out, so it is not retrying forever in the logs.
    echo "CERT_AGENT_ENABLED=$SITE_ONLINE"
  } >> "$INSTALL_DIR/.env"
fi

if [ ! -f "$INSTALL_DIR/.env" ]; then
  cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env" 2>/dev/null || true
  {
    echo "CLIENT_ID=$CLIENT"
    echo "AURAPACS_PROFILE=$PROFILE"
    echo "DATA_DIR=$DATA_DIR"
    echo "LICENSE_SERVER_URL=$LICENSE_SERVER"
  } >> "$INSTALL_DIR/.env"
  # Generated here rather than shipped, so no two installations share a secret.
  for v in DB_PASSWORD SESSION_SECRET; do
    grep -q "^$v=" "$INSTALL_DIR/.env" && sed -i "/^$v=/d" "$INSTALL_DIR/.env"
    echo "$v=$(head -c 32 /dev/urandom | base64 | tr -d '=+/' | cut -c1-40)" >> "$INSTALL_DIR/.env"
  done
  chmod 600 "$INSTALL_DIR/.env"
fi

echo "==> Starting AuraPACS ..."
cd "$INSTALL_DIR"
docker compose up -d

echo
bold "================ AuraPACS is running ================"
if [ "$HAS_TLS" = "yes" ]; then
  echo "  Dashboard : https://${LAN_NAME}"
  echo "  Valid for : $(cat /tmp/aura_names 2>/dev/null)"
else
  echo "  Dashboard : http://$(hostname -I 2>/dev/null | awk '{print $1}'):3001"
fi
echo "  Site ID   : $SITE_ID"
echo "  Data      : $DATA_DIR"
echo
echo "  Open the dashboard and create your administrator account."
echo

if [ "$HAS_TLS" = "yes" ]; then
  if [ "$SITE_ONLINE" = "yes" ]; then
    echo "  This server can reach the internet, so it will also fetch a"
    echo "  publicly trusted certificate. Until that arrives, and any time it"
    echo "  cannot be renewed, the site certificate below is used instead, so"
    echo "  the system keeps working either way."
    echo
  else
    echo "  This server has no route to the internet. It does not need one."
    echo "  Its certificate is valid for ten years and renews nothing."
    echo
  fi
  bold "  ONE STEP ON EACH WORKSTATION"
  echo "  Copy this file to every PC that will open AuraPACS:"
  echo "      $INSTALL_DIR/certs/site-ca.pem"
  echo
  echo "  Windows:  double-click it, Install Certificate, Local Machine,"
  echo "            Place all certificates in: Trusted Root Certification Authorities"
  echo "  Then restart the browser on that PC."
  echo
  echo "  Do this even if the server has internet today. It is what keeps the"
  echo "  system working on the day it does not."
  echo
fi
echo "  Support: Elevate Aura, Chennai."
echo
