const darkModeToggle = document.getElementById('dark-mode-toggle');
const darkModeLabel = darkModeToggle?.querySelector('.dark-mode-label');
const themeIcon = darkModeToggle?.querySelector('.theme-icon');

function setDarkMode(enabled) {
  document.documentElement.classList.toggle('dark', enabled);
  darkModeToggle?.setAttribute('aria-pressed', String(enabled));
  darkModeToggle?.setAttribute('aria-label', enabled ? 'Enable light mode' : 'Enable dark mode');
  if (darkModeLabel) darkModeLabel.textContent = enabled ? 'Light mode' : 'Dark mode';
  if (themeIcon) themeIcon.textContent = enabled ? '☀' : '☾';
}

const savedTheme = localStorage.getItem('theme');
setDarkMode(savedTheme ? savedTheme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches);
darkModeToggle?.addEventListener('click', () => {
  const enabled = !document.documentElement.classList.contains('dark');
  setDarkMode(enabled);
  localStorage.setItem('theme', enabled ? 'dark' : 'light');
});

const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const fileName = document.getElementById('file-name');
function showFile(file) {
  if (!file) return;
  if (file.type && file.type !== 'application/pdf') { fileName.textContent = 'Please select a PDF file.'; return; }
  fileName.textContent = `✓ ${file.name} selected`;
  dropArea?.classList.add('file-selected');
}
fileInput?.addEventListener('change', () => showFile(fileInput.files[0]));
['dragenter', 'dragover'].forEach((eventName) => dropArea?.addEventListener(eventName, (event) => { event.preventDefault(); dropArea.classList.add('drag-active'); }));
['dragleave', 'drop'].forEach((eventName) => dropArea?.addEventListener(eventName, (event) => { event.preventDefault(); dropArea.classList.remove('drag-active'); }));
dropArea?.addEventListener('drop', (event) => {
  const [file] = event.dataTransfer.files;
  if (!file || (file.type && file.type !== 'application/pdf')) { fileName.textContent = 'Please drop a PDF file.'; return; }
  fileInput.files = event.dataTransfer.files;
  showFile(file);
});

function setLoading(formId, buttonId, text) {
  const form = document.getElementById(formId), button = document.getElementById(buttonId);
  form?.addEventListener('submit', () => { button.disabled = true; button.textContent = text; });
}
setLoading('upload-form', 'upload-btn', 'Analyzing your report…');
setLoading('ask-form', 'ask-btn', 'Thinking…');

document.querySelectorAll('.quick-question').forEach((button) => button.addEventListener('click', () => {
  const questionInput = document.getElementById('question-input');
  if (questionInput) { questionInput.value = button.textContent; questionInput.focus(); }
}));
document.getElementById('copy-summary-btn')?.addEventListener('click', async function () {
  const summary = document.getElementById('summary-text')?.innerText || '';
  if (!summary.trim()) return;
  await navigator.clipboard.writeText(summary);
  this.textContent = 'Copied ✓';
  setTimeout(() => { this.textContent = 'Copy summary'; }, 2000);
});
window.addEventListener('load', () => { const chatBox = document.getElementById('chat-box'); if (chatBox) chatBox.scrollTop = chatBox.scrollHeight; });
