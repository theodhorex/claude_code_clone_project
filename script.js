const chat = document.querySelector("#chat");
const composer = document.querySelector("#composer");
const promptInput = document.querySelector("#prompt");
const contextList = document.querySelector("#context-list");

const initialMessages = [
  {
    role: "assistant",
    content:
      "Halo! Ini prototype awal cloningan Claude Code. Coba gunakan /help atau jelaskan task coding yang ingin kamu kerjakan.",
  },
];

const commands = {
  "/help":
    "Command tersedia:\n/help\n/add <path>\n/plan\n/run\n/clear",
  "/plan":
    "Rencana awal:\n1. Tentukan UI/CLI\n2. Tambahkan integrasi model AI\n3. Sambungkan project context\n4. Tambahkan runner untuk command coding",
  "/run":
    "Simulasi validasi:\n- struktur project terdeteksi\n- context file aktif\n- prototype siap dikembangkan ke backend AI",
};

function renderMessage(role, content) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  article.textContent = content;
  chat.appendChild(article);
  chat.scrollTop = chat.scrollHeight;
}

function resetChat() {
  chat.innerHTML = "";
  initialMessages.forEach((message) =>
    renderMessage(message.role, message.content),
  );
}

function addContextFile(path) {
  const item = document.createElement("li");
  item.textContent = path;
  contextList.appendChild(item);
}

function buildAssistantReply(input) {
  const value = input.trim();

  if (!value) {
    return "Tolong isi prompt terlebih dahulu.";
  }

  if (value === "/clear") {
    resetChat();
    return null;
  }

  if (value.startsWith("/add ")) {
    const path = value.slice(5).trim();

    if (!path) {
      return "Format benar: /add <path>";
    }

    addContextFile(path);
    return `Context baru ditambahkan: ${path}`;
  }

  if (commands[value]) {
    return commands[value];
  }

  return `Saya memahami kamu ingin membuat cloningan Claude Code untuk kebutuhan coding.\n\nTask terdeteksi:\n- ${value}\n\nSaran langkah berikutnya:\n1. Pecah kebutuhan menjadi modul chat, context file, dan executor command\n2. Hubungkan UI ini ke backend model AI\n3. Tambahkan integrasi baca file project agar assistant lebih kontekstual`;
}

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  const input = promptInput.value.trim();

  renderMessage("user", input || "(prompt kosong)");

  const reply = buildAssistantReply(input);
  if (reply) {
    renderMessage("assistant", reply);
  }

  promptInput.value = "";
  promptInput.focus();
});

resetChat();
