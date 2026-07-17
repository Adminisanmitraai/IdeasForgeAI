const MAX_FILES = 5;
const MAX_FILE_BYTES = 10 * 1024 * 1024;

const ALLOWED_TYPES = new Set([
  "image/png",
  "image/jpeg",
  "image/webp",
  "image/gif",
  "text/plain",
  "text/markdown",
  "text/csv",
  "application/json",
]);

const PREVIEW_ID = "if-chat-attachment-preview";

let pendingFiles: File[] = [];
let initialized = false;
let previewUrls = new Map<File, string>();

function showAttachmentNotice(message: string): void {
  window.dispatchEvent(
    new CustomEvent("ideasforge:attachment-notice", {
      detail: { message },
    }),
  );

  console.info(`[IdeasForgeAI attachments] ${message}`);
}

function normalizedMimeType(file: File): string {
  if (file.type) {
    return file.type.toLowerCase();
  }

  const filename = file.name.toLowerCase();

  if (filename.endsWith(".md")) {
    return "text/markdown";
  }

  if (filename.endsWith(".csv")) {
    return "text/csv";
  }

  if (filename.endsWith(".json")) {
    return "application/json";
  }

  if (filename.endsWith(".txt")) {
    return "text/plain";
  }

  return "application/octet-stream";
}

function fileKey(file: File): string {
  return [
    file.name,
    file.size,
    file.lastModified,
    normalizedMimeType(file),
  ].join(":");
}

function validateFile(file: File): string | null {
  if (file.size <= 0) {
    return `${file.name} is empty.`;
  }

  if (file.size > MAX_FILE_BYTES) {
    return `${file.name} exceeds the 10 MB limit.`;
  }

  const mimeType = normalizedMimeType(file);

  if (!ALLOWED_TYPES.has(mimeType)) {
    return `${file.name} is not a supported attachment type.`;
  }

  return null;
}

function formatSize(size: number): string {
  if (size < 1024) {
    return `${size} B`;
  }

  if (size < 1024 * 1024) {
    return `${Math.round(size / 1024)} KB`;
  }

  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function clearPreviewUrls(): void {
  for (const url of previewUrls.values()) {
    URL.revokeObjectURL(url);
  }

  previewUrls.clear();
}

function findComposer(): HTMLFormElement | null {
  return (
    document.querySelector<HTMLFormElement>("#chat-composer") ??
    document.querySelector<HTMLFormElement>("#composer") ??
    document.querySelector<HTMLFormElement>("form.composer")
  );
}

function renderPreview(): void {
  const composer = findComposer();
  const existing = document.getElementById(PREVIEW_ID);

  if (!composer) {
    existing?.remove();
    return;
  }

  if (pendingFiles.length === 0) {
    existing?.remove();
    clearPreviewUrls();
    composer.classList.remove("if-composer-has-attachments");
    return;
  }

  composer.classList.add("if-composer-has-attachments");

  const container =
    existing ?? document.createElement("div");

  container.id = PREVIEW_ID;
  container.className = "if-chat-attachments";
  container.setAttribute(
    "aria-label",
    "Pending chat attachments",
  );

  container.innerHTML = "";

  for (const file of pendingFiles) {
    const item = document.createElement("div");
    item.className = "if-chat-attachment";

    const mimeType = normalizedMimeType(file);

    if (mimeType.startsWith("image/")) {
      const image = document.createElement("img");
      image.className = "if-chat-attachment__image";
      image.alt = "";

      let url = previewUrls.get(file);

      if (!url) {
        url = URL.createObjectURL(file);
        previewUrls.set(file, url);
      }

      image.src = url;
      item.appendChild(image);
    } else {
      const icon = document.createElement("div");
      icon.className = "if-chat-attachment__file-icon";
      icon.textContent = "FILE";
      item.appendChild(icon);
    }

    const information = document.createElement("div");
    information.className =
      "if-chat-attachment__information";

    const name = document.createElement("span");
    name.className = "if-chat-attachment__name";
    name.textContent = file.name;

    const metadata = document.createElement("span");
    metadata.className = "if-chat-attachment__metadata";
    metadata.textContent = formatSize(file.size);

    information.append(name, metadata);
    item.appendChild(information);

    const removeButton =
      document.createElement("button");

    removeButton.type = "button";
    removeButton.className =
      "if-chat-attachment__remove";
    removeButton.setAttribute(
      "aria-label",
      `Remove ${file.name}`,
    );
    removeButton.textContent = "×";

    removeButton.addEventListener("click", () => {
      removePendingFile(file);
    });

    item.appendChild(removeButton);
    container.appendChild(item);
  }

  if (!existing) {
    composer.prepend(container);
  }
}

function addFiles(files: readonly File[]): void {
  const existingKeys = new Set(
    pendingFiles.map(fileKey),
  );

  const accepted: File[] = [];

  for (const file of files) {
    const validationError = validateFile(file);

    if (validationError) {
      showAttachmentNotice(validationError);
      continue;
    }

    if (existingKeys.has(fileKey(file))) {
      continue;
    }

    if (
      pendingFiles.length + accepted.length >= MAX_FILES
    ) {
      showAttachmentNotice(
        `A maximum of ${MAX_FILES} files can be attached.`,
      );
      break;
    }

    existingKeys.add(fileKey(file));
    accepted.push(file);
  }

  if (accepted.length === 0) {
    return;
  }

  pendingFiles = [...pendingFiles, ...accepted];
  renderPreview();
}

function removePendingFile(file: File): void {
  pendingFiles = pendingFiles.filter(
    candidate => candidate !== file,
  );

  const previewUrl = previewUrls.get(file);

  if (previewUrl) {
    URL.revokeObjectURL(previewUrl);
    previewUrls.delete(file);
  }

  renderPreview();
}

function handleSelectedEvent(event: Event): void {
  const customEvent =
    event as CustomEvent<{ files?: File[] }>;

  const files = customEvent.detail?.files;

  if (!Array.isArray(files)) {
    return;
  }

  addFiles(files);
}

function handleFileInputChange(event: Event): void {
  const target = event.target;

  if (!(target instanceof HTMLInputElement)) {
    return;
  }

  if (target.type !== "file" || !target.files) {
    return;
  }

  addFiles(Array.from(target.files));

  // Browsers allow clearing a file input.
  target.value = "";
}

function handlePaste(event: ClipboardEvent): void {
  const clipboardFiles = Array.from(
    event.clipboardData?.files ?? [],
  );

  const itemFiles = Array.from(
    event.clipboardData?.items ?? [],
  )
    .filter(item => item.kind === "file")
    .map(item => item.getAsFile())
    .filter((file): file is File => file !== null);

  const files =
    clipboardFiles.length > 0
      ? clipboardFiles
      : itemFiles;

  if (files.length === 0) {
    return;
  }

  event.preventDefault();
  addFiles(files);
}

function observeComposer(): void {
  const observer = new MutationObserver(() => {
    renderPreview();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}

export function initializeAttachmentController(): void {
  if (initialized) {
    return;
  }

  initialized = true;

  window.addEventListener(
    "ideasforge:files-selected",
    handleSelectedEvent,
  );

  document.addEventListener(
    "change",
    handleFileInputChange,
  );

  document.addEventListener("paste", handlePaste);

  observeComposer();
  renderPreview();
}

export function getPendingAttachments(): readonly File[] {
  return [...pendingFiles];
}

export function clearPendingAttachments(): void {
  pendingFiles = [];
  renderPreview();
}