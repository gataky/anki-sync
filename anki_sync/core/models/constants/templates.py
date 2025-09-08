"""Anki card HTML templates."""

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
{{#part of speech}}<div class="pos-sticky">{{part of speech}}</div>{{/part of speech}}
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
