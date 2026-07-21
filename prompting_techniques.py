import time
from anthropic import Anthropic
from anthropic import APIConnectionError, RateLimitError, AuthenticationError
from dotenv import load_dotenv

load_dotenv()

# Connects to Claude's API using the key from .env
client = Anthropic()
MODEL = "claude-haiku-4-5-20251001"

# Fixed categories Claude is allowed to choose from
LABELS = ["Bills & Utilities", "Job Alerts", "Shipping & Orders", "Learning & Courses", "High Priority",
          "Alerts & Newsletters"]


# TECHNIQUE 1 — ZERO-SHOT: direct instruction, no examples, no reasoning step

def classify_zero_shot(email_text):
    categories = ",".join(LABELS)

    prompt = f"""Classify this email exactly into one of these email categories:{categories}.\n
  Reply with ONLY the category name, nothing else\n
  Email:
  {email_text}"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=50,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return message.content[0].text.strip()


# TECHNIQUE 2 — FEW-SHOT: shows 3 worked examples (one per category) before the real email

def classify_few_shot(email_text):
    categories = ",".join(LABELS)

    prompt = f"""Classify this email exactly into one of these email categories:{categories}.\n
  Reply with ONLY the category name, nothing else\n

  Example 1:
  Email: "Your Netflix subscription renews tomorrow"
  Category: Bills & Utilities

  Example 2:
  Email: "5 new Software Engineer jobs match your search"
  Category: Job Alerts

  Example 3:
  Email: "Your package from Target has been delivered"
  Category: Shipping & Orders

  Now classify this email:

  Email:
  {email_text}
  """

    message = client.messages.create(
        model=MODEL,
        max_tokens=50,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return message.content[0].text.strip()


# TECHNIQUE 3 — CHAIN-OF-THOUGHT: asks Claude to reason before committing to a final label.
# Returns TWO values (reasoning, final label) — different shape from the other two techniques,
# since the raw response includes reasoning text that must be split off before scoring.

def classify_CoT(email_text):
    categories = ",".join(LABELS)

    prompt = f"""Classify this email into one of these categories: {categories}.
  Think step by step about which category fits best and end  your response with exactly this format on its own line:\n
  Reason: \n
  Final answer: <category>\n

  Email:
  {email_text}
  """

    message = client.messages.create(
        model=MODEL,
        max_tokens=500,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    full_response = message.content[0].text.strip()

    # Split the raw response into reasoning (before) and the clean label (after)

    full_response_parts = full_response.split("Final answer:")
    if len(full_response_parts)<2:
        return full_response, None
    else:
        Reason = full_response_parts[0]
        Final_answer = full_response_parts[1].strip()
        return Reason, Final_answer
