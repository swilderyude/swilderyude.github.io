(() => {
  const quotes = [
    "潮平两岸阔，风正一帆悬。",
    "海上生明月，天涯共此时。",
    "长风破浪会有时，直挂云帆济沧海。",
    "行到水穷处，坐看云起时。",
    "春水碧于天，画船听雨眠。",
    "星垂平野阔，月涌大江流。",
    "沧海月明珠有泪，蓝田日暖玉生烟。",
    "醉后不知天在水，满船清梦压星河。",
    "山中何事？松花酿酒，春水煎茶。",
    "疏影横斜水清浅，暗香浮动月黄昏。",
    "溪云初起日沉阁，山雨欲来风满楼。",
    "孤帆远影碧空尽，唯见长江天际流。",
    "青山一道同云雨，明月何曾是两乡。",
    "晚来天欲雪，能饮一杯无。",
    "落霞与孤鹜齐飞，秋水共长天一色。",
  ];

  const dayStart = new Date();
  dayStart.setHours(0, 0, 0, 0);
  const dayIndex = Math.floor(dayStart.getTime() / 86400000) % quotes.length;
  document.querySelectorAll("[data-daily-quote]").forEach((node) => {
    node.textContent = quotes[dayIndex];
  });
})();

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
