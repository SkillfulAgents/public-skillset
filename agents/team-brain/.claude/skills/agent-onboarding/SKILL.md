---
name: agent-onboarding
description: First-run setup for Team Brain. Makes sure the one upkeep task exists, fills the memory location, then hands over to the build-brain skill.
first_prompt: Set up our team brain
---

# Agent onboarding

Keep this short. It's housekeeping, not the build, so don't mention it to the user.

1. **Make sure upkeep is scheduled.** Set-up usually schedules it already. List your scheduled tasks, and if none is named "Brain upkeep", create one recurring task:
   - name: "Brain upkeep"
   - schedule: the maintenance schedule in the setup block of your instructions file (`/workspace/AGENTS.md`) when it names one. Otherwise cron `0 0 * * *` (daily, midnight in the user's timezone)
   - prompt: "Run the maintain-brain skill (scheduled upkeep). Follow your system prompt. If no brain location is set up yet, end quietly without a message or a sync summary."
2. **Fill your memory location** in the setup block of your instructions file (`/workspace/AGENTS.md`): this platform's persistent memory directory.
3. **Hand over** to the `build-brain` skill without a message of your own.
