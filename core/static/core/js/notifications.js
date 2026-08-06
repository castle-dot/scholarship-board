// Handles both dropdowns in the nav: the notification bell and the
// account/avatar menu. Clicking one closes the other. Clicking outside
// either one closes whichever is open.
document.addEventListener("click", function (event) {
  toggleDropdown(event, "notif-bell", "notif-dropdown", ".bell-btn");
  toggleDropdown(event, "account-menu", "account-dropdown", ".account-btn");
});

function toggleDropdown(event, wrapperId, dropdownId, triggerSelector) {
  const wrapper = document.getElementById(wrapperId);
  const dropdown = document.getElementById(dropdownId);
  if (!wrapper || !dropdown) return; // not on this page / not logged in, that's fine

  const trigger = wrapper.querySelector(triggerSelector);
  const clickedInside = wrapper.contains(event.target);
  const isOpen = dropdown.style.display === "block";

  if (clickedInside) {
    dropdown.style.display = isOpen ? "none" : "block";
    if (trigger) trigger.setAttribute("aria-expanded", String(!isOpen));
  } else {
    dropdown.style.display = "none";
    if (trigger) trigger.setAttribute("aria-expanded", "false");
  }
}