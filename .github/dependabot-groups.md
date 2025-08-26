# Dependabot Grouping Strategy

This repository uses Dependabot with smart grouping to reduce the number of dependency update PRs and minimize noise.

## Grouping Strategy

### GitHub Actions
- **github-actions**: Minor and patch updates grouped together
- **github-actions-major**: Major updates in separate PRs for careful review

### Python Backend (Poetry/pip)
- **python-runtime**: Runtime dependencies (FastAPI, Neo4j, etc.) minor/patch updates  
- **python-dev-tools**: Development tools (Black, pytest, etc.) minor/patch updates
- **python-major**: All major updates in separate PRs

### Frontend (npm)
- **frontend-runtime**: React, MUI, and runtime dependencies minor/patch updates
- **frontend-dev-tools**: TypeScript, ESLint, Vite and dev tools minor/patch updates  
- **frontend-major**: All major updates in separate PRs

### Root Dev Tools (npm)
- **root-dev-tools**: Prettier and configuration tools minor/patch updates
- **root-dev-major**: Major updates in separate PRs

### Docker
- **docker-images**: Base image updates minor/patch grouped
- **docker-major**: Major base image updates in separate PRs

## Benefits

1. **Reduced Noise**: Instead of individual PRs for each dependency, related updates are grouped
2. **Easier Review**: Similar dependencies are updated together, making reviews more efficient
3. **Risk Management**: Major updates are kept separate for careful evaluation
4. **Consistent Labeling**: All PRs are labeled with "dependencies" and follow conventional commit format

## Update Schedule

All ecosystems are checked monthly to balance staying current with reducing maintenance overhead.