import genanki

ANKI_MODEL_ID = 2607392323
ANKI_MODEL_NAME = "greek"

ANKI_CARD2_FRONT_TEMPLATE = """
<div class="front-word">
  {{greek}}
</div>
{{#audio filename}}
<span class="audio-btn-sticky" onclick="new Audio('{{audio filename}}').play()">
  <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#78A75A">
    <path d="M640-440v-80h160v80H640Zm48 280-128-96 48-64 128 96-48 64Zm-80-480-48-64 128-96 48 64-128 96ZM120-360v-240h160l200-200v640L280-360H120Zm280-246-86 86H200v80h114l86 86v-252ZM300-480Z"/>
  </svg>
</span>
{{/audio filename}}
{{#greek}}
<script>
  var audioButton = document.querySelector('.audio-btn-sticky');
  if (audioButton) {
    audioButton.click();
  }
</script>
{{/greek}}
"""

ANKI_CARD2_BACK_TEMPLATE = """
<div class="front-word">
  {{greek}}
</div>
<hr>
<div class="entry">
  <header class="head">
    <div class="hw">{{english}}</div>

    {{#part of speech}}<div class="pos">{{part of speech}}</div>{{/part of speech}}
  </header>

  <section class="senses">
    <div class="defs">{{definitions}}</div>
  </section>

  {{#synonyms}}<div class="rel"><span class="label">Syn.</span> {{synonyms}}</div>{{/synonyms}}
  {{#antonyms}}<div class="rel"><span class="label">Ant.</span> {{antonyms}}</div>{{/antonyms}}

  {{#etymology}}
    <section class="ety">
      <span class="label">Etym.</span> {{etymology}}
    </section>
  {{/etymology}}

  {{#notes}}
    <section class="notes">
      <span class="label">Notes</span> {{notes}}
    </section>
  {{/notes}}
</div>
{{#audio filename}}
<span class="audio-btn-sticky" onclick="new Audio('{{audio filename}}').play()">
  <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#78A75A">
    <path d="M640-440v-80h160v80H640Zm48 280-128-96 48-64 128 96-48 64Zm-80-480-48-64 128-96 48 64-128 96ZM120-360v-240h160l200-200v640L280-360H120Zm280-246-86 86H200v80h114l86 86v-252ZM300-480Z"/>
  </svg>
</span>
{{/audio filename}}
"""


ANKI_CARD1_FRONT_TEMPLATE = """
<div class="front-word">
  {{english}}
</div>
"""

ANKI_CARD1_BACK_TEMPLATE = """
<div class="front-word">
  {{english}}
</div>
<hr>
<div class="entry">
  <header class="head">
    <div class="hw">{{greek}}</div>

    {{#part of speech}}<div class="pos">{{part of speech}}</div>{{/part of speech}}
  </header>

  <section class="senses">
    <div class="defs">{{definitions}}</div>
  </section>

  {{#synonyms}}<div class="rel"><span class="label">Syn.</span> {{synonyms}}</div>{{/synonyms}}
  {{#antonyms}}<div class="rel"><span class="label">Ant.</span> {{antonyms}}</div>{{/antonyms}}

  {{#etymology}}
    <section class="ety">
      <span class="label">Etym.</span> {{etymology}}
    </section>
  {{/etymology}}

  {{#notes}}
    <section class="notes">
      <span class="label">Notes</span> {{notes}}
    </section>
  {{/notes}}
</div>
{{#audio filename}}
<span class="audio-btn-sticky" onclick="new Audio('{{audio filename}}').play()">
  <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#78A75A">
    <path d="M640-440v-80h160v80H640Zm48 280-128-96 48-64 128 96-48 64Zm-80-480-48-64 128-96 48 64-128 96ZM120-360v-240h160l200-200v640L280-360H120Zm280-246-86 86H200v80h114l86 86v-252ZM300-480Z"/>
  </svg>
</span>
{{/audio filename}}
{{#greek}}
<script>
  var audioButton = document.querySelector('.audio-btn-sticky');
  if (audioButton) {
    audioButton.click();
  }
</script>
{{/greek}}
"""

ANKI_SHARED_CSS = """
/* Base colors */
:root {
  --fg: #0d1b2a;       /* Darker navy for text */
  --muted: #6272a4;    /* Brighter, more noticeable muted text */
  --accent: #ff6f61;   /* Warm coral for accents / highlights */
  --bg: #fefefe;       /* Slightly off-white background */
  --rule: #cbd5e1;     /* Clearer divider lines */
  --chip: #e0f7fa;     /* Light cyan chip / tag background */
}


.nightMode .card {
  --fg:#e5e7eb;
  --muted:#94a3b8;
  --accent:#cbd5e1;
  --bg:#0b0f17;
  --rule:#1f2937;
  --chip:#111827;
}

.card {
  position: relative; /* Add this */
  font-family: ui-serif, "Iowan Old Style", "Palatino Linotype", Palatino, "Times New Roman", serif;
  background: var(--bg);
  color: var(--fg);
  font-size: 18px;
  line-height: 1.35;
  padding: 18px 18px 22px;
  max-width: 720px;
  margin: 0 auto;
}

/* Front-only word */
.front-word {
  font-size: 42px;
  font-weight: 700;
  text-align: center;
  margin-top: 40px;
}

/* Headword block */
.head {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 6px 12px;
  align-items: end;
  margin-bottom: 6px;
}
.hw {
  font-weight: 700;
  font-size: 30px;
  letter-spacing: 0.2px;
}
.pron {
  justify-self: end;
  font-family: "Charis SIL", "Gentium Plus", "Times New Roman", serif;
  font-size: 16px;
  color: var(--muted);
}
.pos {
  grid-column: 1 / -1;
  font-variant: small-caps;
  letter-spacing: 0.6px;
  color: var(--muted);
  margin-top: -2px;
}

/* Multi-sense definitions */
.defs {
  margin-top: 8px;
  white-space: pre-line; /* respects user line breaks */
  counter-reset: sense;
}
.defs p, .defs div, .defs li {
  margin: 6px 0;
  padding-left: 1.4rem;
  position: relative;
}
.defs p::before, .defs div::before, .defs li::before {
  counter-increment: sense;
  content: counter(sense) ".";
  position: absolute;
  left: 0;
  top: 0;
  color: var(--muted);
}

/* Example and translation styling */
.q {
  font-style: italic;
  color: var(--accent);
}
.tr {
  font-style: normal;
  color: var(--muted);
}

/* Relations and chips */
.rel {
  margin-top: 8px;
  padding-left: 1.4rem;
  text-indent: -1.4rem;
}
.label {
  font-variant: small-caps;
  letter-spacing: 0.6px;
  color: var(--muted);
  margin-right: 6px;
}
.tags {
  margin-top: 10px;
  font-size: 12px;
  color: var(--muted);
  background: var(--chip);
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
}

/* Etymology / Notes */
.ety, .notes { margin-top: 10px; }
.sep {
  border: 0;
  border-top: 1px solid var(--rule);
  margin: 14px 0 8px;
}

/* Cloze support */
.cloze { font-weight: 700; }

/* Mobile tweaks */
@media (max-width: 420px){
  .card { font-size: 17px; padding: 14px; }
  .hw { font-size: 26px; }
  .pron { font-size: 15px; }
}

/* Hide default Anki audio button */
.audio {
  display: none;
}

.audio-btn-sticky {
  position: absolute;
  top: 20px;
  right: 20px;
  cursor: pointer;
  vertical-align: middle;
  transition: transform 0.2s;
  background: transparent;
  z-index: 1;
}

.audio-btn-sticky:hover {
  transform: scale(1.1);
}
"""

ANKI_NOTE_MODEL_CARDS = [
    {
        "name": "en2gr",
        "qfmt": ANKI_CARD1_FRONT_TEMPLATE,
        "afmt": ANKI_CARD1_BACK_TEMPLATE,
    },
    {
        "name": "gr2en",
        "qfmt": ANKI_CARD2_FRONT_TEMPLATE,
        "afmt": ANKI_CARD2_BACK_TEMPLATE,
    },
]

ANKI_NOTE_MODEL_FIELDS = [
    {"name": field["name"], "ord": idx}
    for idx, field in enumerate(
        [
            {"name": "english"},
            {"name": "greek"},
            {"name": "audio filename"},
            # -------------------------
            {"name": "part of speech"},
            {"name": "definitions"},
            {"name": "synonyms"},
            {"name": "antonyms"},
            {"name": "etymology"},
            {"name": "notes"},
        ]
    )
]

ANKI_NOTE_MODEL = genanki.Model(
    ANKI_MODEL_ID,
    ANKI_MODEL_NAME,
    fields=ANKI_NOTE_MODEL_FIELDS,
    templates=ANKI_NOTE_MODEL_CARDS,
    css=ANKI_SHARED_CSS,
)
