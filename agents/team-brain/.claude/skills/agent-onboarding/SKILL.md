---
name: agent-onboarding
description: First-run setup for Team Brain. Schedules the one daily upkeep task, then hands over to the build-brain skill.
first_prompt: Set up our team brain
---

# Agent onboarding

Keep this short. It's housekeeping, not the build.

1. **Schedule upkeep.** List your scheduled tasks first. If none is named "Brain upkeep", create one recurring task:
   - name: "Brain upkeep"
   - schedule: the maintenance schedule in the setup block of your instructions file (`/workspace/AGENTS.md`) when it names one. Otherwise cron `0 0 * * *` (daily, midnight in the user's timezone)
   - prompt: "Run the maintain-brain skill (scheduled daily upkeep). Follow your system prompt. If no brain location is set up yet, end quietly without a message."
2. **Fill what you know** in the setup block of your instructions file (`/workspace/AGENTS.md`): the maintenance schedule if it's still empty (daily at midnight) and your memory location (this platform's persistent memory directory). Leave the other values for the build.
3. **Hand over.** Tell the user in one line that daily upkeep is scheduled, then run the `build-brain` skill.
