#!/usr/bin/env bash
set -euo pipefail
study_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cooja_contiki_dir="${CONTIKI_DIR:-$(dirname "$study_dir")/../../contiki-ng}"
if ! test -f "$cooja_contiki_dir/Makefile.include"; then
  git clone --depth 1 --branch release/v4.9 https://github.com/contiki-ng/contiki-ng.git "$cooja_contiki_dir"
fi
cooja_contiki_dir="$(cd "$cooja_contiki_dir" && pwd)"
git -C "$cooja_contiki_dir" submodule update --init --depth 1 tools/cooja
(cd "$cooja_contiki_dir/tools/cooja" && ./gradlew --no-daemon build)
python3 "$study_dir/run_suite.py" --contiki "$cooja_contiki_dir" --output "${COOJA_OUTPUT:-$PWD/cooja-output}" --profile "${1:-smoke}"
