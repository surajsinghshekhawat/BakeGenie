// This file contains shared JavaScript functionality for the Baking AI application

document.addEventListener("DOMContentLoaded", () => {
  // Mobile navigation toggle
  const navToggle = document.querySelector(".nav-toggle");
  const navMenu = document.querySelector(".nav-menu");

  if (navToggle && navMenu) {
    navToggle.addEventListener("click", () => {
      navMenu.classList.toggle("active");
      navToggle.classList.toggle("active");
    });
  }

  // Close mobile menu when clicking on a nav link
  const navLinks = document.querySelectorAll(".nav-link");
  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      if (navMenu.classList.contains("active")) {
        navMenu.classList.remove("active");
        navToggle.classList.remove("active");
      }
    });
  });

  // Add smooth scroll behavior
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });

  // Add animation to all cards on scroll
  const cards = document.querySelectorAll(
    ".feature-card, .recipe-card, .step, .tip-card"
  );
  if (cards.length > 0) {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: "0px 0px -50px 0px",
    };

    const cardObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("fade-in");
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    cards.forEach((card) => {
      card.style.opacity = 0;
      cardObserver.observe(card);
    });
  }

  // Add animation to headings on scroll
  const headings = document.querySelectorAll("h1, h2, h3");
  if (headings.length > 0) {
    const headingObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("slide-up");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 }
    );

    headings.forEach((heading) => {
      heading.style.opacity = 0;
      heading.style.transform = "translateY(20px)";
      heading.style.transition = "opacity 0.6s ease, transform 0.6s ease";
      headingObserver.observe(heading);
    });
  }

  // Add hover effect to buttons
  const buttons = document.querySelectorAll(".btn");
  buttons.forEach((button) => {
    button.addEventListener("mouseenter", () => {
      button.style.transform = "translateY(-2px)";
    });
    button.addEventListener("mouseleave", () => {
      button.style.transform = "translateY(0)";
    });
  });

  // Add hover effect to cards
  const allCards = document.querySelectorAll(
    ".feature-card, .recipe-card, .step, .tip-card"
  );
  allCards.forEach((card) => {
    card.addEventListener("mouseenter", () => {
      card.style.transform = "translateY(-5px)";
      card.style.boxShadow = "var(--shadow-hover)";
    });
    card.addEventListener("mouseleave", () => {
      card.style.transform = "translateY(0)";
      card.style.boxShadow = "var(--shadow)";
    });
  });

  // Add animation to form elements
  const formElements = document.querySelectorAll("input, select, textarea");
  formElements.forEach((element) => {
    element.addEventListener("focus", () => {
      element.style.transform = "scale(1.02)";
      element.style.boxShadow = "0 0 0 2px var(--primary-color)";
    });
    element.addEventListener("blur", () => {
      element.style.transform = "scale(1)";
      element.style.boxShadow = "none";
    });
  });

  // Add loading animation to buttons with loading state
  const loadingButtons = document.querySelectorAll(".btn-loading");
  loadingButtons.forEach((button) => {
    button.addEventListener("click", () => {
      button.classList.add("loading");
      button.disabled = true;
      setTimeout(() => {
        button.classList.remove("loading");
        button.disabled = false;
      }, 2000);
    });
  });

  // Add smooth page transitions
  document.querySelectorAll("a").forEach((link) => {
    if (link.href && link.href.startsWith(window.location.origin)) {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const target = link.href;
        document.body.classList.add("fade-out");
        setTimeout(() => {
          window.location.href = target;
        }, 300);
      });
    }
  });

  // Add parallax effect to hero section
  const hero = document.querySelector(".hero");
  if (hero) {
    window.addEventListener("scroll", () => {
      const scrolled = window.pageYOffset;
      hero.style.backgroundPositionY = -(scrolled * 0.5) + "px";
    });
  }

  // Initialize any tooltips
  const tooltipTriggerList = document.querySelectorAll(
    '[data-bs-toggle="tooltip"]'
  );
  if (typeof bootstrap !== "undefined" && tooltipTriggerList.length > 0) {
    const tooltipList = [...tooltipTriggerList].map(
      (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
    );
  }
});
