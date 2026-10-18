# Leonardus repository instructions

- Keep the accepted Regular 1.100, the preserved Regular 1.000 checkpoint, later versioned candidates, engineering demos and historical evidence distinct. Inspect README.md for the current candidate and selection.
- Record folio-level provenance in data/glyph_evidence.csv; retain uncertain readings.
- Never describe designed completions as authenticated historical handwriting or a signature.
- Do not copy museum images, restricted documents, conversation identifiers or personal paths.
- Keep original font outlines under OFL 1.1 and code/documentation under MIT.
- Use neutral project wording in documentation and keep approval quotes and dates accurate.
- SVG inputs: 1000x1000, baseline y=800, closed filled contours without strokes.
- Preserve source manifests and explicit human approval gates; document any permitted future design changes.
- For changes run pytest, the privacy and inventory checks, build-release, audit, charset and proof rendering.
- Generate specimens from the font through the provided scripts; inspect metadata before committing them.
- Keep local experiments and scan reports in ignored build/. Do not edit the separate research archive.
- Update inventory hashes with python examples/inventory.py after intentional changes.
- No automatic release, visibility change or publishing workflow: review precedes public distribution.
