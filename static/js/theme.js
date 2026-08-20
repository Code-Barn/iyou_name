(function () {
  const KEY = "name_theme";
  const html = document.documentElement;
  const btn = document.getElementById("theme-toggle");
  const iconSun = document.getElementById("icon-sun");
  const iconMoon = document.getElementById("icon-moon");

  function setCookie(name, value, days = 365) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = name + "=" + encodeURIComponent(value) + "; expires=" + expires + "; path=/; SameSite=Lax";
  }

  function apply(theme) {
    if (theme === "dark" || theme === "stealth") {
      html.classList.add("dark");
      if (iconSun) iconSun.classList.remove("hidden");
      if (iconMoon) iconMoon.classList.add("hidden");
    } else {
      html.classList.remove("dark");
      if (iconSun) iconSun.classList.add("hidden");
      if (iconMoon) iconMoon.classList.remove("hidden");
    }
  }

  var cookieMatch = document.cookie.match(/(?:^|; )name_theme=([^;]*)/);
  var saved = cookieMatch ? decodeURIComponent(cookieMatch[1]) : (localStorage.getItem(KEY) || "light");
  apply(saved);

  if (btn) {
    btn.addEventListener("click", function () {
      var isDark = html.classList.contains("dark");
      var next = isDark ? "light" : "dark";
      localStorage.setItem(KEY, next);
      setCookie(KEY, next);
      apply(next);
    });
  }
})();
