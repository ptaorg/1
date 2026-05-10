
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
