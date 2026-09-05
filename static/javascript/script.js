console.log("Script Loaded Successfully");
const darkModeToggle = document.getElementById("dark-mode-toggle");
const darkModeLabel = darkModeToggle?.querySelector(".dark-mode-label");

function setDarkMode(enabled) {
    document.documentElement.classList.add("theme-switching");
    document.documentElement.classList.toggle("dark", enabled);
    darkModeToggle?.setAttribute("aria-pressed", String(enabled));
    darkModeToggle?.setAttribute("aria-label", enabled ? "Enable light mode" : "Enable dark mode");

    if (darkModeLabel) {
        darkModeLabel.textContent = enabled ? "Light mode" : "Dark mode";
    }

    setTimeout(() => {
        document.documentElement.classList.remove("theme-switching");
    }, 350);
}

const savedTheme = localStorage.getItem("theme");
const useDarkMode = savedTheme ? savedTheme === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
setDarkMode(useDarkMode);

darkModeToggle?.addEventListener("click", () => {
    const enabled = !document.documentElement.classList.contains("dark");
    setDarkMode(enabled);
    localStorage.setItem("theme", enabled ? "dark" : "light");
});

const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("file-input");
const fileName = document.getElementById("file-name");

// Click on box
dropArea.addEventListener("click", () => {
    fileInput.click();
});

// Show selected file name
fileInput.addEventListener("change", () => {

    if (fileInput.files.length > 0) {

        fileName.innerHTML = `
        ✅ <span class="font-semibold">
        ${fileInput.files[0].name}
        </span>
        <br>
        <span class="text-green-600">
        File Selected Successfully
        </span>
        `;

        dropArea.classList.remove("border-blue-300");

        dropArea.classList.add(
            "border-green-500",
            "bg-green-50"
        );

    }

});

// Drag Over
dropArea.addEventListener("dragover", (e) => {

    e.preventDefault();

    dropArea.classList.add("border-blue-600", "bg-blue-100");

});

// Drag Leave
dropArea.addEventListener("dragleave", () => {

    dropArea.classList.remove("border-blue-600", "bg-blue-100");

});

// Drop File
dropArea.addEventListener("drop", (e) => {

    e.preventDefault();

    dropArea.classList.remove("border-blue-600", "bg-blue-100");

    fileInput.files = e.dataTransfer.files;

    fileName.innerHTML = `
✅ <span class="font-semibold">
${e.dataTransfer.files[0].name}
</span>

<br>

<span class="text-green-600">
File Selected Successfully
</span>
`;

    dropArea.classList.remove("border-blue-300");

    dropArea.classList.add(
        "border-green-500",
        "bg-green-50"
    );

});
//analysis btn loading design
const uploadForm = document.getElementById("upload-form");
const uploadBtn = document.getElementById("upload-btn");

uploadForm.addEventListener("submit", () => {

    uploadBtn.innerHTML = "⏳ Analyzing...";

    uploadBtn.disabled = true;

});
//ask btn loading design
const askForm = document.getElementById("ask-form");
const askBtn = document.getElementById("ask-btn");

askForm.addEventListener("submit", () => {

    askBtn.innerHTML = "⏳ AI is Thinking...";

    askBtn.disabled = true;

});
// Scroll to bottom of chat box on page load
window.addEventListener("load", function () {

    const chatBox = document.getElementById("chat-box");

    if (chatBox) {

        chatBox.scrollIntoView({
            behavior: "smooth",
            block: "end"
        });

        chatBox.scrollTop = chatBox.scrollHeight;
    }

});
const copySummaryBtn = document.getElementById("copy-summary-btn");

if (copySummaryBtn) {

    copySummaryBtn.addEventListener("click", function () {

        const summary = document.getElementById("summary-text").innerText;

        navigator.clipboard.writeText(summary);

        this.innerHTML = "✅ Copied";

        setTimeout(() => {

            this.innerHTML = "📋 Copy Summary";

        }, 2000);

    });

}
