# Input verification — bounded independent audit

The repo-defined unsolved input is reproduced exactly: **12,956 runes**, SHA-256 `023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585` (ASCII decimal indices joined with commas). This verifies identity of a particular rune-only transcription, **not complete puzzle input or image-level correctness**.

`dataset.json` and `page-map.json` are frozen **parallel-01-inputs-v1**. They contain all 58 original filename entries, 57 nonempty transcription segments, 604 slash-delimited source lines, zero-based offsets and source-character positions. Total including solved pages is 13,136 runes. Slash-lines preserve the supplied transcription; they are not independently certified image line breaks. Headings encoded as runes stay in the stream. Original images retain all other material; detailed spatial inventory is limited to the targeted six pages. Uninspected images are not claimed fully mapped by region.

The mapping transition is supported by actual images: p49 → segment49 (66 runes; offset12048), p50 → no rune segment (offset12114), p51 → segment50 (92 runes; offset12114), p55 → segment54 (76; offset12880), p56 → segment55 (85; offset12956), p57 → segment56 (95; offset13041). Other page joins retain the inherited R19 mapping and are provisional at image level. See `visual-records.json` for source coordinates and scope.

**The inherited description of p50 as near-blank is materially misleading.** It has **13 rows of alphanumeric pairs**, plus botanical ornament. p49 mixes three rune rows and ten alphanumeric rows; p51 mixes nine alphanumeric rows and four rune rows. Exclusion by a rune-only parser must not be read as absence of useful text. The R19 component label does not by itself identify a rune. No new cipher experiment was run.

## What was independently checked

- `parse_inputs.py` uses only Python standard library and a literal 29-rune alphabet; no inherited parsing or mapping imports. Its three hand-checkable tests check symbol order, character positions, page/line boundaries, and mutation detection. A separately retrieved [relikd README table](https://raw.githubusercontent.com/relikd/LiberPrayground/master/README.md) agrees at all29 positions. This is a separate community source, not independent glyph ground truth. The parser author had read the inherited implementation; independence is implementation-level, not blinding.
- `check_inputs.py` compares entire local transcription arrays: krisyotam = relikd = rtkd LP2 suffix, **13,136/13,136** each. The uniquely matching rtkd start follows 2,797 LP1 runes. Full source hashes are in `checks.json`.
- Fresh Internet Archive `files.xml`, with URL/date/hash in `sources/retrieval.json`, matches actual image bytes for **58/58** pages (SHA1). p0–55 use existing local relikd images. Solved p56/57 were obtained from documenting-cicada3301 `73.jpg`/`74.jpg`; their bytes match archive names56.jpg/57.jpg. This supports byte identity relative to the archive manifest, not attribution, signature authenticity or absence of steganography. Frozen v1 page-map retains null local-image references for56/57 because those images arrived later; `checks.json` and `visual-records.json` provide the supplement without changing downstream data.
- Direct viewing covered p49–51,55–57, with high-resolution rune crops for49,51,55–57. Short prefixes match the assigned segments. Checks include AE/A branch shape on p55 rune1, p56 illuminated rune0, and p57 rune1. These are selected, unblinded spot checks, not a measured accuracy gate. Images/crops and coordinates are retained. No reading was selected through English plausibility.

A further suspicious-site check requested by worker B inspected **p57 rune80** (global13121): the image clearly has **Y (index26)**, with a sloping outer top and an internal upright, rather than E. This supports canonical against the reported local scream314 E variant. See `crops/p57-site80-detail.jpg` and the exact source rectangle in `visual-records.json`.

## Ancestry and limits

The actual agreement between three local sources is reproduced. It cannot establish independent witnesses. The newly fetched relikd README explicitly describes copying followed by checking and adding separators. The repository's `analysis/transcription/TRANSCRIPTION-VERDICT.md` states that krisyotam credits iddqd and all lineages share the 2017 root. This audit did **not** reconstruct the complete historical Git/PR ancestry; the attempted rtkd README URL returned404. Thus shared ancestry remains well-motivated reported provenance, not a newly proven universal genealogy. No assertion that every possible community transcript shares one ancestor is made here.

C-001: independently supported for the defined rune stream. C-002: targeted map transition supported; narrow the description of p50. C-003: complete array agreement independently supported; image correctness and universal source ancestry not established. C-004: targeted shape checks only; inherited180/180 and450/450 not rerun. C-005: not tested; single-indel confidence ceiling cannot be certified by this work. C-006: separators retained in parser, but inherited19-line adjudication and24 residual lines not rerun. C-007: independently supported against freshly retrieved archive manifest for58/58 actual files.

## Reproduction

From repository root, with Python3.12 virtual environment:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python audit/parallel-01/inputs/parse_inputs.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python audit/parallel-01/inputs/check_inputs.py
```

`parse-output.txt`, `check-output.txt`, `acquire-output.txt` retain raw outputs. Both checks exited0; there were no timed-out execution commands or CPU-heavy jobs. Acquisition recorded one HTTP404 without aborting unrelated work. No inherited files, caches, thresholds or Git state were modified. Commands and version hashes are in `execution.json`. Crops are inspection aids and retain the original source identity in the records; they are not alternative evidence sources.
