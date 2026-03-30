# Section 3 Task Checklist

## Scope

Add snapshots and recovery so the working draft can be saved as named versions and restored safely.

## Out of Scope

- polished side-by-side snapshot diff UI
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
- [x] add debounced autosave for the working draft
- [x] ensure snapshot creation waits for the latest persisted draft
- [x] add restore confirmation before overwriting the working draft
- [x] add clearer success feedback for snapshot create and restore
- [x] add minimal snapshot compare action against the current working draft
- [x] fetch snapshot source lazily instead of bloating the snapshot list payload
- [x] render a simple line-based diff for snapshot vs current draft

## Verification Checklist

- [x] snapshot can be created from the current working draft
- [x] snapshot list returns saved snapshots in expected order
- [x] restoring a snapshot updates the working draft
- [x] restoring a snapshot does not delete the snapshot itself
- [x] backend snapshot tests pass
- [x] frontend production build passes
- [x] snapshot compare can load a selected snapshot
- [x] snapshot compare shows added/removed/unchanged lines against the current draft

## Notes

- keep the snapshot implementation minimal and safe
- keep compare intentionally lightweight for now; the goal is clarity, not a full git-style diff product
- autosave belongs to the editor-state workflow and should remove the need to manually save before snapshot creation
- restore is the first destructive editor action, so clarity and confirmation matter more than extra version-history UI right now
