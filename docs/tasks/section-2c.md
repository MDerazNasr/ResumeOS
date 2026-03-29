# Section 2C Task Checklist

## Scope

Close out Section 2 by replacing the temporary textarea editor with Monaco and adding checked-in backend tests for the compile workflow.

## Out of Scope

- AI editing
- patch engine
- snapshots
- document protection model

## Implementation Checklist

- [x] add Monaco editor dependency to the web app
- [x] replace the textarea editor with a Monaco-based editor component
- [x] preserve current save and compile behavior
- [x] preserve the compile panel and PDF preview behavior
- [x] add backend test files for compile success, failure, and conflict
- [x] add a simple command to run the backend tests

## Verification Checklist

- [x] Monaco integration builds successfully
- [x] compile success test passes
- [x] compile failure test passes
- [x] compile conflict test passes
- [x] frontend production build passes

## Notes

- this slice is intended to close out Section 2
- once this is done, the next major step should move to snapshots or the protected document model rather than AI
