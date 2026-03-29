# Section 3 Task Checklist

## Scope

Add snapshots and recovery so the working draft can be saved as named versions and restored safely.

## Out of Scope

- side-by-side snapshot diff UI
- AI integration
- automatic pre-tailor snapshot behavior
- job application linkage

## Implementation Checklist

- [x] add snapshot schema
- [x] add backend DTOs for snapshots
- [x] add backend routes to create, list, and restore snapshots
- [x] ensure working draft remains separate from snapshot records
- [x] add frontend snapshot panel to create and list snapshots
- [x] add restore action from snapshot to current working draft
- [x] add backend tests for snapshot creation and restore

## Verification Checklist

- [x] snapshot can be created from the current working draft
- [x] snapshot list returns saved snapshots in expected order
- [x] restoring a snapshot updates the working draft
- [x] restoring a snapshot does not delete the snapshot itself
- [x] backend snapshot tests pass
- [x] frontend production build passes

## Notes

- keep the snapshot implementation minimal and safe
- do not start compare/diff UI until the base snapshot flow is solid
