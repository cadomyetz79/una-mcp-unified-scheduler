"use strict";

// Load an approved, unmodified university Roaring Lion asset ONLY if it has
// been installed locally. This never contacts an external image server, and
// the research-safe geometric lion remains the fallback without the asset.
(() => {
  const prefix = window.location.pathname.startsWith("/chat/interactive")
    ? "/chat/interactive-assets/"
    : "/chat/assets/";
  const official = new Image();
  official.addEventListener("load", () => {
    if (official.naturalWidth < 100 || official.naturalHeight < 100) return;
    for (const lion of document.querySelectorAll("[data-brand-lion]")) {
      lion.src = prefix + "una-roaring-lion.png";
      lion.closest(".brand-mark")?.classList.add("official-mark");
    }
    const favicon = document.querySelector('link[rel="icon"]');
    if (favicon) {
      favicon.href = prefix + "una-roaring-lion.png";
      favicon.type = "image/png";
    }
  }, { once: true });
  official.src = prefix + "una-roaring-lion.png";
})();
