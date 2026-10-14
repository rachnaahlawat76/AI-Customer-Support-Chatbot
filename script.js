const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("send-button");
const resetButton = document.getElementById("reset-button");

function addMessage(text, role) {
  const row = document.createElement("div");
  row.className = `message ${role === "user" ? "user-message" : "bot-message"}`;
  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = role === "user" ? "●" : "✦";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text; // textContent prevents user input from being interpreted as HTML.
  row.append(avatar, bubble);
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
  return row;
}

async function sendMessage(text) {
  const message = text.trim();
  if (!message) return;
  addMessage(message, "user");
  input.value = "";
  sendButton.disabled = true;
  const typing = addMessage("Thinking…", "bot");
  typing.querySelector(".bubble").classList.add("typing");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });
    if (!response.ok) throw new Error("Request failed");
    const data = await response.json();
    typing.querySelector(".bubble").textContent = data.answer;
    typing.querySelector(".bubble").classList.remove("typing");
  } catch (error) {
    typing.querySelector(".bubble").textContent = "Sorry, I couldn’t connect. Please check that the server is running and try again.";
    typing.querySelector(".bubble").classList.remove("typing");
  } finally {
    sendButton.disabled = false;
    input.focus();
    messages.scrollTop = messages.scrollHeight;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(input.value);
});

document.querySelectorAll(".suggestion").forEach((button) => {
  button.addEventListener("click", () => sendMessage(button.dataset.question));
});

resetButton.addEventListener("click", async () => {
  try {
    await fetch("/api/reset", { method: "POST" });
  } finally {
    messages.replaceChildren();
    addMessage("New conversation started! What would you like to know?", "bot");
    input.focus();
  }
});
