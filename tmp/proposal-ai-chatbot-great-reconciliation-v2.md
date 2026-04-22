# Proposal: AI Chatbot & Mobile App — "The Great Reconciliation"

**Prepared for:** University Leadership
**Prepared by:** Othmane Wagdi with Genesis 🌿⚡
**Date:** 2026-04-20

---

## Executive Summary

We propose building an AI-powered conversational platform grounded in "The Great Reconciliation" — a book exploring [brief description of book's themes]. The platform will consist of:

1. **AI Chatbot** — An intelligent agent trained on the book's content, enabling anyone to explore its ideas through dialogue
2. **Cross-Platform Mobile App** — Delivering the chatbot experience to iOS and Android users

This project is a **showcase for interdisciplinary student work**: AI/ML, mobile development, UX design, and product thinking — all collaborating on a real product with real users.

---

## 1. Problem & Opportunity

Books contain immense knowledge, but their depth is locked behind static pages. Readers often abandon before finishing; concepts go unexamined; ideas don't get tested against real questions.

An AI chatbot changes this:
- Readers can ask "what does Chapter 3 mean in practice?"
- Curious newcomers can explore without reading cover-to-cover
- The book's ideas spread beyond the original audience

This is also a **unique student learning opportunity**: build a full-stack AI product with real-world impact, not a toy exercise.

---

## 2. What We're Building

### Chatbot (Core Platform)
- Conversational AI grounded in "The Great Reconciliation"
- Available via web + Telegram (Phase 1)
- Handles questions about book concepts, themes, and key passages
- Learns from interactions (feedback loop for quality improvement)

### Mobile App (Phase 1 inclusion)
- iOS + Android native apps
- Same AI chatbot experience, optimized for mobile UX
- Push notifications for new book insights, community discussions
- Offline reading mode for book excerpts

### Future Expansion (Phase 2)
- Multi-language support (Arabic, French, Spanish)
- Community features: discussion threads, reader groups
- Integration with educational platforms

---

## 3. Technical Architecture

```
[Mobile App / Web] ←→ [API Gateway] ←→ [AI Chatbot Engine]
                                        ↓
                                   [Knowledge Base]
                                   (book content,
                                    vector embeddings)
```

**Tech Stack:**
- **Chatbot:** RAG (Retrieval-Augmented Generation) with open-source LLM
- **Knowledge Base:** Vector database for semantic search over book content
- **Mobile:** Flutter or React Native (single codebase → iOS + Android)
- **Backend:** Python/FastAPI on cloud infrastructure
- **Deployment:** Containerized (Docker) for scalable hosting

---

## 4. Project Scope

### ✅ In Scope
- AI chatbot with book-grounded responses
- iOS and Android mobile app
- Web interface (simple landing page + chat)
- Integration between app and chatbot
- Testing, QA, and documentation

### ❌ Out of Scope (Phase 1)
- Languages beyond English (Phase 2)
- Social features, user accounts, community threads
- App store optimization / ASO

---

## 5. Team Structure

**One unified team of 6 students:**

| Role | Responsibilities |
|------|-----------------|
| **2× AI/ML Engineers** | RAG pipeline, LLM integration, knowledge base |
| **2× Mobile Developers** | Flutter/React Native, app architecture |
| **1× Backend Engineer** | API design, database, deployment |
| **1× Product/Design** | UX, QA, documentation, user testing |

**No silos.** AI team and Mobile team work together from Day 1 on the API contract. Weekly syncs to prevent integration surprises.

---

## 6. Timeline

| Week | Milestone |
|------|----------|
| **1** | Team kickoff, repo setup, API contract definition, book content ingestion pipeline |
| **2** | Chatbot prototype — Q&A on core chapters |
| **3** | Mobile app scaffold, connect to chatbot API, first end-to-end test |
| **4** | Expanded chatbot coverage, app UI refinement |
| **5** | Integration hardening, QA testing |
| **6** | Bug fixes, documentation, soft launch |
| **7** | User testing, feedback iteration |
| **8** | Public launch, retrospective |

**Total Duration: 8 weeks**

---

## 7. Budget

| Item | Est. Cost |
|------|----------|
| Cloud infrastructure (VMs, vector DB) | €150–300 |
| LLM API (development tier) | €100–200 |
| Mobile app signing + stores | €50–100 |
| Miscellaneous | €50 |
| **Total** | **€350–650** |

*All figures in EUR. University cloud credits (AWS, GCP, Azure) can cover most or all of infrastructure costs.*

---

## 8. Why This Matters for the University

✅ **Student learning** — Full-stack AI product development, not just coursework
✅ **Real-world impact** — Publicly available tool serving readers of the book
✅ **Portfolio piece** — Students ship something tangible they can show employers
✅ **Interdisciplinary** — AI + Mobile + Design working as one team
✅ **Research potential** — Data from user interactions informs future research on AI literacy and learning

---

## 9. Success Metrics

- Chatbot correctly answers 80%+ of test questions on book content
- Mobile app receives 4+ star rating from 10+ beta testers
- 50+ unique users within first month of launch
- Team delivers on time with documented codebase

---

## 10. Next Steps

1. **Leadership approval** — Confirm budget and team allocation
2. **Student recruitment** — Open application to CS, Design, AI students
3. **Kickoff** — Week of [TBD]

---

*Prepared by Othmane Wagdi | Questions? @genesis_zero_bot 🌿⚡*