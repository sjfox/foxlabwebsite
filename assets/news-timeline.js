(() => {
  const timeline = document.querySelector('#news-timeline');
  if (!timeline) return;
  const search = document.querySelector('#news-search');
  const topic = document.querySelector('#news-tag');
  const status = document.querySelector('#news-status');
  const items = Array.from(timeline.querySelectorAll('.timeline-item'));
  timeline.classList.add('news-enhanced');
  document.querySelector('.timeline-tools').hidden = false;

  function filter() {
    const query = search.value.trim().toLowerCase();
    let count = 0;
    items.forEach((item) => {
      item.hidden = !(item.dataset.search.includes(query) &&
        (!topic.value || item.dataset.tags.split('|').includes(topic.value)));
      if (!item.hidden) count += 1;
    });
    status.textContent = count ? `${count} update${count === 1 ? '' : 's'}` :
      'No updates match your search. Try another search or choose All topics.';
  }

  function openLinkedItem() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const item = items.find((entry) => entry.id === id);
    if (!item) return;
    search.value = '';
    topic.value = '';
    filter();
    item.classList.add('is-open');
    item.querySelector('.timeline-summary').setAttribute('aria-expanded', 'true');
    item.scrollIntoView({ block: 'start' });
  }

  items.forEach((item) => {
    const button = item.querySelector('.timeline-summary');
    button.setAttribute('aria-expanded', String(item.classList.contains('is-open')));
    button.addEventListener('click', () => {
      const open = item.classList.toggle('is-open');
      button.setAttribute('aria-expanded', String(open));
    });
  });
  search.addEventListener('input', filter);
  topic.addEventListener('change', filter);
  window.addEventListener('hashchange', openLinkedItem);
  filter();
  openLinkedItem();
})();
