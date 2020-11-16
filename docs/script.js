let currentSection = document.getElementById('proben-select').value;

document.getElementById('proben-select').addEventListener('change', (ev) => {
  document.getElementById(currentSection).hidden = true;
  document.getElementById(ev.target.value).hidden = false;
  currentSection = ev.target.value;
});

for (let input of document.querySelectorAll("#Talentprobe > div > input")) {
  input.addEventListener("change", () => {
    const force = document.getElementById('talentprobe-r').checked ? 'force ' : '';

    const e1 = document.getElementById('talentprobe-e1').value;
    const e2 = document.getElementById('talentprobe-e2').value;
    const e3 = document.getElementById('talentprobe-e3').value;
    const fw = document.getElementById('talentprobe-fw').value;
    const mod = parseInt(document.getElementById('talentprobe-mod').value) || '';
    const comment = document.getElementById('talentprobe-kommentar').value;

    document.getElementById('talentprobe-output').innerText = `!${force}${e1},${e2},${e3}@${fw}${mod} ${comment}`
  });
}

for (let input of document.querySelectorAll("#Sammelprobe > div > input")) {
  input.addEventListener("change", () => {
    const force = document.getElementById('sammelprobe-r').checked ? 'force ' : '';

    const v = document.getElementById('sammelprobe-versuche').value;
    const time = document.getElementById('sammelprobe-zw').value + document.getElementById('sammelprobe-ze').value;
    const e1 = document.getElementById('sammelprobe-e1').value;
    const e2 = document.getElementById('sammelprobe-e2').value;
    const e3 = document.getElementById('sammelprobe-e3').value;
    const fw = document.getElementById('sammelprobe-fw').value;
    const mod = parseInt(document.getElementById('sammelprobe-mod').value) || '';
    const comment = document.getElementById('sammelprobe-kommentar').value;

    document.getElementById('sammelprobe-output').innerText = `!${force}S${v}x${time} ${e1},${e2},${e3}@${fw}${mod} ${comment}`
  });
}

for (let input of document.querySelectorAll("#Schips > div > input")) {
  input.addEventListener("change", () => {
    const dice1 = document.getElementById('schip-1').checked ? 'r' : 'k';
    const dice2 = document.getElementById('schip-2').checked ? 'r' : 'k';
    const dice3 = document.getElementById('schip-3').checked ? 'r' : 'k';
    document.getElementById('schips-output').innerText = `schips ${dice1}${dice2}${dice3}`;
  });
}

document.getElementById('begabung-d').addEventListener(
  'change',
  ev => document.getElementById('begabung-output').innerText = `begabung ${ev.target.value}`
);

document.getElementById('repeat-r').addEventListener(
  'change',
  ev => document.getElementById('repeat-output').innerText = ev.target.checked ? 'retry' : "repeat"
);

for (let input of document.querySelectorAll("#Notiz > div > input")) {
  input.addEventListener("change", () => {
    if (document.getElementById('notiz-delete').checked) {
      document.getElementById('notiz-output').innerText = `delete note ${document.getElementById('notiz-id').value}`;
    } else {
      document.getElementById('notiz-output').innerText =
        `note:${document.getElementById('notiz-id').value}->${document.getElementById('notiz-value').value}`;
    }
  });
}

document.getElementById('wiki-search').addEventListener(
  'change',
  ev => document.getElementById('wiki-output').innerText = `wiki ${ev.target.value}`
);
