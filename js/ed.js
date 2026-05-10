
  const sections = document.querySelectorAll("section");
  const navLinks = document.querySelectorAll(".nav-link");

  const setActive = () => {
    let current = "top";
    sections.forEach(section => {
      const top = section.offsetTop;
      if (window.scrollY >= top - 260) current = section.id;
    });
    navLinks.forEach(link => {
      link.classList.toggle("active", link.getAttribute("href") === "#" + current);
    });
  };
  window.addEventListener("scroll", setActive);
  window.addEventListener("load", setActive);


// Q&A検索
(function(){
  const input = document.getElementById('faqSearch');
  if (!input) return;
  const items = document.querySelectorAll('.faq-item');
  const note = document.querySelector('.faq-search-note');
  const total = items.length;
  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    let visible = 0;
    items.forEach(item => {
      const text = item.textContent.toLowerCase();
      const match = !q || text.includes(q);
      item.classList.toggle('is-hidden', !match);
      if (match) visible++;
    });
    if (note) {
      note.textContent = q
        ? `「${input.value}」の検索結果: ${visible} 問 / 全 ${total} 問`
        : `全 ${total} 問。キーワードで絞り込めます。`;
    }
  });
})();
