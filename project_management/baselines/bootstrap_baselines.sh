#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
third_party="${repo_root}/third_party"
mkdir -p "${third_party}"

checkout_repo() {
  local name="$1"
  local url="$2"
  local revision="$3"
  local target="${third_party}/${name}"

  if [[ ! -d "${target}/.git" ]]; then
    git clone "${url}" "${target}"
  fi

  git -C "${target}" fetch --tags origin
  git -C "${target}" checkout --detach "${revision}"
  test "$(git -C "${target}" rev-parse HEAD)" = "${revision}"
  printf '%s\t%s\n' "${name}" "${revision}"
}

checkout_repo \
  "Time-Series-Library" \
  "https://github.com/thuml/Time-Series-Library.git" \
  "4e938a1767106324dd753b2a44832bf870a0252e"

checkout_repo \
  "FAN-official" \
  "https://github.com/icannotnamemyself/FAN.git" \
  "838e1b002aa0e8cbc3889dfb69967c40c0c15761"

checkout_repo \
  "FilterNet-official" \
  "https://github.com/aikunyi/FilterNet.git" \
  "cdb321c4e338e0c07b45cee92f54b3c5bd5a809e"

checkout_repo \
  "DDN-official" \
  "https://github.com/Hank0626/DDN.git" \
  "72b8d9c595ca81e70500919689f8715ed133e6d2"

checkout_repo \
  "PIR-official" \
  "https://github.com/icantnamemyself/PIR.git" \
  "fc372bb02090da887d4a20b614a6cfecbfd813d0"

checkout_repo \
  "TimeEmb-official" \
  "https://github.com/showmeon/TimeEmb.git" \
  "9adf3fba801b34642e7191b45e08aff224b26e67"

checkout_repo \
  "TFPS-official" \
  "https://github.com/syrGitHub/TFPS.git" \
  "83a11827e27e6617e8c8a8771f0a1dd7e10976a5"
