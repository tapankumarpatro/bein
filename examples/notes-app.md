# Example: people abandon their notes app

**Ask:** People stop using their note-taking app after a few weeks because old notes become a pile they never look at again.

Real run on 2026-11-23 with the general `bein` pack, no Jev key. Full data: [notes-app/run.json](notes-app/run.json).

## What Claude usually says

One fresh agent got only the problem and the slot names (no mention of novelty) and returned 15 ideas:

1. Weekly digest that brings back 3 old notes related to this week's writing
2. Sidebar that shows related old notes while you type
3. Spaced-repetition review queue for notes marked important
4. Auto-archive notes untouched for 90 days
5. "On this day": what you wrote a week, month and year ago
6. Weekly AI synthesis of the week's notes into themes
7. Ask a question, get an answer that cites your notes
8. Notes that appear when a matching calendar event, place or person comes up
9. Daily swipe deck to triage new captures
10. Attach each note to an active project
11. A quiet "gardening" count of notes linked or merged
12. Duplicate-and-merge suggestions
13. One tap to share a note as a page
14. On day 7, show one of your notes that answers something you searched for
15. Monthly "what you learned" recap

A web scan found most of these already shipping: Obsidian review plugins, Re:note, LoopNotes, flomo daily review, Evernote's related notes, Taskade's morning resurfacer.

## What bein returned

40 candidates were ranked away from those answers. Two judges scored coherence (they agreed within 1 point on all 40, and 19 averaged 2 or more). After fusing, the top 3 went to a prior-art search.

### 1. Old notes come back to be changed, not read
*Memory reconsolidation (neuroscience): a recalled memory becomes editable again.*
Only one old note is ever visible. It opens in edit mode and can't be put back until you change something: add a line, cross something out, link it. No feed, no digest.
**Check:** notes older than 6 months that get an edit or a new link, per user per month.
**Prior art:** no app found that makes editing the price of resurfacing. *Logged in the gap ledger.*

### 2. Your old note objects when you contradict it
*Cross-examination (law): a witness is called up when testimony conflicts.*
While you write a claim that disagrees with something you wrote before, the old note appears beside it with one question: "Which do you believe now?" Your answer updates the old note.
**Check:** share of resurfaced notes the user edits to disagree with their past self.
**Prior art:** close cousin. The Obsidian Contradiction Finder plugin and Memo detect conflicting notes in batch. New here: it fires while you write and makes you update the old note.

### 3. Questions addressed to a future date
*Time-capsule letters (postal).*
Any note can carry a question for a date, like "Did this plan work?" for three months out. On that date it is the one old note shown, and it waits for your answer.
**Check:** share of delivered questions that get answered.
**Prior art:** known as standalone apps (FutureMe, Capsy, Sealed Notes), but not found inside a notes app. New here: the move into the notes app.

## Numbers

| | Claude's usual ideas | bein |
|---|---|---|
| distance from the usual answers (higher = further) | 3.32 | 4.97 |
| near-duplicate rate | 0.00 | 0.00 |
