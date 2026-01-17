# xlsx Audit Risk

Summary:
- npm audit reports 1 high severity vulnerability in xlsx (SheetJS).
- No fix is currently available per npm audit.

Details:
- Prototype Pollution in SheetJS (GHSA-4r6h-8v6p-xvw6)
- ReDoS in SheetJS (GHSA-5pgg-2g8v-p4x9)

Current status:
- npm audit fix (with --legacy-peer-deps) cannot resolve xlsx because there is no upstream fix.

Operational guidance:
- Track upstream release notes for SheetJS/xlsx.
- If security posture requires mitigation, consider replacing xlsx usage or isolating inputs.
