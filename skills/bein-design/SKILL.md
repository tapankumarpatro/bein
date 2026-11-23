---
name: bein-design
description: bein pack for design. Finds non-obvious but usable UI, UX, product, interaction, visual and brand ideas by searching away from Claude's default answers, the usual cards, modals, dashboards and gradients. Use when the user wants an innovative, unusual, fresh or "not generic" design direction, screen, flow, feature concept or brand idea, or says /bein-design.
---

# bein-design

Run the full process of the `bein` skill (its `SKILL.md` sits in the sibling folder `../bein/`) using this pack.

## Slot grammar

```json
"slots": ["need", "form", "medium", "interaction"],
"anchor_slots": ["need"]
```

| Slot | Holds | Home atoms come from |
|---|---|---|
| need | what this user is trying to get done, and the feeling they want | the brief, user research, current pain |
| form | the structural metaphor: what the thing *is* (feed, map, desk, ticket, conversation…) | current screens, plus the far bank |
| medium | where and in what material it lives (screen, sound, print, time of day, email, haptics…) | the current platform, plus the far bank |
| interaction | how the user acts on it (drag to commit, scrub, peek, ritual…) | current flows, plus the far bank |

The mirror step matters a lot here. Claude's default design answers are very uniform (cards, modals, sidebars, onboarding tours), so measuring them gives a strong signal.

## Far atoms

Pick from `references/far-atoms.md`. Choose on **structural fit** with the need, never on looks.

## Feasibility rubric (step 7)

Kill an idea if any answer is "no":
1. Can it be mocked in **≤1 day** and tested with a real user in a week?
2. Can a first-time user grasp it in **≤10 seconds** without a tutorial?
3. Does it meet accessibility basics: keyboard reachable, readable contrast, works without colour or sound alone?
4. Does it fit the product's design system and brand rules (read the project's design guide), or knowingly and openly break one rule?
5. Can it be built on the current stack without a new platform?

Note the main usability risk. Big screen changes still need the user's approval before building.
