/**
 * Lumina Landing & Distribution Interactive Logic
 * Modern Web Best Practices + Accessibility + Zero Third-Party Dependencies
 */

(function () {
  "use strict";

  // --- 1. Theme Scheme Management (Modern Web Guidance) ---
  const metaColorScheme = document.querySelector('meta[name="color-scheme"]');
  const themeToggleBtn = document.getElementById("theme-toggle");
  const themeIconSun = document.getElementById("theme-icon-sun");
  const themeIconMoon = document.getElementById("theme-icon-moon");

  function getSystemScheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function getActiveScheme() {
    const meta = metaColorScheme ? metaColorScheme.getAttribute("content") : "light dark";
    if (meta === "dark" || meta === "light") {
      return meta;
    }
    return getSystemScheme();
  }

  function updateThemeUI(active) {
    if (!themeToggleBtn) return;
    const isDark = active === "dark";
    if (themeIconSun && themeIconMoon) {
      themeIconSun.style.display = isDark ? "block" : "none";
      themeIconMoon.style.display = isDark ? "none" : "block";
    }
    themeToggleBtn.setAttribute(
      "aria-label",
      isDark ? "Switch to light theme" : "Switch to dark theme"
    );
  }

  if (themeToggleBtn && metaColorScheme) {
    updateThemeUI(getActiveScheme());

    themeToggleBtn.addEventListener("click", function () {
      const current = getActiveScheme();
      const target = current === "dark" ? "light" : "dark";
      const sys = getSystemScheme();

      if (target === sys) {
        // Reverting to system preference
        try {
          localStorage.removeItem("color-scheme");
        } catch (e) {}
        metaColorScheme.setAttribute("content", "light dark");
      } else {
        // Explicit override
        try {
          localStorage.setItem("color-scheme", target);
        } catch (e) {}
        metaColorScheme.setAttribute("content", target);
      }
      updateThemeUI(target);
    });

    // Listen for OS scheme changes
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
      try {
        const stored = localStorage.getItem("color-scheme");
        if (!stored) {
          updateThemeUI(getSystemScheme());
        }
      } catch (e) {}
    });

    // Sync across tabs
    window.addEventListener("storage", function (e) {
      if (e.key === "color-scheme") {
        const newTheme = e.newValue ?? "light dark";
        metaColorScheme.setAttribute("content", newTheme);
        updateThemeUI(getActiveScheme());
      }
    });
  }

  // --- 2. Interactive Before / After Slider ---
  const compareOverlay = document.getElementById("compare-overlay");
  const compareDivider = document.getElementById("compare-divider");
  const compareSlider = document.getElementById("compare-slider");
  const comparePercent = document.getElementById("compare-percent");

  function updateComparison(val) {
    if (!compareOverlay || !compareDivider) return;
    const clamped = Math.max(0, Math.min(100, val));
    compareOverlay.style.clipPath = `polygon(0 0, ${clamped}% 0, ${clamped}% 100%, 0 100%)`;
    compareDivider.style.left = `${clamped}%`;
    if (comparePercent) {
      comparePercent.textContent = `%${Math.round(clamped)}`;
    }
  }

  if (compareSlider) {
    compareSlider.addEventListener("input", function (e) {
      updateComparison(e.target.value);
    });
  }

  // Pointer drag on compare container
  const compareContainer = document.getElementById("compare-container");
  if (compareContainer && compareSlider) {
    let isDragging = false;

    function handlePointer(clientX) {
      const rect = compareContainer.getBoundingClientRect();
      const pos = ((clientX - rect.left) / rect.width) * 100;
      const clamped = Math.max(0, Math.min(100, pos));
      compareSlider.value = clamped;
      updateComparison(clamped);
    }

    compareContainer.addEventListener("pointerdown", function (e) {
      isDragging = true;
      compareContainer.setPointerCapture(e.pointerId);
      handlePointer(e.clientX);
    });

    compareContainer.addEventListener("pointermove", function (e) {
      if (isDragging) {
        handlePointer(e.clientX);
      }
    });

    function endDrag(e) {
      if (isDragging) {
        isDragging = false;
        try {
          compareContainer.releasePointerCapture(e.pointerId);
        } catch (err) {}
      }
    }

    compareContainer.addEventListener("pointerup", endDrag);
    compareContainer.addEventListener("pointercancel", endDrag);
  }

  // --- 3. Clipboard Copy for CLI Command ---
  const copyButtons = document.querySelectorAll(".btn-copy-command");
  const toast = document.getElementById("copy-toast");

  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("show");
    setTimeout(function () {
      toast.classList.remove("show");
    }, 2400);
  }

  copyButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const textToCopy = btn.getAttribute("data-clipboard-text");
      if (!textToCopy) return;

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textToCopy).then(
          function () {
            showToast("Command copied to clipboard!");
          },
          function () {
            fallbackCopy(textToCopy);
          }
        );
      } else {
        fallbackCopy(textToCopy);
      }
    });
  });

  function fallbackCopy(text) {
    const input = document.createElement("textarea");
    input.value = text;
    input.style.position = "fixed";
    input.style.opacity = "0";
    document.body.appendChild(input);
    input.focus();
    input.select();
    try {
      document.execCommand("copy");
      showToast("Command copied to clipboard!");
    } catch (e) {
      showToast("Could not copy, please copy manually.");
    }
    document.body.removeChild(input);
  }
})();
