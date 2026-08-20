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

  function updateLogos(isDark) {
    const navbarLogo = document.getElementById("navbar-logo");
    if (navbarLogo) {
      navbarLogo.src = isDark
        ? "/static/core/images/tinynamelogo_DM.png"
        : "/static/core/images/tinynamelogo.png";
    }
    const footerLogo = document.getElementById("footer-logo");
    if (footerLogo) {
      footerLogo.src = isDark
        ? "/static/core/images/tinynamelogo_DM.png"
        : "/static/core/images/tinynamelogo.png";
    }
    const dekalbLogo = document.getElementById("footer-dekalb-logo");
    if (dekalbLogo) {
      dekalbLogo.src = isDark
        ? "/static/core/images/createdinDeKalb_DM.png"
        : "/static/core/images/createdinDeKalb.png";
    }
  }

  function apply(theme) {
    const isDark = theme === "dark" || theme === "stealth";
    if (isDark) {
      html.classList.add("dark");
      if (iconSun) iconSun.classList.remove("hidden");
      if (iconMoon) iconMoon.classList.add("hidden");
    } else {
      html.classList.remove("dark");
      if (iconSun) iconSun.classList.add("hidden");
      if (iconMoon) iconMoon.classList.remove("hidden");
    }
    updateLogos(isDark);
  }

  const cookieMatch = document.cookie.match(/(?:^|; )name_theme=([^;]*)/);
  const saved = cookieMatch ? decodeURIComponent(cookieMatch[1]) : (localStorage.getItem(KEY) || "light");
  apply(saved);

  if (btn) {
    btn.addEventListener("click", function () {
      const isDark = html.classList.contains("dark");
      const next = isDark ? "light" : "dark";
      localStorage.setItem(KEY, next);
      setCookie(KEY, next);
      apply(next);
    });
  }
})();
