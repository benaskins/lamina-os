# GitHub Workflow Guide for Lamina OS

## Merge Strategy Recommendations

### Current Issue
When using GitHub's "Rebase and merge" strategy through the web UI, commits get new SHAs, causing local branches to diverge from remote. This creates the "divergent branches" message you're seeing.

### Recommended Approaches

#### Option 1: Use Squash and Merge (Recommended for feature branches)
- Maintains clean linear history
- Single commit per feature
- No local/remote divergence issues
- Perfect for Luthier's crafted PRs

#### Option 2: CLI-based Workflow
```bash
# After PR approval, merge locally
git checkout main
git pull origin main
git merge --no-ff luthier/feature-branch
git push origin main

# Or for rebase:
git checkout main
git pull origin main
git rebase luthier/feature-branch
git push origin main
```

#### Option 3: Regular Merge (via GitHub)
- Creates merge commits
- Preserves all commit history
- No divergence issues
- Less clean history

### Recommended Workflow for Luthier PRs

1. **Create PR via CLI**:
```bash
# As Luthier
gh pr create --title "feat: ..." --body "..."
```

2. **Review on GitHub**:
- You review and approve
- Add comments as needed

3. **Merge via CLI** (to avoid divergence):
```bash
# After approval
gh pr merge [PR-NUMBER] --squash --delete-branch
```

Or configure the repo to prefer squash merges:
```bash
gh repo edit --default-branch-merge-commit=false --default-branch-squash-merge=true
```

### Quick Fix for Current Situation
```bash
# When you see divergence after a rebase merge
git fetch origin
git reset --hard origin/main
```

### Best Practice Going Forward

For Luthier's PRs, I recommend:
1. **Squash and merge** through GitHub UI (cleanest)
2. Or **merge via CLI** with gh pr merge (most control)
3. Always `git pull --rebase` after merging to avoid divergence

This maintains clean history while avoiding the divergence issues you're experiencing.