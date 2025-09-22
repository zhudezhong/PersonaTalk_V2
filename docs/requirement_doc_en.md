# 📖 Requirement Confirmation Document

**Project Name**: AI Roleplay Web App (MVP)  
**Document Version**: v1.1 (with Emotion Recognition)  
**Date**: 2025-09-23  
**Deadline**: 2025-09-28 24:00  

---

## 📑 Table of Contents
- [1. Background & Objective](#1-background--objective)
- [2. Scope Confirmation](#2-scope-confirmation)
  - [2.1 Must-Have Features](#21-must-have-features)
  - [2.2 Optional Features](#22-optional-features)
  - [2.3 Out of Scope](#23-out-of-scope)
- [3. Character Settings](#3-character-settings)
- [4. Technical Implementation](#4-technical-implementation)
- [5. Milestones](#5-milestones)
- [6. Success Criteria](#6-success-criteria)
- [7. Risks & Mitigation](#7-risks--mitigation)

---

## 1. Background & Objective
The goal of this project is to develop an **AI-based roleplay web prototype** where users can search for and select characters (e.g., Harry Potter, Socrates, Einstein) and interact with them via voice.  

A new feature, **Emotion Recognition**, is added to detect the user’s emotional state (positive / negative / neutral) and adjust the character’s tone accordingly.  

---

## 2. Scope Confirmation

### 2.1 Must-Have Features
1. **Character Search & Selection**  
2. **Voice Chat (Single-turn Demo)**  
3. **3 Predefined Characters**  
4. **Emotion Recognition (Basic)**  

### 2.2 Optional Features
- Multi-turn continuous conversation  
- Custom role creation  
- Fine-grained emotions (anger, sadness, joy, surprise, etc.)  
- Animated character avatars (emotion-driven expressions)  

### 2.3 Out of Scope
- Mobile adaptation (desktop only)  
- User login/registration  
- Monetization/payment features  

---

## 3. Character Settings
**Harry Potter, Socrates, Albert Einstein** → persona, tone, emotion response examples.  

---

## 4. Technical Implementation
ASR, LLM, TTS, Emotion Recognition APIs.  

---

## 5. Milestones
| Date | Milestone | Deliverable |
|------|-----------|-------------|
| 9/23 | Scope Freeze | This Requirement Doc v1.1 |
| 9/24 | Prototype & Tech Review | Prototype + Review |
| 9/25–26 | Core Development | Demo (search + voice chat + emotion recognition) |
| 9/27 | Integration & Testing | Internal version |
| 9/28 | Fix & Submission | Final Demo + Docs |

---

## 6. Success Criteria
- Users can search and select characters.  
- Users can complete one full voice interaction.  
- 3 characters respond in consistent style.  
- Emotion recognition adjusts tone.  
- Submission delivered by 9/28 24:00.  

---

## 7. Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|------------|
| Low accuracy in emotion recognition | Replies may feel unnatural | Use basic 3-class model |
| Short dev cycle | Incomplete features | Prioritize must-haves |
| API instability | Blocked functions | Backup APIs / fallback to text |
| Bug accumulation | Final demo unusable | Freeze dev by 9/27 |
