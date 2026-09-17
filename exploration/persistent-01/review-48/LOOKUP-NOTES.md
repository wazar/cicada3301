Read-only lookup failures retained:
1. `rg ... corpus/A-primary-artifacts/README* ...` failed before execution: zsh no matches found for the README glob (exit1).
2. Initial broad `rg` on corpus JSON/Markdown returned excessive metadata; output was truncated. Follow-up used exact manifest objects and narrow known-control references. No image was opened by this text search.
3. Source lookup requested src/jpeg.c, which does not exist (rg exit2); actual file is src/jpg.c. Existing src/outguess.c matches also produced truncated output. Follow-up used exact line ranges.
These are navigation/output errors, not successful scientific checks. All subsequent scientific jobs were logged separately.
