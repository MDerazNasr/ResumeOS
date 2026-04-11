export const THEME_STORAGE_KEY = "resumeos.themeMode";

export function inlineThemeScript() {
  return `
    (function () {
      try {
        var storedTheme = window.localStorage.getItem("${THEME_STORAGE_KEY}");
        if (storedTheme === "light" || storedTheme === "dark") {
          document.documentElement.dataset.theme = storedTheme;
        }
      } catch (error) {}
    })();
  `;
}
