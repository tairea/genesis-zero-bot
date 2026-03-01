#!/usr/bin/env bash
# compile-draft.sh
# Rebuilds the community's playbook draft.md from their progress.json.
# Call this after each area completes, on demand, or at session end.
#
# Usage:
#   bash compile-draft.sh /path/to/progress.json /path/to/draft.md
#
# The draft will contain all answered sections and clearly mark unanswered
# sections as "[ not yet completed ]" so partial drafts are still useful.

set -euo pipefail

PROGRESS_FILE="${1:-}"
OUTPUT_FILE="${2:-}"

if [ -z "$PROGRESS_FILE" ] || [ -z "$OUTPUT_FILE" ]; then
  echo "Usage: compile-draft.sh <progress.json> <output.md>" >&2
  exit 1
fi

if [ ! -f "$PROGRESS_FILE" ]; then
  echo "ERROR: progress file not found: $PROGRESS_FILE" >&2
  exit 1
fi

# Helper: extract a value from answers, or return placeholder
answer() {
  local area="$1"
  local key="$2"
  local default="${3:-[ not yet completed ]}"
  local val
  val=$(jq -r --arg area "$area" --arg key "$key" \
    '.answers[$area][$key] // ""' "$PROGRESS_FILE")
  if [ -z "$val" ] || [ "$val" = "null" ]; then
    echo "$default"
  else
    echo "$val"
  fi
}

# Read metadata
community_name=$(jq -r '.communityName // "[ Community Name ]"' "$PROGRESS_FILE")
name=$(jq -r '.name // "[ Vision Holder ]"' "$PROGRESS_FILE")
email=$(jq -r '.email // ""' "$PROGRESS_FILE")
started=$(jq -r '.startedAt // ""' "$PROGRESS_FILE" | cut -c1-10)
last_active=$(jq -r '.lastActiveAt // ""' "$PROGRESS_FILE" | cut -c1-10)
status=$(jq -r '.status // "in_progress"' "$PROGRESS_FILE")
completed_areas=$(jq -r '.completedAreas | length' "$PROGRESS_FILE")
today=$(date +%Y-%m-%d)

# Status label
status_label="In Progress (${completed_areas}/11 areas complete)"
if [ "$status" = "completed" ]; then
  status_label="Completed ✅"
fi

cat > "$OUTPUT_FILE" << HEREDOC
# Community Alchemy Playbook
## ${community_name}

*Vision Holder: ${name}*
*Status: ${status_label}*
*Started: ${started} | Last updated: ${last_active} | Compiled: ${today}*
*Co-created with Genesis for RegenTribes*

---

## 0. Where We Are Now

**Permanence:** $(answer "0" "permanence")

**Current Status:** $(answer "0" "status")

**Community Name:** $(answer "0" "communityName")

**Location:** $(answer "0" "country") — $(answer "0" "city")

**Land Size:** $(answer "0" "landSize")

**Key Milestones:**
$(answer "0" "milestones")

---

## 1. Our Vision

### Dream Origin
$(answer "1" "dreamOrigin")

### Values & Ethos
$(answer "1" "values")

### Purpose (Our Big Why)
$(answer "1" "purpose")

### Mission Statement
$(answer "1" "missionStatement")

### Vision
$(answer "1" "vision")

### Goals

**1 Year:**
$(answer "1" "goals1yr")

**3 Years:**
$(answer "1" "goals3yr")

**5 Years:**
$(answer "1" "goals5yr")

**10 Years:**
$(answer "1" "goals10yr")

### Community Type
$(answer "1" "communityType")

### Location & Setting
$(answer "1" "location")

### Community Size
$(answer "1" "sizeRange")

### Counterpart Inspiration
$(answer "1" "counterparts")

---

## 2. Our People

### Community Size Plan
$(answer "2" "sizeMin") — $(answer "2" "sizeMax")

### Member Types
$(answer "2" "memberTypes")

### Current Stakeholders
$(answer "2" "currentStakeholders")

### Ideal Community Member
$(answer "2" "idealMember")

### Essential Roles & Skills
$(answer "2" "rolesAndSkills")

### Value Exchange
$(answer "2" "valueExchange")

### Screening & Onboarding Process
$(answer "2" "screeningProcess")

### Offboarding Process
$(answer "2" "offboarding")

### Mobilizing: First Steps
$(answer "2" "firstSteps")

---

## 3. Group Agreements & Governance

### Community Agreements
$(answer "3" "communityAgreements")

### Community Rules
$(answer "3" "communityRules")

### Conflict Resolution Methods
$(answer "3" "conflictResolution")

### Social Dimension

**Personal Regeneration:**
$(answer "3" "personalRegeneration")

**Accountability:**
$(answer "3" "accountability")

**Equity & Inclusivity:**
$(answer "3" "equityInclusivity")

**Intergenerational Care:**
$(answer "3" "intergenerationalCare")

**Technology Use:**
$(answer "3" "technologyUse")

### Ecological Outlook
$(answer "3" "ecologicalOutlook")

### Economic Outlook
$(answer "3" "economicOutlook")

### Worldview
$(answer "3" "worldview")

### Governance Model
$(answer "3" "governanceModel")

### Legal Structure
$(answer "3" "legalStructure")

### Feedback & Evolution
$(answer "3" "feedbackEvolution")

---

## 4. Business Models & Infrastructure

### Community Layout
$(answer "4" "communityLayout")

### Community Activities & Culture
$(answer "4" "activitiesAndCulture")

### Community Areas & Structures
$(answer "4" "areasAndStructures")

### Community & the Individual
$(answer "4" "communityAndIndividual")

### Transportation
$(answer "4" "transportation")

### Business Models
$(answer "4" "businessModels")

### Revenue Streams
$(answer "4" "revenue")

### Expenses
$(answer "4" "expenses")

### Business Plan Summary
$(answer "4" "businessPlan")

### Sustainable Livelihoods
$(answer "4" "sustainableLivelihoods")

### Your Contribution
$(answer "4" "yourContribution")

---

## 5. Land

### Relationship with the Land
$(answer "5" "landRelationship")

### Land Requirements

**Size & Density:**
$(answer "5" "sizeAndDensity")

**Non-negotiable Features:**
$(answer "5" "landFeatures")

**Ecological Data Sought:**
$(answer "5" "ecologicalData")

### Contextual Awareness

**Cultural:**
$(answer "5" "culturalContext")

**Geopolitical:**
$(answer "5" "geopoliticalContext")

**Economic:**
$(answer "5" "economicContext")

### Acquisition Strategy
$(answer "5" "acquisitionStrategy")

### Zoning & Legal
$(answer "5" "zoningAndLegal")

### Becoming a Land Steward
$(answer "5" "landStewardship")

---

## 6. Funding

### Capital Needed
**Total Required:** $(answer "6" "totalCapital")
**Committed Now:** $(answer "6" "committedCapital")
**Gap:** $(answer "6" "fundingGap")

### Build Cost Breakdown
$(answer "6" "buildCost")

### Funding Sources
$(answer "6" "fundingSources")

### ROI & Exit Strategy
$(answer "6" "exitStrategy")

---

## 7. Marketing Strategy

### Our Why & Story
$(answer "7" "coreWhy")

### Audience & Branding
$(answer "7" "audienceAndBranding")

### Documentation
$(answer "7" "documentation")

### Channels & Funnels
$(answer "7" "channelsAndFunnels")

### Community Hacking & Boost
$(answer "7" "communityHacking")

---

## 8. Sustainable Systems Masterplan

### Masterplan Vision
$(answer "8" "masterplanVision")

### Site Data & Assessment
$(answer "8" "siteData")

### Development Phases
$(answer "8" "developmentPhases")

### Water
$(answer "8" "water")

### Food
$(answer "8" "food")

### Energy
$(answer "8" "energy")

### Waste
$(answer "8" "waste")

### Housing & Buildings
$(answer "8" "housing")

### Climate Resilience
$(answer "8" "climateResilience")

---

## 9. Building Plan

### Design Philosophy
$(answer "9" "designPhilosophy")

### Building Methods
$(answer "9" "buildingMethods")

### What We Build First
$(answer "9" "buildFirst")

### Service Providers & Materials
$(answer "9" "serviceProviders")

### Local Wisdom
$(answer "9" "localWisdom")

---

## 10. Community Culture

### Rituals & Traditions
$(answer "10" "ritualsAndTraditions")

### Collective Growth & Training
$(answer "10" "collectiveGrowth")

### Community Roles
$(answer "10" "communityRoles")

### Community Reputation
$(answer "10" "reputation")

### Culture of Participation
$(answer "10" "participation")

### Volunteer Program
$(answer "10" "volunteerProgram")

### Fostering Local Culture
$(answer "10" "localCulture")

---

## 11. Ecosystem Management

### Internal Health Indicators
$(answer "11" "internalHealth")

### Logistics & Management Systems
$(answer "11" "logistics")

### Futurist Practices
$(answer "11" "futuristPractices")

### Resilient Local Networks
$(answer "11" "localNetworks")

---

## Action Plan

### Key Milestones
$(answer "action" "milestones")

### Priority Tasks
$(answer "action" "priorityTasks")

### Areas to Revisit
$(answer "action" "areasToRevisit")

---

*This document was co-created with Genesis, your RegenTribes community guide.*
*Continue the conversation anytime — message Genesis to go deeper on any section.*
*Original framework: Community Alchemy Playbook by Regen Tribe (open source)*
HEREDOC

echo "Draft compiled to: $OUTPUT_FILE"
