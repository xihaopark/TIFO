#!/usr/bin/env bash
set -u

tex_file="${1:-sample-sigconf.tex}"
pdf_file="${2:-}"
errors=0
warnings=0

fail() {
  printf 'ERROR: %s\n' "$1"
  errors=$((errors + 1))
}

warn() {
  printf 'WARN: %s\n' "$1"
  warnings=$((warnings + 1))
}

if [[ ! -f "$tex_file" ]]; then
  fail "TeX file not found: $tex_file"
  printf 'Preflight: %d error(s), %d warning(s)\n' "$errors" "$warnings"
  exit 1
fi

if ! rg -q -F '\documentclass[sigconf,anonymous,review]{acmart}' "$tex_file"; then
  fail 'Expected anonymous ACM review document class was not found.'
fi

if rg -n -F '\reviewhighlight{' "$tex_file" >/tmp/kdd27_reviewhighlight_hits.$$; then
  fail "Internal \\reviewhighlight markup remains ($(wc -l </tmp/kdd27_reviewhighlight_hits.$$) lines)."
fi
rm -f /tmp/kdd27_reviewhighlight_hits.$$

if rg -n '\\(textcolor\{red\}|color\{red\})' "$tex_file" >/tmp/kdd27_red_hits.$$; then
  fail "Red text commands remain ($(wc -l </tmp/kdd27_red_hits.$$) lines); inspect even if some are comments."
fi
rm -f /tmp/kdd27_red_hits.$$

if rg -n 'Table~?[[:space:]]*[XYZWV]|Table[[:space:]]+[XYZWV]' "$tex_file" >/tmp/kdd27_placeholder_hits.$$; then
  fail 'Placeholder table references such as Table X/Y/Z/W/V remain.'
fi
rm -f /tmp/kdd27_placeholder_hits.$$

if rg -n -i 'TODO|FIXME|TBD|INSERT[[:space:]]+(RESULT|VALUE|CITATION)|\?\?' "$tex_file" >/tmp/kdd27_todo_hits.$$; then
  fail 'Unresolved TODO/FIXME/TBD/placeholder markers remain.'
fi
rm -f /tmp/kdd27_todo_hits.$$

if ! rg -q 'KDD_RESUBMIT_SUMMARY|Summary of Changes|summary-of-changes' "$tex_file"; then
  warn 'No Summary of Changes marker/input was found in the TeX entrypoint.'
fi

if rg -n '\\author\{|\\affiliation\{' "$tex_file" >/tmp/kdd27_author_hits.$$; then
  warn 'Author/affiliation commands exist; verify the compiled review PDF is anonymous.'
fi
rm -f /tmp/kdd27_author_hits.$$

if [[ -n "$pdf_file" ]]; then
  if [[ ! -f "$pdf_file" ]]; then
    fail "PDF file not found: $pdf_file"
  elif command -v pdfinfo >/dev/null 2>&1; then
    pages="$(pdfinfo "$pdf_file" 2>/dev/null | awk '/^Pages:/ {print $2}')"
    if [[ -n "$pages" ]]; then
      printf 'INFO: compiled PDF has %s total page(s). Verify page 1 is the summary and pages 2-9 are self-contained content.\n' "$pages"
    else
      warn 'Could not read PDF page count.'
    fi
  else
    warn 'pdfinfo is unavailable; page count was not checked.'
  fi
fi

printf 'Preflight: %d error(s), %d warning(s)\n' "$errors" "$warnings"
if (( errors > 0 )); then
  exit 1
fi
