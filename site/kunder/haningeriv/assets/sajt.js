(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Headern blir vit när man scrollat förbi toppen
  const mast = $('.masthead');
  if (mast && !document.body.classList.contains('no-hero')) {
    const upd = () => mast.classList.toggle('solid', scrollY > 40);
    addEventListener('scroll', upd, { passive: true });
    upd();
  }

  // Mobilmeny
  const menuBtn = $('.menu-btn');
  if (menuBtn) {
    menuBtn.addEventListener('click', () => {
      const open = document.body.classList.toggle('menu-open');
      menuBtn.setAttribute('aria-expanded', open);
    });
    $$('.nav a').forEach(a => a.addEventListener('click', () => {
      document.body.classList.remove('menu-open');
      menuBtn.setAttribute('aria-expanded', 'false');
    }));
  }

  // Bildspel i heron
  const slides = $$('.hero-slides img');
  const dots = $$('.hero-dots button');
  if (slides.length > 1) {
    let i = 0, timer;
    const show = n => {
      slides[i].classList.remove('on'); dots[i]?.setAttribute('aria-current', 'false');
      i = (n + slides.length) % slides.length;
      slides[i].classList.add('on'); dots[i]?.setAttribute('aria-current', 'true');
    };
    const start = () => { if (!reduce) timer = setInterval(() => show(i + 1), 7000); };
    dots.forEach((d, k) => d.addEventListener('click', () => { clearInterval(timer); show(k); start(); }));
    start();
    document.addEventListener('visibilitychange', () => { clearInterval(timer); if (!document.hidden) start(); });
  }

  // Tjänstekarusell på startsidan: pilknappar
  const car = $('.svc-car');
  const carBtns = $$('.car-btns button');
  if (car && carBtns.length) {
    const step = () => ($('.svc-card', car)?.offsetWidth || 340) + 16;
    const upd = () => {
      carBtns[0].disabled = car.scrollLeft < 4;
      carBtns[1].disabled = car.scrollLeft + car.clientWidth >= car.scrollWidth - 4;
    };
    carBtns.forEach(b => b.addEventListener('click', () => car.scrollBy({ left: +b.dataset.d * step(), behavior: reduce ? 'auto' : 'smooth' })));
    car.addEventListener('scroll', upd, { passive: true });
    addEventListener('resize', upd);
    upd();
  }

  // Tjänstemeny: markera aktiv sektion
  const svcLinks = $$('.svc-nav a');
  if (svcLinks.length && 'IntersectionObserver' in window) {
    const map = new Map(svcLinks.map(a => [a.getAttribute('href').slice(1), a]));
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return;
      svcLinks.forEach(a => a.classList.remove('on'));
      const a = map.get(e.target.id);
      if (a) { a.classList.add('on'); a.scrollIntoView({ block: 'nearest', inline: 'center' }); }
    }), { rootMargin: '-45% 0px -50% 0px' });
    map.forEach((_, id) => { const el = document.getElementById(id); if (el) io.observe(el); });
  }

  // Galleri: filter + bildvisning
  const gallery = $('.gallery');
  if (gallery) {
    const figs = $$('figure', gallery);
    $$('.filters button').forEach(b => b.addEventListener('click', () => {
      $$('.filters button').forEach(x => x.setAttribute('aria-pressed', x === b));
      figs.forEach(f => { f.hidden = b.dataset.f !== 'alla' && f.dataset.cat !== b.dataset.f; });
    }));
    const lb = $('.lightbox'), lbImg = $('img', lb), lbTxt = $('p', lb);
    let cur = 0, last = null;
    const visible = () => figs.filter(f => !f.hidden);
    const open = fig => {
      cur = visible().indexOf(fig);
      const img = $('img', fig);
      lbImg.src = img.dataset.full || img.src; lbImg.alt = img.alt;
      lbTxt.textContent = $('figcaption', fig)?.textContent || '';
      lb.classList.add('open'); document.body.style.overflow = 'hidden';
      $('.lb-close', lb).focus();
    };
    const close = () => { lb.classList.remove('open'); document.body.style.overflow = ''; last?.focus(); };
    const go = d => { const v = visible(); open(v[(cur + d + v.length) % v.length]); };
    figs.forEach(f => {
      f.tabIndex = 0; f.setAttribute('role', 'button');
      f.addEventListener('click', () => { last = f; open(f); });
      f.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); last = f; open(f); } });
    });
    $('.lb-close', lb).addEventListener('click', close);
    $('.lb-prev', lb).addEventListener('click', () => go(-1));
    $('.lb-next', lb).addEventListener('click', () => go(1));
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    document.addEventListener('keydown', e => {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') go(-1);
      if (e.key === 'ArrowRight') go(1);
    });
  }

  // Formulär: öppnar e-postprogrammet med meddelandet ifyllt.
  // Byt mot en formulärtjänst när sajten går live.
  $$('form[data-mail]').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const d = new FormData(form);
      const rows = [];
      for (const [k, v] of d.entries()) if (k !== 'samtycke' && String(v).trim()) rows.push(k + ': ' + v);
      const subject = form.dataset.subject + (d.get('Namn') ? ' – ' + d.get('Namn') : '');
      location.href = 'mailto:' + form.dataset.mail + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(rows.join('\n'));
      $('.form-ok', form)?.classList.add('show');
    });
  });

  $$('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
})();
