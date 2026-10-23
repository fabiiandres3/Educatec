(() => {
  const home = document.querySelector(".educatec-home");
  if (!home) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
  const progressBar = home.querySelector(".home-scroll-progress");
  const hero = home.querySelector(".home-hero");
  const heroVisual = home.querySelector("#hero-visual");
  const heroFloats = home.querySelector("#hero-floats");
  const heroOverlay = home.querySelector("#hero-overlay");
  const heroIntro = home.querySelector(".hero-intro");
  const heroHint = home.querySelector("#hero-scroll-hint");
  const levels = home.querySelector(".home-levels");
  const levelsTrack = home.querySelector("#levels-track");
  const levelsBar = home.querySelector("#levels-progress-bar");
  let mouseX = 0;
  let mouseY = 0;
  let ticking = false;

  function updateScrollEffects() {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    progressBar.style.transform = `scaleX(${scrollable > 0 ? window.scrollY / scrollable : 0})`;

    if (hero && heroFloats) {
      const rect = hero.getBoundingClientRect();
      const range = Math.max(1, rect.height - window.innerHeight);
      const progress = clamp(-rect.top / range);
      const fade = clamp(progress / 0.22);
      heroFloats.style.opacity = String(1 - fade);
      heroFloats.style.filter = `blur(${fade * 10}px)`;
    }

    if (!reducedMotion && hero && heroVisual) {
      const rect = hero.getBoundingClientRect();
      const range = Math.max(1, rect.height - window.innerHeight);
      const progress = clamp(-rect.top / range);
      const zoom = clamp(progress / 0.6);
      heroVisual.style.setProperty("--hero-scale", (0.55 + zoom * 0.45).toFixed(3));
      heroVisual.style.setProperty("--hero-radius", `${48 * (1 - zoom)}px`);
      heroVisual.style.setProperty("--hero-rx", `${mouseY * 6 * (1 - zoom)}deg`);
      heroVisual.style.setProperty("--hero-ry", `${mouseX * 6 * (1 - zoom)}deg`);
      heroOverlay.style.setProperty("--hero-overlay", (clamp((progress - 0.55) / 0.3) * 0.6).toFixed(2));
      heroOverlay.style.setProperty("--hero-blur", `${clamp((progress - 0.55) / 0.3) * 8}px`);
      heroOverlay.style.setProperty("--hero-copy-blur", `${8 * (1 - clamp(progress / 0.55))}px`);
      heroIntro.style.opacity = String(1 - clamp(progress / 0.3));
      heroIntro.style.transform = `translateY(${-200 * clamp(progress / 0.4)}px)`;
      heroHint.style.opacity = String(1 - clamp(progress / 0.18));
    }

    const gallery = home.querySelector(".about-gallery");
    if (gallery && !reducedMotion) {
      const rect = gallery.getBoundingClientRect();
      const progress = clamp((window.innerHeight - rect.top) / (window.innerHeight + rect.height));
      gallery.querySelectorAll("figure").forEach((figure, index) => {
        const offset = index % 2 === 0 ? 100 - 200 * progress : -60 + 120 * progress;
        figure.style.transform = `translateY(${offset}px)`;
      });
    }

    if (levels && levelsTrack) {
      const rect = levels.getBoundingClientRect();
      const range = Math.max(1, rect.height - window.innerHeight);
      const progress = clamp(-rect.top / range);
      levelsTrack.style.transform = `translate3d(${-66.6667 * progress}%,0,0)`;
      levelsBar.style.width = `${progress * 100}%`;
    }
    ticking = false;
  }

  function requestScrollUpdate() {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(updateScrollEffects);
    }
  }

  window.addEventListener("scroll", requestScrollUpdate, { passive: true });
  window.addEventListener("resize", requestScrollUpdate);
  requestScrollUpdate();

  hero?.addEventListener("pointermove", (event) => {
    if (reducedMotion || window.innerWidth < 768) return;
    const rect = hero.getBoundingClientRect();
    mouseX = (event.clientX - rect.left) / rect.width - 0.5;
    mouseY = (event.clientY - rect.top) / rect.height - 0.5;
    requestScrollUpdate();
  });

  const menuButton = home.querySelector(".home-menu-toggle");
  const mobileNav = home.querySelector("#home-mobile-nav");
  menuButton?.addEventListener("click", () => {
    const isOpen = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!isOpen));
    menuButton.setAttribute("aria-label", isOpen ? "Abrir menú" : "Cerrar menú");
    menuButton.innerHTML = `<i class="fa-solid fa-${isOpen ? "bars" : "xmark"}"></i>`;
    mobileNav.hidden = isOpen;
  });
  mobileNav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
    mobileNav.hidden = true;
    menuButton?.setAttribute("aria-expanded", "false");
    menuButton?.setAttribute("aria-label", "Abrir menú");
    if (menuButton) menuButton.innerHTML = '<i class="fa-solid fa-bars"></i>';
  }));

  const words = home.querySelector("#manifesto-text");
  if (words) {
    words.innerHTML = words.textContent.trim().split(/\s+/).map((word) => `<span class="manifesto-word">${word}</span>`).join(" ");
    const wordSpans = [...words.querySelectorAll(".manifesto-word")];
    const updateWords = () => {
      const rect = words.getBoundingClientRect();
      const progress = clamp((window.innerHeight * 0.82 - rect.top) / (rect.height + window.innerHeight * 0.3));
      const litWords = Math.floor(progress * (wordSpans.length + 3));
      wordSpans.forEach((word, index) => { word.style.color = index < litWords ? "#020617" : "#94a3b8"; });
    };
    window.addEventListener("scroll", updateWords, { passive: true });
    updateWords();
  }

  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
  home.querySelectorAll(".reveal, .feature-card, .event-row, .event-card").forEach((element, index) => {
    if ((element.classList.contains("event-row") || element.classList.contains("event-card"))) element.style.transitionDelay = `${index * 0.1}s`;
    revealObserver.observe(element);
  });

  home.querySelectorAll(".tilt-card").forEach((card) => {
    card.addEventListener("pointermove", (event) => {
      if (event.pointerType === "touch") return;
      const rect = card.getBoundingClientRect();
      card.style.setProperty("--pointer-x", `${((event.clientX - rect.left) / rect.width) * 100}%`);
      card.style.setProperty("--pointer-y", `${((event.clientY - rect.top) / rect.height) * 100}%`);
    });
    card.addEventListener("pointerleave", () => {
      card.style.setProperty("--pointer-x", "50%");
      card.style.setProperty("--pointer-y", "50%");
    });
  });

  const carousel = home.querySelector("[data-events-carousel]");
  if (carousel) {
    const viewport = carousel.querySelector("[data-events-viewport]");
    const track = carousel.querySelector("[data-events-track]");
    const cards = [...track.querySelectorAll(".event-card")];
    const previous = carousel.querySelector("[data-events-prev]");
    const next = carousel.querySelector("[data-events-next]");
    const dots = carousel.querySelector("[data-events-dots]");
    const current = carousel.querySelector("[data-events-current]");
    const total = carousel.querySelector("[data-events-total]");
    const formatNumber = (number) => String(number + 1).padStart(2, "0");
    let offset = 0;
    let cardPitch = 0;

    const measureCardPitch = () => {
      if (!track.firstElementChild) return;
      const cardWidth = track.firstElementChild.getBoundingClientRect().width;
      const styles = window.getComputedStyle(track);
      const gap = parseFloat(styles.columnGap || styles.gap) || 0;
      cardPitch = cardWidth + gap;
      if (cardPitch > 0) offset %= cardPitch;
    };
    const getCurrentIndex = () => cards.indexOf(track.firstElementChild);
    const updateIndicators = () => {
      const index = Math.max(0, getCurrentIndex());
      current.textContent = formatNumber(index);
      [...dots.children].forEach((dot, dotIndex) => {
        dot.classList.toggle("is-active", dotIndex === index);
        if (dotIndex === index) dot.setAttribute("aria-current", "true");
        else dot.removeAttribute("aria-current");
      });
    };
    const applyOffset = () => {
      if (cardPitch <= 0) return;
      while (offset >= cardPitch) {
        offset -= cardPitch;
        track.append(track.firstElementChild);
      }
      while (offset < 0) {
        offset += cardPitch;
        track.prepend(track.lastElementChild);
      }
      track.style.transform = "translate3d(" + -offset + "px, 0, 0)";
      updateIndicators();
    };
    const moveByCards = (count) => {
      offset += count * cardPitch;
      applyOffset();
    };

    carousel.classList.toggle("is-single-event", cards.length < 2);
    carousel.classList.toggle("is-two-events", cards.length === 2);
    cards.forEach((card, index) => {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = "events-carousel-dot";
      dot.setAttribute("aria-label", "Mostrar evento " + (index + 1) + " de " + cards.length);
      dot.addEventListener("click", () => {
        const targetPosition = [...track.children].indexOf(cards[index]);
        offset += targetPosition * cardPitch;
        applyOffset();
      });
      dots.append(dot);
    });
    total.textContent = formatNumber(cards.length - 1);

    measureCardPitch();
    updateIndicators();
    previous.addEventListener("click", () => moveByCards(-1));
    next.addEventListener("click", () => moveByCards(1));

    window.addEventListener("resize", () => {
      measureCardPitch();
      applyOffset();
    });

    if (cards.length > 1 && cardPitch > 0) {
      carousel.classList.add("is-autoplaying");
      let previousFrame = 0;
      const pixelsPerSecond = reducedMotion ? 9 : 24;
      const animate = (time) => {
        const elapsed = previousFrame ? Math.min((time - previousFrame) / 1000, 0.05) : 0;
        previousFrame = time;
        offset += pixelsPerSecond * elapsed;
        applyOffset();
        requestAnimationFrame(animate);
      };
      requestAnimationFrame(animate);
    }
  }
})();
