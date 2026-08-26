/* Logika aplikasi Belajar Operasi Ortopedi (SPA sederhana, tanpa framework). */

const STORAGE_KEY = "ortho_app_progress_v1";

function loadProgress() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) throw new Error("empty");
    return JSON.parse(raw);
  } catch (e) {
    return { viewedProcedures: [], quizHistory: [], flashcardKnown: [] };
  }
}

function saveProgress(progress) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
}

let progress = loadProgress();

function markProcedureViewed(id) {
  if (!progress.viewedProcedures.includes(id)) {
    progress.viewedProcedures.push(id);
    saveProgress(progress);
  }
}

function recordQuizAttempt(entry) {
  progress.quizHistory.unshift(entry);
  progress.quizHistory = progress.quizHistory.slice(0, 30);
  saveProgress(progress);
}

function toggleFlashcardKnown(id) {
  const idx = progress.flashcardKnown.indexOf(id);
  if (idx >= 0) progress.flashcardKnown.splice(idx, 1);
  else progress.flashcardKnown.push(id);
  saveProgress(progress);
}

/* ---------------- Router ---------------- */
const appEl = document.getElementById("app");

const routes = {
  home: renderHome,
  procedures: renderProcedureList,
  "procedure-detail": renderProcedureDetail,
  quiz: renderQuizSetup,
  flashcards: renderFlashcards,
  glossary: renderGlossary,
  progress: renderProgressPage,
};

let currentRoute = { name: "home", params: {} };

function navigate(name, params = {}) {
  currentRoute = { name, params };
  window.scrollTo(0, 0);
  render();
  updateActiveNav();
  closeMobileSidebar();
}

function render() {
  const fn = routes[currentRoute.name] || renderHome;
  appEl.innerHTML = "";
  fn(currentRoute.params);
}

function updateActiveNav() {
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.route === currentRoute.name);
  });
}

/* ---------------- Helpers ---------------- */
function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([key, val]) => {
    if (key === "class") node.className = val;
    else if (key === "html") node.innerHTML = val;
    else if (key.startsWith("on") && typeof val === "function") {
      node.addEventListener(key.substring(2).toLowerCase(), val);
    } else {
      node.setAttribute(key, val);
    }
  });
  (Array.isArray(children) ? children : [children]).forEach((child) => {
    if (child === null || child === undefined) return;
    if (typeof child === "string") node.appendChild(document.createTextNode(child));
    else node.appendChild(child);
  });
  return node;
}

function findCategory(id) {
  return ORTHO_DATA.categories.find((c) => c.id === id);
}

function findProcedure(id) {
  return ORTHO_DATA.procedures.find((p) => p.id === id);
}

function proceduresInCategory(catId) {
  return ORTHO_DATA.procedures.filter((p) => p.category === catId);
}

/* ---------------- Home / Dashboard ---------------- */
function renderHome() {
  const totalProc = ORTHO_DATA.procedures.length;
  const viewed = progress.viewedProcedures.length;
  const quizCount = progress.quizHistory.length;
  const bestScore = progress.quizHistory.reduce((max, h) => Math.max(max, h.pct), 0);

  const header = el("div", { class: "page-header" }, [
    el("h1", {}, "Belajar Operasi Ortopedi"),
    el("p", {}, "Pelajari prinsip, indikasi, langkah operasi, dan komplikasi dari berbagai tindakan bedah ortopedi. Uji pemahamanmu lewat kuis dan flashcard."),
  ]);

  const stats = el("div", { class: "stats-row" }, [
    statTile(totalProc, "Total Prosedur"),
    statTile(viewed, "Prosedur Dipelajari"),
    statTile(quizCount, "Kuis Dikerjakan"),
    statTile(bestScore ? bestScore + "%" : "-", "Skor Terbaik"),
  ]);

  const catHeader = el("h2", { style: "margin: 26px 0 14px; font-size:1.15rem;" }, "Kategori Operasi");
  const grid = el("div", { class: "grid" });
  ORTHO_DATA.categories.forEach((cat) => {
    const count = proceduresInCategory(cat.id).length;
    const card = el(
      "div",
      { class: "card", onclick: () => navigate("procedures", { category: cat.id }) },
      [
        el("div", { class: "icon" }, cat.ikon),
        el("h3", {}, cat.nama),
        el("p", {}, cat.deskripsi),
        el("span", { class: "badge" }, count + " prosedur"),
      ]
    );
    grid.appendChild(card);
  });

  const quickActions = el("div", { style: "margin-top:30px; display:flex; gap:12px; flex-wrap:wrap;" }, [
    el("button", { class: "btn", onclick: () => navigate("quiz") }, "🧠 Mulai Kuis"),
    el("button", { class: "btn secondary", onclick: () => navigate("flashcards") }, "🗂️ Flashcard Istilah"),
    el("button", { class: "btn secondary", onclick: () => navigate("glossary") }, "📖 Buka Glosarium"),
  ]);

  appEl.append(header, stats, catHeader, grid, quickActions);
}

function statTile(value, label) {
  return el("div", { class: "stat-tile" }, [
    el("div", { class: "value" }, String(value)),
    el("div", { class: "label" }, label),
  ]);
}

/* ---------------- Procedure list ---------------- */
function renderProcedureList(params) {
  const catId = params.category;
  const cat = findCategory(catId);
  const list = cat ? proceduresInCategory(catId) : ORTHO_DATA.procedures;

  appEl.appendChild(
    el("button", { class: "back-link", onclick: () => navigate("home") }, "← Kembali ke Beranda")
  );

  appEl.appendChild(
    el("div", { class: "page-header" }, [
      el("h1", {}, cat ? `${cat.ikon} ${cat.nama}` : "Semua Prosedur"),
      el("p", {}, cat ? cat.deskripsi : "Daftar seluruh prosedur operasi ortopedi yang tersedia."),
    ])
  );

  const chipRow = el("div", { class: "chip-row" });
  chipRow.appendChild(
    el("div", { class: "chip" + (!catId ? " active" : ""), onclick: () => navigate("procedures", {}) }, "Semua")
  );
  ORTHO_DATA.categories.forEach((c) => {
    chipRow.appendChild(
      el(
        "div",
        { class: "chip" + (catId === c.id ? " active" : ""), onclick: () => navigate("procedures", { category: c.id }) },
        c.ikon + " " + c.nama
      )
    );
  });
  appEl.appendChild(chipRow);

  const grid = el("div", { class: "grid" });
  list.forEach((proc) => {
    const isDone = progress.viewedProcedures.includes(proc.id);
    grid.appendChild(
      el("div", { class: "card", onclick: () => navigate("procedure-detail", { id: proc.id }) }, [
        el("h3", {}, proc.nama),
        el("p", {}, proc.definisi.slice(0, 110) + (proc.definisi.length > 110 ? "…" : "")),
        el("span", { class: "badge" + (isDone ? " done" : "") }, isDone ? "✓ Sudah dipelajari" : "Belum dipelajari"),
      ])
    );
  });
  appEl.appendChild(grid);
}

/* ---------------- Procedure detail ---------------- */
function renderProcedureDetail(params) {
  const proc = findProcedure(params.id);
  if (!proc) {
    appEl.appendChild(el("div", { class: "empty-state" }, "Prosedur tidak ditemukan."));
    return;
  }
  markProcedureViewed(proc.id);
  const cat = findCategory(proc.category);

  appEl.appendChild(
    el("button", { class: "back-link", onclick: () => navigate("procedures", { category: proc.category }) }, "← Kembali ke " + (cat ? cat.nama : "Daftar"))
  );

  appEl.appendChild(
    el("div", { class: "detail-header" }, [
      el("div", {}, [
        el("h1", {}, proc.nama),
        el("div", { class: "subtitle" }, proc.singkatan || ""),
      ]),
      el("span", { class: "pill" }, cat ? cat.ikon + " " + cat.nama : ""),
    ])
  );

  appEl.appendChild(
    el("div", { class: "section-block definisi" }, [
      el("h2", {}, "📘 Definisi"),
      el("p", {}, proc.definisi),
    ])
  );

  const twoCol = el("div", { class: "two-col" });
  twoCol.appendChild(sectionList("✅ Indikasi", proc.indikasi, "ul"));
  twoCol.appendChild(sectionList("⛔ Kontraindikasi", proc.kontraindikasi, "ul"));
  appEl.appendChild(twoCol);

  appEl.appendChild(sectionList("🧰 Persiapan Pra-operasi", proc.persiapan, "ul"));
  appEl.appendChild(sectionList("🩺 Langkah-langkah Operasi", proc.langkahOperasi, "ol"));

  const twoCol2 = el("div", { class: "two-col" });
  twoCol2.appendChild(sectionList("🔧 Instrumen Kunci", proc.instrumenKunci, "ul"));
  twoCol2.appendChild(sectionList("⚠️ Komplikasi", proc.komplikasi, "ul"));
  appEl.appendChild(twoCol2);

  appEl.appendChild(sectionList("💡 Tips Klinis", proc.tipsKlinis, "ul"));

  const relatedQuiz = ORTHO_DATA.quiz.filter((q) => q.kategori === proc.category);
  if (relatedQuiz.length) {
    appEl.appendChild(
      el("div", { style: "margin-top: 10px;" }, [
        el("button", {
          class: "btn",
          onclick: () => navigate("quiz", { autoCategory: proc.category }),
        }, "🧠 Uji Pemahaman: Kuis " + (cat ? cat.nama : "")),
      ])
    );
  }
}

function sectionList(title, items, listTag) {
  const list = el(listTag, {});
  (items || []).forEach((item) => list.appendChild(el("li", {}, item)));
  return el("div", { class: "section-block" }, [el("h2", {}, title), list]);
}

/* ---------------- Quiz ---------------- */
let quizState = null;

function renderQuizSetup(params) {
  appEl.appendChild(
    el("div", { class: "page-header" }, [
      el("h1", {}, "🧠 Kuis Ortopedi"),
      el("p", {}, "Pilih kategori dan jumlah soal untuk menguji pemahamanmu."),
    ])
  );

  const selectedCats = new Set(params.autoCategory ? [params.autoCategory] : ORTHO_DATA.categories.map((c) => c.id));

  const grid = el("div", { class: "quiz-setup-grid" });
  ORTHO_DATA.categories.forEach((cat) => {
    const count = ORTHO_DATA.quiz.filter((q) => q.kategori === cat.id).length;
    const checkbox = el("input", { type: "checkbox" });
    checkbox.checked = selectedCats.has(cat.id);
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) selectedCats.add(cat.id);
      else selectedCats.delete(cat.id);
    });
    const card = el("label", { class: "check-card" }, [
      checkbox,
      el("span", {}, `${cat.ikon} ${cat.nama} (${count})`),
    ]);
    grid.appendChild(card);
  });
  appEl.appendChild(grid);

  const startBtn = el("button", { class: "btn" }, "Mulai Kuis");
  startBtn.addEventListener("click", () => {
    const pool = ORTHO_DATA.quiz.filter((q) => selectedCats.has(q.kategori));
    if (!pool.length) return;
    startQuiz(shuffle(pool));
  });
  appEl.appendChild(el("div", {}, startBtn));
}

function shuffle(arr) {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function startQuiz(questions) {
  quizState = {
    questions,
    index: 0,
    answers: [], // { selected, correct }
  };
  renderQuizQuestion();
}

function renderQuizQuestion() {
  appEl.innerHTML = "";
  const { questions, index } = quizState;
  const q = questions[index];
  const pct = Math.round((index / questions.length) * 100);

  appEl.appendChild(
    el("div", { class: "quiz-progress-bar" }, [el("div", { class: "quiz-progress-fill", style: `width:${pct}%` })])
  );

  const card = el("div", { class: "question-card" });
  card.appendChild(el("div", { class: "qnum" }, `Soal ${index + 1} dari ${questions.length}`));
  card.appendChild(el("h2", {}, q.pertanyaan));

  const optionsWrap = el("div", {});
  let answered = false;

  q.opsi.forEach((opsi, i) => {
    const btn = el("button", { class: "option-btn" }, opsi);
    btn.addEventListener("click", () => {
      if (answered) return;
      answered = true;
      const isCorrect = i === q.jawaban;
      quizState.answers[index] = { selected: i, correct: isCorrect };
      Array.from(optionsWrap.children).forEach((child, ci) => {
        child.disabled = true;
        if (ci === q.jawaban) child.classList.add("correct");
        else if (ci === i) child.classList.add("incorrect");
      });
      const explBox = el("div", { class: "explanation-box" }, (isCorrect ? "✅ Benar! " : "❌ Kurang tepat. ") + q.penjelasan);
      card.appendChild(explBox);
      nextBtn.disabled = false;
    });
    optionsWrap.appendChild(btn);
  });
  card.appendChild(optionsWrap);

  const actions = el("div", { class: "quiz-actions" });
  const nextBtn = el("button", { class: "btn" }, index === questions.length - 1 ? "Lihat Hasil" : "Soal Berikutnya");
  nextBtn.disabled = true;
  nextBtn.addEventListener("click", () => {
    if (index === questions.length - 1) {
      finishQuiz();
    } else {
      quizState.index += 1;
      renderQuizQuestion();
    }
  });
  actions.appendChild(nextBtn);
  card.appendChild(actions);

  appEl.appendChild(card);
}

function finishQuiz() {
  const { questions, answers } = quizState;
  const correctCount = answers.filter((a) => a && a.correct).length;
  const pct = Math.round((correctCount / questions.length) * 100);

  recordQuizAttempt({
    date: new Date().toISOString(),
    total: questions.length,
    correct: correctCount,
    pct,
  });

  appEl.innerHTML = "";
  const summary = el("div", { class: "result-summary" }, [
    el("div", { class: "score" }, pct + "%"),
    el("p", {}, `Kamu menjawab benar ${correctCount} dari ${questions.length} soal.`),
    el("div", { style: "display:flex; gap:10px; justify-content:center; margin-top:16px;" }, [
      el("button", { class: "btn", onclick: () => navigate("quiz") }, "Kuis Baru"),
      el("button", { class: "btn secondary", onclick: () => navigate("home") }, "Kembali ke Beranda"),
    ]),
  ]);
  appEl.appendChild(summary);

  appEl.appendChild(el("h2", { style: "margin: 26px 0 14px;" }, "Tinjau Jawaban"));
  questions.forEach((q, i) => {
    const ans = answers[i];
    const wasCorrect = ans && ans.correct;
    const item = el("div", { class: "review-item" }, [
      el("span", { class: "status " + (wasCorrect ? "ok" : "bad") }, wasCorrect ? "Benar" : "Salah"),
      el("div", { class: "q" }, `${i + 1}. ${q.pertanyaan}`),
      el("div", { style: "color: var(--text-dim); font-size:0.9rem;" }, [
        el("div", {}, "Jawaban benar: " + q.opsi[q.jawaban]),
        ans && !wasCorrect ? el("div", {}, "Jawabanmu: " + q.opsi[ans.selected]) : null,
        el("div", { style: "margin-top:6px;" }, q.penjelasan),
      ]),
    ]);
    appEl.appendChild(item);
  });
}

/* ---------------- Flashcards ---------------- */
let flashcardState = { deck: [], index: 0, flipped: false };

function renderFlashcards() {
  appEl.innerHTML = "";
  if (!flashcardState.deck.length) {
    flashcardState.deck = shuffle(ORTHO_DATA.glossary);
    flashcardState.index = 0;
    flashcardState.flipped = false;
  }

  appEl.appendChild(
    el("div", { class: "page-header" }, [
      el("h1", {}, "🗂️ Flashcard Istilah Ortopedi"),
      el("p", {}, "Klik kartu untuk membalik dan melihat definisinya. Tandai sudah hafal untuk melacak progres."),
    ])
  );

  const item = flashcardState.deck[flashcardState.index];
  const known = progress.flashcardKnown.includes(item.istilah);

  const wrap = el("div", { class: "flashcard-wrap" });

  const card = el("div", { class: "flashcard" + (flashcardState.flipped ? " flipped" : "") });
  const inner = el("div", { class: "flashcard-inner" }, [
    el("div", { class: "flashcard-face front" }, item.istilah),
    el("div", { class: "flashcard-face back" }, item.definisi),
  ]);
  card.appendChild(inner);
  card.addEventListener("click", () => {
    flashcardState.flipped = !flashcardState.flipped;
    renderFlashcards();
  });
  wrap.appendChild(card);

  wrap.appendChild(el("div", { class: "flashcard-counter" }, `Kartu ${flashcardState.index + 1} dari ${flashcardState.deck.length} · ${progress.flashcardKnown.length} sudah dihafal`));

  const controls = el("div", { class: "flashcard-controls" }, [
    el("button", { class: "btn secondary", onclick: () => stepFlashcard(-1) }, "← Sebelumnya"),
    el("button", { class: "btn " + (known ? "secondary" : "") , onclick: () => { toggleFlashcardKnown(item.istilah); renderFlashcards(); } }, known ? "✓ Sudah Hafal" : "Tandai Hafal"),
    el("button", { class: "btn secondary", onclick: () => stepFlashcard(1) }, "Selanjutnya →"),
  ]);
  wrap.appendChild(controls);

  const shuffleBtn = el("button", { class: "btn secondary", style: "margin-top:10px;", onclick: () => {
    flashcardState.deck = shuffle(ORTHO_DATA.glossary);
    flashcardState.index = 0;
    flashcardState.flipped = false;
    renderFlashcards();
  }}, "🔀 Acak Ulang");
  wrap.appendChild(shuffleBtn);

  appEl.appendChild(wrap);
}

function stepFlashcard(dir) {
  const len = flashcardState.deck.length;
  flashcardState.index = (flashcardState.index + dir + len) % len;
  flashcardState.flipped = false;
  renderFlashcards();
}

/* ---------------- Glossary ---------------- */
function renderGlossary() {
  appEl.appendChild(
    el("div", { class: "page-header" }, [
      el("h1", {}, "📖 Glosarium Istilah Ortopedi"),
      el("p", {}, "Cari istilah bedah ortopedi yang sering digunakan."),
    ])
  );

  const searchInput = el("input", { class: "search-box", type: "text", placeholder: "Cari istilah… (mis. reduksi, varus)" });
  appEl.appendChild(searchInput);

  const listWrap = el("dl", { id: "glossary-list" });
  appEl.appendChild(listWrap);

  function renderList(filter) {
    listWrap.innerHTML = "";
    const f = filter.trim().toLowerCase();
    const items = ORTHO_DATA.glossary
      .filter((g) => !f || g.istilah.toLowerCase().includes(f) || g.definisi.toLowerCase().includes(f))
      .sort((a, b) => a.istilah.localeCompare(b.istilah));
    if (!items.length) {
      listWrap.appendChild(el("div", { class: "empty-state" }, "Tidak ada istilah yang cocok."));
      return;
    }
    items.forEach((g) => {
      listWrap.appendChild(
        el("div", { class: "glossary-item" }, [el("dt", {}, g.istilah), el("dd", {}, g.definisi)])
      );
    });
  }

  searchInput.addEventListener("input", () => renderList(searchInput.value));
  renderList("");
}

/* ---------------- Progress Page ---------------- */
function renderProgressPage() {
  appEl.appendChild(
    el("div", { class: "page-header" }, [
      el("h1", {}, "📊 Progres Belajar"),
      el("p", {}, "Ringkasan pembelajaranmu tersimpan otomatis di perangkat ini."),
    ])
  );

  appEl.appendChild(el("h2", { style: "font-size:1.05rem; margin-bottom: 10px;" }, "Prosedur per Kategori"));
  ORTHO_DATA.categories.forEach((cat) => {
    const procs = proceduresInCategory(cat.id);
    const viewedInCat = procs.filter((p) => progress.viewedProcedures.includes(p.id)).length;
    const pct = procs.length ? Math.round((viewedInCat / procs.length) * 100) : 0;
    appEl.appendChild(
      el("div", { class: "progress-bar-row" }, [
        el("div", { class: "label" }, `${cat.ikon} ${cat.nama}`),
        el("div", { class: "progress-track" }, [el("div", { class: "progress-fill", style: `width:${pct}%` })]),
        el("div", { class: "progress-pct" }, pct + "%"),
      ])
    );
  });

  appEl.appendChild(el("h2", { style: "font-size:1.05rem; margin: 26px 0 10px;" }, `Flashcard Dihafal (${progress.flashcardKnown.length}/${ORTHO_DATA.glossary.length})`));
  const fcPct = Math.round((progress.flashcardKnown.length / ORTHO_DATA.glossary.length) * 100);
  appEl.appendChild(
    el("div", { class: "progress-bar-row" }, [
      el("div", { class: "label" }, "🗂️ Istilah"),
      el("div", { class: "progress-track" }, [el("div", { class: "progress-fill", style: `width:${fcPct}%` })]),
      el("div", { class: "progress-pct" }, fcPct + "%"),
    ])
  );

  appEl.appendChild(el("h2", { style: "font-size:1.05rem; margin: 26px 0 10px;" }, "Riwayat Kuis Terakhir"));
  if (!progress.quizHistory.length) {
    appEl.appendChild(el("div", { class: "empty-state" }, "Belum ada riwayat kuis. Yuk mulai kuis pertamamu!"));
  } else {
    const table = el("table", { class: "history-table" });
    const thead = el("tr", {}, [el("th", {}, "Tanggal"), el("th", {}, "Skor"), el("th", {}, "Benar/Total")]);
    table.appendChild(thead);
    progress.quizHistory.forEach((h) => {
      const date = new Date(h.date);
      table.appendChild(
        el("tr", {}, [
          el("td", {}, date.toLocaleString("id-ID")),
          el("td", {}, h.pct + "%"),
          el("td", {}, `${h.correct}/${h.total}`),
        ])
      );
    });
    appEl.appendChild(table);
  }

  const resetBtn = el("button", { class: "btn secondary", style: "margin-top:24px;" }, "Reset Semua Progres");
  resetBtn.addEventListener("click", () => {
    if (confirm("Yakin ingin menghapus seluruh progres belajar di perangkat ini?")) {
      progress = { viewedProcedures: [], quizHistory: [], flashcardKnown: [] };
      saveProgress(progress);
      renderProgressPage.__reset = true;
      navigate("progress");
    }
  });
  appEl.appendChild(resetBtn);
}

/* ---------------- Sidebar / Mobile nav ---------------- */
function closeMobileSidebar() {
  document.getElementById("sidebar").classList.remove("open");
  document.getElementById("sidebar-overlay").classList.remove("show");
}

function initNav() {
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.addEventListener("click", () => navigate(btn.dataset.route));
  });

  const menuBtn = document.getElementById("mobile-menu-btn");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  menuBtn.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    overlay.classList.toggle("show");
  });
  overlay.addEventListener("click", closeMobileSidebar);
}

document.addEventListener("DOMContentLoaded", () => {
  initNav();
  navigate("home");
});
