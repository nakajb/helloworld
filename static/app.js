let selectedTone = "formal";

document.querySelectorAll(".tone-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tone-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    selectedTone = btn.dataset.tone;
  });
});

document.getElementById("generate-btn").addEventListener("click", async () => {
  const jobDesc = document.getElementById("job-description").value.trim();
  if (!jobDesc) {
    showError("Please paste a job description before generating.");
    return;
  }

  setLoading(true);
  hideError();

  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_description: jobDesc, tone: selectedTone }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Generation failed. Please try again.");
    }

    document.getElementById("cover-letter-output").value = data.cover_letter;
    document.getElementById("copy-btn").disabled = false;
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
});

document.getElementById("copy-btn").addEventListener("click", async () => {
  const text = document.getElementById("cover-letter-output").value;
  const btn = document.getElementById("copy-btn");

  try {
    await navigator.clipboard.writeText(text);
  } catch {
    // Fallback for non-secure contexts
    const el = document.getElementById("cover-letter-output");
    el.select();
    document.execCommand("copy");
  }

  btn.textContent = "Copied!";
  setTimeout(() => {
    btn.textContent = "Copy to Clipboard";
  }, 2000);
});

function setLoading(isLoading) {
  const btn = document.getElementById("generate-btn");
  const btnText = btn.querySelector(".btn-text");
  const spinner = btn.querySelector(".btn-spinner");
  btn.disabled = isLoading;
  btnText.hidden = isLoading;
  spinner.hidden = !isLoading;
}

function showError(msg) {
  const el = document.getElementById("error-message");
  el.textContent = msg;
  el.hidden = false;
}

function hideError() {
  document.getElementById("error-message").hidden = true;
}
