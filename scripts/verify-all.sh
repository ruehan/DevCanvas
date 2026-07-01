#!/usr/bin/env bash
# 모노레포 전체 검증 — api/ 와 web/ 각각에서 verify.sh 실행.
# 사용법: bash scripts/verify-all.sh
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

VERIFY="${VERIFY_SCRIPT:-$HOME/.config/opencode/scripts/verify.sh}"
FAIL=0

for proj in api web; do
  if [ -d "$proj" ]; then
    printf '\n==== %s ====\n' "$proj"
    bash "$VERIFY" "$proj" || FAIL=1
  fi
done

if [ "$FAIL" -ne 0 ]; then
  printf '\n❌ 일부 프로젝트 검증 실패\n' >&2
  exit 1
fi
printf '\n✅ 모든 프로젝트 검증 통과\n'
