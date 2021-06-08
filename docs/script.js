for (let input of document.querySelectorAll("#Talentprobe input")) {
  input.addEventListener("change", () => {
    const force = document.getElementById("talentprobe-r").checked
      ? "force "
      : "";

    const e1 = document.getElementById("talentprobe-e1").value;
    const e2 = document.getElementById("talentprobe-e2").value;
    const e3 = document.getElementById("talentprobe-e3").value;
    const fw = document.getElementById("talentprobe-fw").value;
    const mod = modToString(document.getElementById("talentprobe-mod").value);
    const modFP =
      modToString(document.getElementById("talentprobe-mod-fp").value) + "FP";
    const comment = document.getElementById("talentprobe-kommentar").value;

    document.getElementById(
      "talentprobe-output"
    ).innerText = `!${force}${e1},${e2},${e3} @ ${fw} ${mod} ${modFP} ${comment}`;
  });
}

const updateSammelprobe = () => {
  const force = document.getElementById("sammelprobe-r").checked
    ? "force "
    : "";

  const v = document.getElementById("sammelprobe-versuche").value;
  const time =
    document.getElementById("sammelprobe-zw").value +
    document.getElementById("sammelprobe-ze").value;
  const e1 = document.getElementById("sammelprobe-e1").value;
  const e2 = document.getElementById("sammelprobe-e2").value;
  const e3 = document.getElementById("sammelprobe-e3").value;
  const fw = document.getElementById("sammelprobe-fw").value;
  const mod = modToString(document.getElementById("sammelprobe-mod").value);
  const modFP =
    modToString(document.getElementById("sammelprobe-mod-fp").value) + "FP";
  const comment = document.getElementById("sammelprobe-kommentar").value;

  document.getElementById(
    "sammelprobe-output"
  ).innerText = `!${force}S${v}x${time} ${e1},${e2},${e3} @ ${fw} ${mod} ${modFP} ${comment}`;
};

for (let input of document.querySelectorAll("#Sammelprobe input")) {
  input.addEventListener("change", updateSammelprobe);
}
document
  .getElementById("sammelprobe-ze")
  .addEventListener("change", updateSammelprobe);

for (let input of document.querySelectorAll("#Schips input")) {
  input.addEventListener("change", () => {
    const dice1 = document.getElementById("schip-1").checked ? "r" : "k";
    const dice2 = document.getElementById("schip-2").checked ? "r" : "k";
    const dice3 = document.getElementById("schip-3").checked ? "r" : "k";
    document.getElementById(
      "schips-output"
    ).innerText = `schips ${dice1}${dice2}${dice3}`;
  });
}

document.getElementById("begabung-select").addEventListener("change", () => {
  const incompetent =
    document.getElementById("begabung-select").value === "incompetent";
  for (let input of document.querySelectorAll("#Begabung input")) {
    input.disabled = incompetent;
  }
  document.getElementById("begabung-output").innerText = incompetent
    ? "unfähig"
    : `begabung ${begabung_selected}`;
});
begabung_selected = 1;
for (let input of document.querySelectorAll("#Begabung input")) {
  input.addEventListener("change", (ev) => {
    const command =
      document.getElementById("begabung-select").value === "incompetent"
        ? "unfähig"
        : `begabung  ${ev.target.value}`;
    begabung_selected = ev.target.value;
    document.getElementById("begabung-output").innerText = command;
  });
}

for (let input of document.querySelectorAll("#Trefferzone input")) {
  input.addEventListener("change", () => {
    let size = "klein";
    if (document.getElementById(`hit-zone-2`).checked) {
      size = "mittel";
    }
    if (document.getElementById(`hit-zone-3`).checked) {
      size = "groß";
    }
    if (document.getElementById(`hit-zone-4`).checked) {
      size = "riesig";
    }
    document.getElementById("hit-zone-output").innerText = `hitzone ${
      document.getElementById("hit-zone-r").checked ? "humanoid" : "kreatur"
    } ${size}`;
  });
}

document
  .getElementById("repeat-r")
  .addEventListener(
    "change",
    (ev) =>
      (document.getElementById("repeat-output").innerText = ev.target.checked
        ? "retry"
        : "repeat")
  );

for (let input of document.querySelectorAll(
  "#Notizen input, #Notizen select"
)) {
  input.addEventListener("change", () => {
    if (document.getElementById("notiz-delete").checked) {
      document.getElementById("notiz-op").disabled = true;
      document.getElementById("notiz-value").disabled = true;
      document.getElementById("notiz-list").disabled = true;
      document.getElementById(
        "notiz-output"
      ).innerText = `delete note ${sanitizeID(
        document.getElementById("notiz-id").value
      )}`;
    } else if (document.getElementById("notiz-list").checked) {
      document.getElementById("notiz-op").disabled = true;
      document.getElementById("notiz-value").disabled = true;
      document.getElementById("notiz-delete").disabled = true;
      document.getElementById("notiz-output").innerText = "notes";
    } else {
      document.getElementById("notiz-op").disabled = false;
      document.getElementById("notiz-value").disabled = false;
      document.getElementById("notiz-list").disabled = false;
      document.getElementById("notiz-delete").disabled = false;
      document.getElementById("notiz-output").innerText = `note:${sanitizeID(
        document.getElementById("notiz-id").value
      )}${document.getElementById("notiz-op").value}${
        document.getElementById("notiz-value").value
      }`;
    }
  });
}

document
  .getElementById("wiki-search")
  .addEventListener(
    "change",
    (ev) =>
      (document.getElementById(
        "wiki-output"
      ).innerText = `wiki ${ev.target.value}`)
  );

function sanitizeID(noteID) {
  return noteID.trim().replaceAll(" ", "_");
}

function modToString(number) {
  if (number > 0) {
    return `+${number.toString()}`;
  }
  if (number < 0) {
    return number.toString();
  }
  return "";
}
