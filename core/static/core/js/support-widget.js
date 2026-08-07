// Handles the floating support button: opens/closes the popup, and
// copies the account number to the clipboard when its Copy button is clicked.
// This REPLACES copy-account.js — delete that script tag if you added it,
// this file does the same copy job plus the open/close behavior.
document.addEventListener("click", function (event) {
  const fab = document.getElementById("support-fab");
  const popup = document.getElementById("support-popup");
  const closeBtn = document.getElementById("support-close-btn");
  const copyBtn = document.getElementById("copy-account-btn");
  if (!fab || !popup) return;

  const isOpen = popup.style.display === "block";

  if (event.target === fab) {
    popup.style.display = isOpen ? "none" : "block";
    fab.setAttribute("aria-expanded", String(!isOpen));
    return;
  }

  if (event.target === closeBtn) {
    popup.style.display = "none";
    fab.setAttribute("aria-expanded", "false");
    return;
  }

  if (event.target === copyBtn) {
    const accountNumber = document.getElementById("account-number").textContent.trim();
    navigator.clipboard.writeText(accountNumber).then(function () {
      const original = copyBtn.textContent;
      copyBtn.textContent = "Copied!";
      copyBtn.classList.add("copied");
      setTimeout(function () {
        copyBtn.textContent = original;
        copyBtn.classList.remove("copied");
      }, 2000);
    });
    return;
  }

  // clicked outside the popup and outside the button -> close it
  if (isOpen && !popup.contains(event.target) && event.target !== fab) {
    popup.style.display = "none";
    fab.setAttribute("aria-expanded", "false");
  }
});