document.addEventListener('DOMContentLoaded', () => {
  const revealItems = document.querySelectorAll('.edc-reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -35px 0px' });
    revealItems.forEach(item => observer.observe(item));
  } else {
    revealItems.forEach(item => item.classList.add('is-visible'));
  }

  // Event rows open on click; only one stays open at a time.
  document.querySelectorAll('.edc-event-trigger').forEach(trigger => {
    trigger.addEventListener('click', () => {
      const item = trigger.closest('.edc-event-item');
      const willOpen = !item.classList.contains('is-open');
      document.querySelectorAll('.edc-event-item.is-open').forEach(openItem => {
        openItem.classList.remove('is-open');
        const openTrigger = openItem.querySelector('.edc-event-trigger');
        if (openTrigger) openTrigger.setAttribute('aria-expanded', 'false');
      });
      if (willOpen) {
        item.classList.add('is-open');
        trigger.setAttribute('aria-expanded', 'true');
      }
    });
  });

  // On small screens, arrows move the educational-level carousel.
  const levels = document.querySelector('.edc-levels');
  const next = document.getElementById('levelNext');
  const prev = document.getElementById('levelPrev');
  const moveLevel = direction => {
    if (!levels) return;
    const card = levels.querySelector('.edc-level-card');
    const gap = 14;
    const amount = card ? card.getBoundingClientRect().width + gap : 300;
    levels.scrollBy({ left: amount * direction, behavior: 'smooth' });
  };
  if (next) next.addEventListener('click', () => moveLevel(1));
  if (prev) prev.addEventListener('click', () => moveLevel(-1));

  // Smooth anchor movement, respecting reduced-motion preferences.
  document.querySelectorAll('.edc-home a[href^="#"]').forEach(link => {
    link.addEventListener('click', event => {
      const id = link.getAttribute('href');
      const target = id && document.querySelector(id);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    });
  });
});
