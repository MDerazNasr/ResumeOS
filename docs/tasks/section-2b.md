# Section 2B Task Checklist

## Scope

Build real LaTeX compile execution and a real PDF preview path on top of the Section 2A compile contract.

## Out of Scope

- Monaco integration
- AI editing
- patch engine
- snapshots
- vector retrieval

## Implementation Checklist

- [x] inspect local TeX commands available on this machine
- [x] choose the initial compile command and execution strategy
- [x] implement backend subprocess compile service
- [x] write source into a temp compile directory
- [x] run TeX with timeout and log capture
- [x] detect successful PDF output
- [x] persist compile run result with artifact path
- [x] expose a route to fetch the latest compiled PDF
- [x] update frontend compile panel to load the real PDF
- [x] render real compile errors from backend logs

## Verification Checklist

- [x] starter resume compiles successfully
- [x] latest PDF can be fetched from the backend
- [x] preview pane updates after successful compile
- [x] intentionally broken LaTeX returns failure logs
- [x] compile conflict still returns `409`
- [x] frontend production build passes

## Notes

- keep the existing compile API contract stable unless a change is clearly necessary
- prefer the smallest real compile path that works locally before hardening for production containerization
- Monaco integration remains the main remaining Section 2 editor item
