# Alchemy Session Management

How Genesis identifies users, persists their progress, and resumes across sessions.

---

## Data Directory

All user progress lives outside the project repo:

```
~/.openclaw/alchemy/
└── {telegram_user_id}/
    ├── progress.json    ← identity, position, all answers
    └── draft.md         ← running compiled draft (rebuilt on demand)
```

Use the environment variable `ALCHEMY_DATA_DIR` if set; otherwise default to `~/.openclaw/alchemy`.

```bash
ALCHEMY_DATA_DIR="${ALCHEMY_DATA_DIR:-$HOME/.openclaw/alchemy}"
USER_DIR="$ALCHEMY_DATA_DIR/{telegram_user_id}"
```

---

## Identifying the User

**In Telegram:** Every incoming message includes the sender's Telegram user ID (`from.id`). This is stable, unique, and does not change even if the user changes their username. Use it as the directory key.

**How to read it:** The OpenClaw channel context for Telegram includes the sender's `userId` or `chatId`. Use whichever is available:
- Direct messages: `from.id` == `chat.id` — use either.
- Group chats: `from.id` is the user; `chat.id` is the group. Use `from.id` as the user key and `chat.id` for reply delivery.

**On every alchemy trigger:**
```bash
USER_DIR="$ALCHEMY_DATA_DIR/{telegram_user_id}"
PROGRESS_FILE="$USER_DIR/progress.json"
```

If `$PROGRESS_FILE` exists → **resume**. If not → **start fresh**.

---

## Progress JSON Schema

```json
{
  "version": "1.0",
  "telegramUserId": "123456789",
  "chatId": "123456789",
  "name": "Alice",
  "email": "alice@example.com",
  "communityName": "Green Valley Commons",
  "communitySlug": "green-valley-commons",
  "startedAt": "2026-02-28T10:00:00Z",
  "lastActiveAt": "2026-02-28T14:32:00Z",
  "lastNudgedAt": null,
  "status": "in_progress",
  "currentArea": 2,
  "currentSubsection": "2.3 Ideal Community Members",
  "completedAreas": [0, 1],
  "answers": {
    "0": {
      "permanence": "permanent community",
      "status": "idea with land, no construction",
      "communityName": "Green Valley Commons",
      "country": "Portugal",
      "landSize": "12 hectares",
      "milestonesStartedPlanning": "2025"
    },
    "1": {
      "dreamOrigin": "...",
      "values": "...",
      "purpose": "...",
      "missionStatement": "...",
      "vision": "...",
      "goals1yr": "...",
      "goals3yr": "...",
      "goals5yr": "...",
      "goals10yr": "...",
      "communityType": "Farm/Permaculture + Wellness",
      "location": "Alentejo, Portugal",
      "sizeRange": "Village scale, 20–80 people",
      "counterparts": "..."
    }
  }
}
```

**Field notes:**
- `status`: `"in_progress"` | `"completed"` | `"paused"`
- `currentArea`: integer 0–11 (or 12 = action plan phase)
- `currentSubsection`: human-readable string for context (e.g. `"3.7 Conflict Resolution"`)
- `completedAreas`: array of area numbers fully signed-off by the user
- `answers`: keyed by area number as string; each area is a flat object of subsection answers
- `lastNudgedAt`: ISO timestamp of last weekly nudge sent (prevents double-nudging)

---

## Session Start Logic

When the alchemy skill triggers:

```
1. Read $PROGRESS_FILE if it exists
2. IF file exists AND status == "in_progress":
     → Greet by name
     → Show progress summary (completed areas, current position)
     → Ask: "Ready to continue with Area {N}: {Name}? Or would you like to revisit a previous area?"
3. IF file exists AND status == "completed":
     → Offer to review, update, or regenerate the final document
4. IF file does not exist:
     → Begin fresh session setup (collect name, email, chat ID, community name)
     → Create $USER_DIR and write initial progress.json
```

---

## Saving Answers During a Session

After completing each subsection, write answers immediately — don't wait for the area to finish:

```bash
# Update lastActiveAt and save answers for the current area
UPDATED=$(jq \
  --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg area "{current_area}" \
  --argjson areaAnswers '{...subsection answers...}' \
  --arg subsection "{current_subsection}" \
  '.lastActiveAt = $now |
   .currentSubsection = $subsection |
   .answers[$area] = (.answers[$area] // {} | . + $areaAnswers)' \
  "$PROGRESS_FILE")
echo "$UPDATED" > "$PROGRESS_FILE"
```

After completing a full area, add it to `completedAreas` and increment `currentArea`:

```bash
UPDATED=$(jq \
  --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson completedArea {area_number} \
  --argjson nextArea {area_number + 1} \
  '.lastActiveAt = $now |
   .completedAreas += [$completedArea] |
   .currentArea = $nextArea |
   .currentSubsection = ""' \
  "$PROGRESS_FILE")
echo "$UPDATED" > "$PROGRESS_FILE"
```

---

## Draft Compilation

The `draft.md` file is rebuilt from `progress.json` at any time using the compile script:

```bash
bash {baseDir}/scripts/compile-draft.sh "$PROGRESS_FILE" "$USER_DIR/draft.md"
```

This can be run:
- After each area completes (to keep draft current)
- When a user asks "show me what we have so far"
- At session end before delivery

---

## Progress Summary (for greetings and check-ins)

Show this whenever resuming or when the user asks for a status update:

```
🔺 Community Alchemy — {Community Name}

✅ Completed: {list of completed area names}
📍 Currently on: Area {N} — {Area Name} ({current subsection})
⬜ Remaining: {list of areas not yet started}

Last session: {X days ago}
```

---

## Weekly Nudge Cron Job

See `{baseDir}/scripts/weekly-nudge.sh` for the nudge script.

**To install as a cron job:**
```bash
# Run every Monday at 9am local time
crontab -e
# Add:
0 9 * * 1 TELEGRAM_BOT_TOKEN=your_token ALCHEMY_DATA_DIR=~/.openclaw/alchemy bash /path/to/skills/alchemy/scripts/weekly-nudge.sh
```

The script skips users who:
- Have `status == "completed"`
- Were nudged less than 6 days ago (`lastNudgedAt`)
- Have been inactive for less than 3 days (too soon to nudge)

---

## Pausing a Session

If a user says they need to stop:
1. Save all current answers to `progress.json`
2. Set `status` to `"in_progress"` (not paused — they may return any time)
3. Rebuild `draft.md`
4. Confirm: *"All saved. Your progress for {Community Name} is safely stored. Message me any time to continue — or I'll check in with you next week."*

---

## Completion

When Area 11 and the Action Plan are finished:
1. Set `status` to `"completed"` in `progress.json`
2. Run `compile-draft.sh` to generate the final document
3. Deliver via Telegram attachment and Google Drive (see SKILL.md delivery section)
4. Archive: copy final document to `$USER_DIR/final-{communitySlug}.md`
