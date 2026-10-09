const mount = document.querySelector("[data-news-timeline]");

if (mount) {
  const searchInput = document.querySelector("[data-news-search]");
  const tagSelect = document.querySelector("[data-news-tag]");
  const status = document.querySelector("[data-news-status]");
  const embeddedData = document.querySelector("#foxlab-news-data");

  const embeddedNews = () => {
    if (!embeddedData) {
      throw new Error("No embedded news data found.");
    }
    return JSON.parse(embeddedData.textContent);
  };

  const loadNews = fetch("../data/news.json")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`News data request failed: ${response.status}`);
      }
      return response.json();
    })
    .catch(() => embeddedNews());

  loadNews
    .then((items) => {
      const tags = [...new Set(items.flatMap((item) => item.tags || []))].sort();
      tags.forEach((tag) => {
        const option = document.createElement("option");
        option.value = tag;
        option.textContent = tag;
        tagSelect.append(option);
      });

      const render = () => {
        const query = searchInput.value.trim().toLowerCase();
        const tag = tagSelect.value;
        const filtered = items.filter((item) => {
          const haystack = [
            item.date,
            item.title,
            item.summary,
            item.details,
            ...(item.tags || [])
          ].join(" ").toLowerCase();
          const matchesQuery = !query || haystack.includes(query);
          const matchesTag = !tag || (item.tags || []).includes(tag);
          return matchesQuery && matchesTag;
        });

        mount.innerHTML = "";
        status.textContent = `${filtered.length} update${filtered.length === 1 ? "" : "s"}`;

        filtered.forEach((item, index) => {
          const article = document.createElement("article");
          article.className = "timeline-item";

          const button = document.createElement("button");
          button.className = "timeline-summary";
          button.type = "button";
          button.setAttribute("aria-expanded", "false");
          button.innerHTML = `
            <time>${item.date}</time>
            <h3>${item.title}</h3>
            <p>${item.summary}</p>
            <div class="tag-list">${(item.tags || []).map((itemTag) => `<span>${itemTag}</span>`).join("")}</div>
          `;

          const detail = document.createElement("div");
          detail.className = "timeline-detail";
          const links = (item.links || []).map((link) => `<p><a href="${link.href}">${link.label}</a></p>`).join("");
          const gallery = (item.images || []).length
            ? `<div class="timeline-gallery">${item.images.map((src) => `<img src="${src}" alt="">`).join("")}</div>`
            : "";
          detail.innerHTML = `<p>${item.details}</p>${links}${gallery}`;

          button.addEventListener("click", () => {
            const isOpen = article.classList.toggle("is-open");
            button.setAttribute("aria-expanded", String(isOpen));
          });

          article.append(button, detail);
          mount.append(article);

          if (index === 0 && !query && !tag) {
            article.classList.add("is-open");
            button.setAttribute("aria-expanded", "true");
          }
        });
      };

      searchInput.addEventListener("input", render);
      tagSelect.addEventListener("change", render);
      render();
    })
    .catch((error) => {
      status.textContent = "Lab news could not be loaded.";
      console.error("Unable to load Fox Lab news timeline", error);
    });
}
