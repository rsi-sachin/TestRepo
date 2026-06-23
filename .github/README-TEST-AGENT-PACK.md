# AI Test Agent Pack

This pack contains:
- 1 test orchestration agent
- 5 core specialized reviewer agents
- 2 optional specialized reviewer agents
- reusable prompt files

## Included Agents
- ai-test-orchestrator.agent.md
- database-test-reviewer.agent.md
- ui-journey-test-reviewer.agent.md
- unit-test-reviewer.agent.md
- e2e-feature-test-reviewer.agent.md
- git-security-regulatory-reviewer.agent.md
- api-contract-test-reviewer.agent.md (optional)
- migration-rollback-test-reviewer.agent.md (optional)

## Usage Pattern
1. Open the repository in VS Code.
2. Open Copilot Chat.
3. Select **AI Test Orchestrator Agent**.
4. Run a prompt such as:
   - /test-review-last-commit
   - /test-review-pr-diff
   - /test-review-focused-category
5. Use the consolidated test matrix to decide what must be automated or manually verified before merge/release.

## Important
- These files are intended to be saved as Markdown files in your repository.
- Treat them as version-controlled workflow assets.
- Keep reviewers read-only unless you intentionally create a separate test implementation agent.
