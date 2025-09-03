// ---------- Menu Toggle ----------
function setupMenuToggle() {
  const menuBtn = document.getElementById("menu-btn");
  const closeBtn = document.getElementById("close-btn");
  const mobileMenu = document.getElementById("mobile-menu");

  if (menuBtn && closeBtn && mobileMenu) {
    menuBtn.addEventListener("click", () => {
      mobileMenu.classList.remove("-translate-y-full");
    });

    closeBtn.addEventListener("click", () => {
      mobileMenu.classList.add("-translate-y-full");
    });
  }
}

// ---------- Modal Functions ----------
function openModal(id) {
  document.getElementById(id)?.classList.remove("hidden");
}

function closeModal(id) {
  document.getElementById(id)?.classList.add("hidden");
}

// ---------- Random Memory Fetch ----------
async function fetchRandomMemory() {
  try {
    const res = await fetch("/random_memory");
    const data = await res.json();
    alert("🎲 Random Memory: " + data.memory);
  } catch (err) {
    console.error("Error fetching random memory:", err);
    alert("⚠️ Could not fetch a random memory. Try again.");
  }
}

// ---------- Form Validation + Counter ----------
function setupFormValidation() {
  const details = document.getElementById("details");
  const counter = document.getElementById("details-count");
  const form = document.getElementById("log-memory-form");

  if (details && counter) {
    details.addEventListener("input", () => {
      counter.textContent = details.value.length;
    });
  }

  if (form && details) {
    form.addEventListener("submit", (e) => {
      if (details.value.length < 10) {
        e.preventDefault();
        alert("Please write at least 10 characters in details.");
      }
    });
  }
}

// ---------- Search Results Clear ----------
function setupClearResults() {
  const clearBtn = document.getElementById("clearBtn");

  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      // Clear search box
      const searchBox = document.querySelector("input[name='query']");
      if (searchBox) searchBox.value = "";

      // Remove results list if exists
      const resultsList = document.getElementById("resultsList");
      if (resultsList) resultsList.remove();

      // Hide "no results" message if it exists
      const noResultsMsg = document.getElementById("noResultsMsg");
      if (noResultsMsg) noResultsMsg.remove();

      // Remove Clear button itself
      clearBtn.remove();
    });
  }
}

// ---------- Initialize Everything ----------
document.addEventListener("DOMContentLoaded", () => {
  setupMenuToggle();
  setupFormValidation();
  setupClearResults();
});

