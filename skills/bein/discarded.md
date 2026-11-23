# bein discard list (template)

bein copies this file to `~/.bein/discarded.md` on first use and only ever edits that copy.

Approaches bein must not generate again. Claude reads the list before writing far atoms, mutations and write-ups, and never proposes anything on it or a reworded version of it. `jev_judge.py known` also treats every line as a known idea, so candidates that resemble one get filtered out.

Add a line whenever you reject an idea, say "I see this every day", or an idea is built or proved useless. The ledger also adds gaps that someone filled. Format: `- approach — why discarded (date)`. Only lines starting with `- ` count.
