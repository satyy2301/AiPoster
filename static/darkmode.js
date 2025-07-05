// Toggle and persist dark mode
function toggleDarkMode() {
  console.log('Toggling dark mode'); // Debug line
  document.body.classList.toggle('dark-mode');
  const isDark = document.body.classList.contains('dark-mode');
  localStorage.setItem('darkMode', isDark);
  console.log('Dark mode:', isDark); // Debug line
}

// Initialize dark mode on page load
function initDarkMode() {
  const darkMode = localStorage.getItem('darkMode') === 'true';
  console.log('Initial dark mode:', darkMode); // Debug line
  if (darkMode) {
    document.body.classList.add('dark-mode');
  }
}

// Make functions available globally
window.toggleDarkMode = toggleDarkMode;
window.initDarkMode = initDarkMode;

// Initialize
document.addEventListener('DOMContentLoaded', initDarkMode);