"""Anki card CSS styling."""

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
