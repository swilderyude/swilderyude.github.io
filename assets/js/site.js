(() => {
  const list = document.querySelector(".archive-list");
  if (!list) return;

  const raw = list.getAttribute("data-articles");
  if (!raw) return;

  let articles = [];
  try {
    articles = JSON.parse(raw);
  } catch {
    return;
  }

  const render = (tag) => {
    const items = tag ? articles.filter((article) => article.tags.includes(tag)) : articles;
    list.innerHTML = items
      .sort((a, b) => b.date.localeCompare(a.date))
      .map(
        (article) => `
          <li>
            <time>${article.date}</time>
            <a href="${article.url}">${article.title}</a>
            <span>${article.folder || article.category || ""}</span>
          </li>
        `,
      )
      .join("");
  };

  document.querySelectorAll(".tag-filter").forEach((button) => {
    button.addEventListener("click", () => {
      const active = button.classList.contains("active");
      document.querySelectorAll(".tag-filter").forEach((item) => item.classList.remove("active"));
      if (active) {
        render("");
        return;
      }
      button.classList.add("active");
      render(button.dataset.tag || "");
    });
  });

  const params = new URLSearchParams(window.location.search);
  const tag = params.get("tag");
  if (tag) {
    const match = Array.from(document.querySelectorAll(".tag-filter")).find((button) => button.dataset.tag === tag);
    if (match) {
      match.classList.add("active");
      render(tag);
    }
  }
})();

(() => {
  const openHashFolder = () => {
    if (!window.location.hash) return;
    const id = decodeURIComponent(window.location.hash.slice(1));
    const target = document.getElementById(id);
    if (!target || target.tagName !== "DETAILS") return;

    let current = target;
    while (current) {
      if (current.tagName === "DETAILS") current.open = true;
      current = current.parentElement ? current.parentElement.closest("details") : null;
    }
    target.scrollIntoView({ block: "start" });
  };

  window.addEventListener("hashchange", openHashFolder);
  openHashFolder();
})();
