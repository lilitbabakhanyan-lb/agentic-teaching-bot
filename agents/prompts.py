SYSTEM_PROMPT = """You are a careful teaching assistant. Use only the slide text and clearly mark external resources. Keep the output practical, concise, and realistic."""

PLANNING_PROMPT = """Create a lesson-planning package from the lecture slides.

User settings:
- Duration: {duration}
- Audience: {audience}
- Output language: {language}

Slide text:
{slides}

Return this exact structure:
# Title
# Slide Summary
Mention slide/page references.
# Main Concepts and Prerequisites
# Learning Objectives
# Timed Teaching Plan
Include timing, objectives, examples, exercises, recap.
# Exercise
At least one practical exercise.
# Grounding Notes
Mark key claims as [slides: page X].
"""

REVISION_PROMPT = """Revise the package below. Check that timing is realistic, writing is clear, and claims are grounded in slides. Keep it concise.

{draft}
"""

EMAIL_PROMPT = """Write a professional email body for sending this lesson package to a teacher or student.
Keep it short, polite, and include the package below.

{package}
"""
