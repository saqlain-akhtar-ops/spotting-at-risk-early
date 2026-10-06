# Git notes from the fourth notebook page

This attachment is a mock-test answer sheet, rather than a requirement to alter the project. The following commands explain the listed concepts. Run destructive/history-changing commands only when you intend that effect.

| Command | Purpose |
| --- | --- |
| `git add -A` | Stage new files, modifications, and deletions. |
| `git add -u` | Stage modifications and deletions of tracked files. |
| `git add -p` | Choose changes interactively. |
| `git add -n` | Preview staging without changing the index. |
| `git add -f file` | Explicitly stage an ignored file. Never use for secrets. |
| `git add -v file` | Display files while staging. |
| `git commit -m "message"` | Commit with a message. |
| `git commit --amend` | Replace the most recent commit. Avoid on shared history. |
| `git commit --amend --no-edit` | Amend while keeping its message. |
| `git commit --allow-empty -m "message"` | Create a commit without file changes. |
| `git commit -s` | Add a Signed-off-by line; it is not a cryptographic signature. |
| `git switch -c codex/backend` | Create and switch to a branch. |
| `git status --short` | Compact working-tree status. |
| `git status --ignored` | Also show ignored files. |
| `git log --oneline` | Compact commit history. |
| `git log -p` | Show patches in history. |
| `git log --stat` | Show change statistics. |
| `git log --graph --oneline --all` | Draw branch history. |

Dependencies, operational databases, local credentials, uploaded files, and analytical data exports are ignored by this repository. No repository was published: the connected GitHub account exposed no repositories, and no destination was supplied.
