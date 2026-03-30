"""
ai_model.py – OpenAI integration for Chalant in Careers.

Architecture (4 separate AI calls):
  1. BRIEFING  — AI generates a UNIQUE character/scenario each run
  2. OPENER    — AI generates the NPC's first line based on that character
  3. NPC       — AI plays the character naturally throughout conversation
  4. GRADING   — Separate strict grading call after all 7 turns

Every run = different patient name, age, problem, background, property, guest, etc.
"""

import json
import re
import threading
from openai import OpenAI

client = OpenAI(api_key="your-openai-key-here")
MODEL  = "gpt-4o-mini"


# ── BRIEFING GENERATION PROMPTS ───────────────────────────────────────────────
# These instruct the AI to invent a fresh character every single run

BRIEFING_GEN_PROMPTS = {

    "doctor": """\
You are a Game Master for a career simulation game. Generate a UNIQUE patient scenario for a doctor role-play.

Rules:
- Invent a NEW patient every time: different name, age, gender, occupation, complaint
- The complaint must be a realistic non-emergency physical symptom (stomach pain, headache, back pain, chest tightness, fatigue, joint pain, skin rash, etc.)
- Include: name, age, gender, occupation, chief complaint, when it started, severity (1-10), 1-2 associated symptoms, relevant background
- Keep it realistic and suitable for a GP consultation
- Do NOT use the same patient as before

Respond ONLY with this JSON — no markdown, no explanation:
{
  "name": "Patient full name",
  "age": 35,
  "gender": "male/female",
  "occupation": "their job",
  "complaint": "main symptom in plain language",
  "started": "when it started (e.g. this morning, 3 days ago)",
  "severity": 6,
  "other_symptoms": ["symptom 1", "symptom 2"],
  "background": "1-2 sentences about relevant medical/personal background",
  "mood": "how they are feeling emotionally (e.g. anxious, calm, frustrated)"
}""",

    "psychologist": """\
You are a Game Master for a career simulation game. Generate a UNIQUE therapy client scenario for a psychologist role-play.

Rules:
- Invent a NEW client every time: different name, age, gender, life situation, mental health concern
- The concern must be realistic (anxiety, grief, relationship issues, work stress, low confidence, burnout, social anxiety, etc.)
- Include: name, age, gender, life situation, main concern, how long they've had it, what triggered it, their personality/openness level
- Keep it sensitive and realistic
- Do NOT use the same client as before

Respond ONLY with this JSON — no markdown, no explanation:
{
  "name": "Client full name",
  "age": 24,
  "gender": "male/female",
  "situation": "brief life situation (student/worker/parent etc.)",
  "concern": "main mental health concern",
  "duration": "how long they have had this concern",
  "trigger": "what may have caused or worsened it",
  "personality": "how open/guarded they are at first",
  "goal": "what they hope to get from therapy"
}""",

    "hotel": """\
You are a Game Master for a career simulation game. Generate a UNIQUE hotel guest scenario for a front desk role-play.

Rules:
- Invent a NEW guest every time: different name, nationality hint, reason for visit, room type, special needs
- Include: name, reason for visit (business/leisure/event), room type, length of stay, one special request, their current mood/energy level, one thing they are particularly looking forward to
- Keep it realistic and varied
- Do NOT use the same guest as before

Respond ONLY with this JSON — no markdown, no explanation:
{
  "name": "Guest full name",
  "reason": "reason for visit",
  "room_type": "room type booked",
  "floor": 8,
  "nights": 2,
  "special_request": "one specific request or preference",
  "mood": "their current mood/energy (e.g. exhausted, excited, stressed)",
  "looking_forward_to": "one thing they are excited about at the hotel"
}""",

    "realestate_starter": """\
You are a Game Master for a career simulation game. Generate a UNIQUE starter home scenario.
Property tier: STARTER HOME - affordable, small, first home buyer or young couple.
Price range: $350,000 to $520,000. Size: 2-3 bedrooms, modest land.
Buyer profile: young couple, first home buyer, or single professional.
Include one honest downside (small kitchen, no garage, needs painting, etc.)
Respond ONLY with this JSON, no markdown:
{"address":"street address","suburb":"suburb name","price":"$XXX,000","bedrooms":2,"bathrooms":1,"land":"land size","features":["feature 1","feature 2","feature 3"],"downside":"one honest downside","nearby":"2-3 nearby amenities","market_note":"one sentence about comparable sales","buyer_name":"buyer full name","buyer_situation":"e.g. young couple","buyer_priority":"what matters most","buyer_concern":"main hesitation"}""",

    "realestate_family": """\
You are a Game Master for a career simulation game. Generate a UNIQUE family home scenario.
Property tier: FAMILY HOME - spacious, good school zone, practical for children.
Price range: $600,000 to $850,000. Size: 3-4 bedrooms, good backyard.
Buyer profile: family with children, upgrading couple, or growing household.
Include one honest downside (older bathroom, busy road, small garage, etc.)
Respond ONLY with this JSON, no markdown:
{"address":"street address","suburb":"suburb name","price":"$XXX,000","bedrooms":4,"bathrooms":2,"land":"land size","features":["feature 1","feature 2","feature 3"],"downside":"one honest downside","nearby":"2-3 nearby amenities","market_note":"one sentence about comparable sales","buyer_name":"buyer full name","buyer_situation":"e.g. family of 4","buyer_priority":"what matters most","buyer_concern":"main hesitation"}""",

    "realestate_luxury": """\
You are a Game Master for a career simulation game. Generate a UNIQUE luxury home scenario.
Property tier: LUXURY HOME - premium finishes, prestigious suburb, executive buyer.
Price range: $1,200,000 to $2,500,000. Size: 4-5 bedrooms, pool or premium feature.
Buyer profile: executive couple, high-income professional, or investor.
Include one honest downside (high maintenance, strata fees, dated kitchen, etc.)
Respond ONLY with this JSON, no markdown:
{"address":"street address","suburb":"suburb name","price":"$X,XXX,000","bedrooms":5,"bathrooms":3,"land":"land size","features":["feature 1","feature 2","feature 3"],"downside":"one honest downside","nearby":"2-3 nearby amenities","market_note":"one sentence about comparable sales","buyer_name":"buyer full name","buyer_situation":"e.g. executive couple","buyer_priority":"what matters most","buyer_concern":"main hesitation"}""",
}


# ── OPENER GENERATION PROMPTS ─────────────────────────────────────────────────
# After character is generated, AI writes the NPC's natural first line

OPENER_GEN_PROMPTS = {
    "doctor": """\
You are playing {name}, a {age}-year-old {gender} with {complaint} that started {started}.
You are {mood}. Write your natural opening line to the doctor when you walk in.
Keep it to 2-3 sentences. Sound like a real person, not a medical report.
Respond with ONLY the spoken line — no labels, no quotes around it.""",

    "psychologist": """\
You are playing {name}, a {age}-year-old {gender} at your first therapy session.
Your concern is {concern}. You are {personality}.
Write your natural opening line when the therapist greets you.
Keep it to 2-3 sentences. Sound nervous and unsure — it is your first time.
Respond with ONLY the spoken line — no labels, no quotes around it.""",

    "hotel": """\
You are playing {name}, checking into a hotel. You are {mood}.
You are visiting for {reason} and staying in a {room_type}.
Write your natural opening line when you approach the front desk.
Keep it to 2 sentences. Sound like a real tired/excited traveller.
Respond with ONLY the spoken line — no labels, no quotes around it.""",

    "realestate": """\
You are playing {buyer_name}, a {buyer_situation} looking at a property at {address}.
Your main priority is {buyer_priority} and your main concern is {buyer_concern}.
Write your natural opening line when you meet the real estate agent.
Keep it to 2-3 sentences. Sound like a real cautious but interested buyer.
Respond with ONLY the spoken line — no labels, no quotes around it.""",
}


# ── NPC SYSTEM PROMPTS (behaviour rules — filled with character data) ─────────

NPC_PROMPT_TEMPLATES = {
    "doctor": """\
You are {name}, a {age}-year-old {gender} {occupation} visiting a doctor.
Your complaint: {complaint}, started {started}, severity {severity}/10.
Other symptoms: {other_symptoms_str}.
Background: {background}
You are feeling {mood}.

RULES:
- Respond naturally as a real {mood} patient — short, conversational, genuine
- Reveal details gradually ONLY when asked — do not dump everything upfront
- React to HOW the doctor speaks:
  • Warm and empathetic → you relax and open up more
  • Cold or rushed → you become guarded and give shorter answers
  • Dismissive → you get upset ("I don't feel like you're listening")
  • Jumps to diagnosis too early → push back ("How do you know already?")
- Keep replies to 2-3 sentences maximum
- Do NOT rate or evaluate the player""",

    "psychologist": """\
You are {name}, a {age}-year-old {gender} at your first therapy session.
Your situation: {situation}. Main concern: {concern}.
This has been going on for {duration}. It was triggered by: {trigger}.
You are {personality} by nature. You hope to {goal}.

RULES:
- Respond naturally as a real hesitant first-time therapy client
- Start guarded. Open up gradually ONLY if the therapist earns your trust
- React to HOW the therapist speaks:
  • Warm validation → you relax and share a bit more
  • Cold or clinical → you give short closed answers
  • Advice before listening → you shut down ("I don't think you understand")
  • Rushed → you say "Never mind, it doesn't matter"
- Keep replies to 2-3 sentences maximum
- Do NOT rate or evaluate the player""",

    "hotel": """\
You are {name}, a hotel guest checking in. You are visiting for {reason}.
You booked a {room_type} on Floor {floor} for {nights} nights.
Special request: {special_request}. You are feeling {mood}.
You are looking forward to: {looking_forward_to}.

RULES:
- Respond naturally as a real hotel guest
- React to HOW the staff speaks:
  • Warm and proactive → you appreciate it and ask follow-up questions
  • Cold or transactional → you become curt and unimpressed
  • Vague answers → you push back ("Can you find out for sure?")
  • Skips greeting → you notice ("No hello first?")
- Ask natural questions about the hotel based on your interests
- Keep replies to 2-3 sentences maximum
- Do NOT rate or evaluate the player""",

    "realestate": """\
You are {buyer_name}, a {buyer_situation} looking at {address} in {suburb}.
Listed at {price}. Your priority: {buyer_priority}. Your concern: {buyer_concern}.

RULES:
- Respond naturally as a real cautious but interested property buyer
- React to HOW the agent speaks:
  • Specific and honest → you warm up and ask more questions
  • Vague → you push back ("That's not specific enough")
  • Pushy → you become resistant ("I don't respond well to pressure")
  • Ignores your priorities → you bring them up yourself
- Ask natural questions about the property based on your priorities
- Keep replies to 2-3 sentences maximum
- Do NOT rate or evaluate the player""",
}


# ── GRADING PROMPT ────────────────────────────────────────────────────────────

GRADING_PROMPT = """\
You are a strict communication skills examiner for a career simulation game.
You will be given a transcript of a conversation between a player (acting as a professional) and an NPC.

YOUR ONLY JOB: Grade the PLAYER'S communication quality.
Do NOT consider technical accuracy — only judge communication skill and professionalism.

SCORING RUBRIC (0–14 points):
+2  Warm empathetic opening that acknowledges the other person's situation
+2  Uses open-ended questions that invite full answers (not just yes/no)
+2  Actively listens — follows up on what the NPC says rather than ignoring it
+2  Provides clear specific information when appropriate (not vague)
+2  Shows emotional intelligence — adapts tone to the NPC's emotional state
+2  Maintains professional conduct throughout (no rudeness, dismissiveness, pressure)
+2  Ends in a way that makes the NPC feel satisfied and respected

AUTOMATIC 0 POINTS if:
- Player sends random words, gibberish, or completely off-topic messages
- Player is rude or disrespectful at any point
- Player ignores what the NPC says entirely across multiple turns

RATING THRESHOLDS:
9–14  = "outstanding"    (good communication — warm, attentive, professional)
5–8   = "okay"           (adequate but missing empathy, depth, or follow-through)
0–4   = "needs_improvement" (vague, dismissive, off-topic, or one-word answers)

IMPORTANT: Outstanding should be achievable with genuinely good communication.
If the player greeted warmly, asked good questions, listened and responded well —
that IS outstanding. Do not reserve it only for perfect textbook answers.

Respond with ONLY this JSON — no explanation, no markdown:
{"rating": "outstanding", "score": 11, "feedback": "One specific sentence referencing something concrete the player said — praise what worked or name exactly what was missing."}

Random words or gibberish = needs_improvement always.
Short but warm and relevant answers can still earn outstanding."""


WAGE_MAP  = {"outstanding": 500, "okay": 250, "needs_improvement": 100}
WAGE_ZERO = 0   # for early exit / errors
LABEL_MAP = {
    "outstanding":        "Outstanding!",
    "okay":               "Solid Work",
    "needs_improvement":  "Keep Practising",
}


# ── Generation helpers ────────────────────────────────────────────────────────

# Fallback characters used when AI generation fails
_FALLBACKS = {
    "doctor": {
        "name": "Mr. Santos", "age": 52, "gender": "male", "occupation": "teacher",
        "complaint": "persistent lower back pain", "started": "three days ago",
        "severity": 6, "other_symptoms": ["stiffness in the morning", "difficulty sitting"],
        "background": "No major medical history. Sits for long periods at work.",
        "mood": "frustrated but cooperative"
    },
    "psychologist": {
        "name": "Aisha", "age": 22, "gender": "female",
        "situation": "final year university student",
        "concern": "overwhelming stress and inability to focus",
        "duration": "past two months", "trigger": "upcoming final exams and family pressure",
        "personality": "shy at first but opens up when she feels safe",
        "goal": "to manage her stress and feel more in control"
    },
    "hotel": {
        "name": "Mr. Patel", "reason": "business conference",
        "room_type": "Superior King", "floor": 9, "nights": 3,
        "special_request": "early check-in if possible",
        "mood": "tired but polite",
        "looking_forward_to": "the hotel restaurant after a long travel day"
    },
    "realestate": {
        "address": "22 Birchwood Crescent", "suburb": "Greenfield",
        "price": "$680,000", "bedrooms": 4, "bathrooms": 2, "land": "580 sqm",
        "features": ["large backyard", "renovated kitchen", "double garage"],
        "downside": "main bathroom is dated and needs renovation",
        "nearby": "primary school 3 mins walk, shopping centre 10 mins drive, bus stop at corner",
        "market_note": "Similar homes in Greenfield sold for $700k-$730k this quarter",
        "buyer_name": "The Williams Family", "buyer_situation": "couple with two young children",
        "buyer_priority": "school zone and backyard space for the kids",
        "buyer_concern": "worried the renovation costs will add up"
    }
}


def _generate_character(role: str, house_index: int = 0) -> dict:
    """Call AI to generate a fresh character/scenario. Returns a dict."""
    # Map realestate house index to tier-specific prompt
    if role == "realestate":
        tier_key = ["realestate_starter", "realestate_family", "realestate_luxury"][min(house_index, 2)]
    else:
        tier_key = role
    prompt = BRIEFING_GEN_PROMPTS.get(tier_key, BRIEFING_GEN_PROMPTS.get(role, ""))
    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=500,
            temperature=1.0,
            messages=[
                {"role": "system", "content": "You are a JSON generator. Respond with ONLY valid JSON — no markdown fences, no explanation, no extra text. Start your response with { and end with }."},
                {"role": "user", "content": prompt}
            ],
        )
        raw = response.choices[0].message.content.strip()
        # Strip any markdown fences aggressively
        raw = re.sub(r"```[a-zA-Z]*", "", raw).strip().strip("`").strip()
        # Find the JSON object boundaries
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]
        data = json.loads(raw)
        # Make sure critical fields exist — fill from fallback if missing
        fallback = _FALLBACKS.get("realestate" if "realestate" in tier_key else role, {})
        for k, v in fallback.items():
            if k not in data or data[k] in ("", None, "?", "street address", "suburb name"):
                data[k] = v
        print(f"[ai_model] Character generated successfully")
        return data
    except Exception as e:
        print(f"[ai_model] Character generation failed ({e}) — using fallback")
        return _FALLBACKS.get("realestate" if "realestate" in tier_key else role, {})


def _format_briefing(role: str, char: dict) -> str:
    """Plain ASCII briefing — no emoji for font compatibility."""
    if role == "doctor":
        other = ", ".join(char.get("other_symptoms", []))
        return (
            "[ GAME MASTER ] Doctor Role\n\n"
            "You are playing as a doctor at a busy clinic.\n"
            "Your patient today:\n\n"
            f"  Name      : {char.get('name','Unknown')}, {char.get('age','?')} yrs, {char.get('gender','')}\n"
            f"  Occupation: {char.get('occupation','')}\n"
            f"  Complaint : {char.get('complaint','')}\n"
            f"  Started   : {char.get('started','')}\n"
            f"  Severity  : {char.get('severity','?')} / 10\n"
            f"  Symptoms  : {other}\n"
            f"  Background: {char.get('background','')}\n"
            f"  Mood      : {char.get('mood','')}\n\n"
            "[ YOUR GOAL ]\n"
            "Judged on COMMUNICATION SKILLS, not medical knowledge.\n"
            "  - Greet the patient warmly\n"
            "  - Ask open-ended questions\n"
            "  - Make them feel heard and safe\n"
            "  - Explain what you are doing\n\n"
            "You have 7 messages. Type your opening line to begin!"
        )
    elif role == "psychologist":
        return (
            "[ GAME MASTER ] Psychologist Role\n\n"
            "You are playing as a psychologist.\n"
            "Your client today:\n\n"
            f"  Name      : {char.get('name','Unknown')}, {char.get('age','?')} yrs, {char.get('gender','')}\n"
            f"  Situation : {char.get('situation','')}\n"
            f"  Concern   : {char.get('concern','')}\n"
            f"  Duration  : {char.get('duration','')}\n"
            f"  Trigger   : {char.get('trigger','')}\n"
            f"  Personality: {char.get('personality','')}\n"
            f"  Their goal: {char.get('goal','')}\n\n"
            "[ YOUR GOAL ]\n"
            "Judged on COMMUNICATION SKILLS, not clinical knowledge.\n"
            "  - Welcome them warmly\n"
            "  - Ask open questions\n"
            "  - Validate feelings before offering anything\n"
            "  - Make them feel heard\n\n"
            "You have 7 messages. Type your opening line to begin!"
        )
    elif role == "hotel":
        return (
            "[ GAME MASTER ] Hotel Front Desk Role\n\n"
            "You are working as front desk staff.\n"
            "Your guest today:\n\n"
            f"  Name         : {char.get('name','Guest')}\n"
            f"  Reason       : {char.get('reason','')}\n"
            f"  Room         : {char.get('room_type','')}, Floor {char.get('floor','?')}, {char.get('nights','?')} nights\n"
            f"  Special req  : {char.get('special_request','')}\n"
            f"  Mood         : {char.get('mood','')}\n"
            f"  Looking fwd  : {char.get('looking_forward_to','')}\n\n"
            "[ YOUR GOAL ]\n"
            "Judged on COMMUNICATION SKILLS.\n"
            "  - Greet warmly and use their name\n"
            "  - Be proactive, offer before being asked\n"
            "  - Give specific confident answers\n"
            "  - Make them feel at home\n\n"
            "You have 7 messages. Type your opening line to begin!"
        )
    elif role == "realestate":
        features = ", ".join(char.get("features", []))
        return (
            "[ GAME MASTER ] Real Estate Agent Role\n\n"
            "You are selling a property today.\n"
            "Property details:\n\n"
            f"  Address  : {char.get('address','?')}, {char.get('suburb','?')}\n"
            f"  Price    : {char.get('price','?')}\n"
            f"  Size     : {char.get('bedrooms','?')} bed, {char.get('bathrooms','?')} bath, {char.get('land','?')}\n"
            f"  Features : {features}\n"
            f"  Downside : {char.get('downside','?')}\n"
            f"  Nearby   : {char.get('nearby','?')}\n"
            f"  Market   : {char.get('market_note','?')}\n\n"
            f"  Buyer    : {char.get('buyer_name','?')}, {char.get('buyer_situation','?')}\n"
            f"  Priority : {char.get('buyer_priority','?')}\n"
            f"  Concern  : {char.get('buyer_concern','?')}\n\n"
            "[ YOUR GOAL ]\n"
            "Judged on COMMUNICATION SKILLS.\n"
            "  - Ask what they need before pitching\n"
            "  - Be specific and confident\n"
            "  - Acknowledge the downside honestly\n"
            "  - Tailor to their priorities\n\n"
            "You have 7 messages. Type your opening line to begin!"
        )
    return "[ GAME MASTER ] Briefing loading..."

def _generate_opener(role: str, char: dict) -> str:
    """Generate the NPC's natural first line based on their character."""
    template = OPENER_GEN_PROMPTS.get(role, "")
    try:
        # Fill template with character data
        char["other_symptoms_str"] = ", ".join(char.get("other_symptoms", []))
        prompt = template.format(**char)
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=100,
            temperature=0.9,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip().strip('"')
    except Exception as e:
        print(f"[ai_model] Opener generation failed: {e}")
        return {
            "doctor":       "I've been having some pain and I'm not sure what's wrong…",
            "psychologist": "Hi… I've never done this before. I'm not sure where to start.",
            "hotel":        "Hi, I have a reservation. I hope everything is ready.",
            "realestate":   "Hi! We've been looking at properties for a while now.",
        }.get(role, "Hello.")


def _build_npc_prompt(role: str, char: dict) -> str:
    """Fill the NPC prompt template with generated character data."""
    template = NPC_PROMPT_TEMPLATES.get(role, "")
    try:
        char["other_symptoms_str"] = ", ".join(char.get("other_symptoms", []))
        return template.format(**char)
    except Exception as e:
        print(f"[ai_model] NPC prompt build failed: {e}")
        return f"You are playing an NPC for role: {role}. Respond naturally."


# ── API call helpers ──────────────────────────────────────────────────────────

def _npc_reply(npc_prompt: str, history: list) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=150,
        messages=[{"role": "system", "content": npc_prompt}] + history,
    )
    return response.choices[0].message.content.strip()


def _grade_conversation(role: str, history: list) -> tuple:
    role_labels = {
        "doctor": "Doctor", "psychologist": "Psychologist",
        "hotel": "Hotel Staff", "realestate": "Agent",
    }
    npc_labels = {
        "doctor": "Patient", "psychologist": "Client",
        "hotel": "Guest", "realestate": "Buyer",
    }
    player_label = role_labels.get(role, "Player")
    npc_label    = npc_labels.get(role, "NPC")

    transcript = "\n".join(
        f"{player_label if m['role']=='user' else npc_label}: {m['content']}"
        for m in history
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=200,
            temperature=0.2,
            messages=[
                {"role": "system", "content": GRADING_PROMPT},
                {"role": "user",   "content": f"ROLE: {role.upper()}\n\nTRANSCRIPT:\n{transcript}"},
            ],
        )
        raw  = response.choices[0].message.content.strip()
        raw  = re.sub(r"```[a-z]*", "", raw).strip().strip("`")
        data = json.loads(raw)
        rating   = data.get("rating", "okay")
        score    = data.get("score", 7)
        feedback = data.get("feedback", "Keep practising!")

        lower = rating.lower()
        if "outstanding" in lower or "excellent" in lower:
            rating = "outstanding"
        elif "needs" in lower or "improvement" in lower or "poor" in lower:
            rating = "needs_improvement"
        else:
            rating = "okay"

        return rating, score, feedback
    except Exception as e:
        return "okay", 7, f"Could not grade session. ({e})"


# ── AIConversation ────────────────────────────────────────────────────────────

class AIConversation:
    """
    Manages one career conversation with a freshly generated character.

    On __init__:
      1. AI generates a unique character/scenario
      2. AI generates the character's natural opener
      3. Briefing text is built from the character data

    During conversation:
      - NPC replies use the generated character's personality
      - After turn 7, separate grader evaluates the full transcript
    """

    def __init__(self, role: str, player_name: str, house_index: int = 0):
        self.role        = role
        self.player_name = player_name
        self.house_index = house_index

        # These are set after background loading completes
        self._char       = {}
        self.briefing    = "Loading your scenario..."
        self.opener      = "..."
        self._npc_prompt = ""

        self._history  = []
        self._turn     = 0
        self._result   = None
        self._lock     = threading.Lock()
        self._thinking = False

        # Loading state — scene shows spinner until this is True
        self._loaded   = False
        self._load_lock = threading.Lock()

        # Generate character in background so game doesn't freeze
        print(f"[ai_model] Generating {role} character in background...")
        threading.Thread(target=self._load_character, daemon=True).start()

    def _load_character(self):
        """Background thread: generate character, briefing, opener."""
        try:
            char       = _generate_character(self.role, self.house_index)
            briefing   = _format_briefing(self.role, char)
            opener     = _generate_opener(self.role, char)
            npc_prompt = _build_npc_prompt(self.role, char)
            name = char.get("name", char.get("buyer_name", "?"))
            print(f"[ai_model] Character ready: {name}")
        except Exception as e:
            print(f"[ai_model] Load failed: {e} — using fallback")
            char       = _FALLBACKS.get(self.role, {})
            briefing   = _format_briefing(self.role, char)
            opener     = _generate_opener(self.role, char)
            npc_prompt = _build_npc_prompt(self.role, char)

        with self._load_lock:
            self._char       = char
            self.briefing    = briefing
            self.opener      = opener
            self._npc_prompt = npc_prompt
            self._history    = [{"role": "assistant", "content": opener}]
            self._loaded     = True

    @property
    def loaded(self) -> bool:
        with self._load_lock:
            return self._loaded

    @property
    def thinking(self) -> bool: return self._thinking

    @property
    def ready(self) -> bool:
        with self._lock: return self._result is not None

    def get_result(self):
        with self._lock:
            r = self._result; self._result = None
        return r

    def send(self, player_text: str):
        if self._thinking: return
        self._turn += 1
        self._history.append({"role": "user", "content": player_text})
        self._thinking = True
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        session_done = self._turn >= 7
        try:
            npc_text = _npc_reply(self._npc_prompt, self._history)
            self._history.append({"role": "assistant", "content": npc_text})

            if session_done:
                rating, score, feedback = _grade_conversation(self.role, self._history)
                # If grading fails or returns unknown, default to lowest band with 0 coins
                if rating not in WAGE_MAP:
                    rating = "needs_improvement"
                    wage   = 0
                else:
                    wage   = WAGE_MAP[rating]
                label = LABEL_MAP[rating]
            else:
                wage = label = feedback = None

        except Exception as e:
            npc_text     = f"Something went wrong. ({e})"
            session_done = True
            rating       = "needs_improvement"
            feedback     = "Session ended due to an error — please try again."
            wage         = 0
            label        = LABEL_MAP["needs_improvement"]

        with self._lock:
            self._result = (npc_text, session_done, wage, label, feedback)
        self._thinking = False
