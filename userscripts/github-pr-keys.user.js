// ==UserScript==
// @name         GitHub PR keys (GitLab-style v/j/k/o)
// @namespace    sprin.dotfiles
// @version      0.4.0
// @description  v = mark current file Viewed and jump to next, j/k = next/prev file, o = expand/collapse current file, Ctrl-D/U = half page, Ctrl-F/B = full page, Cmd-Shift-Enter x2 = approve review
// @match        https://github.com/*/pull/*
// @updateURL    https://raw.githubusercontent.com/ChiTienHsieh/dotfiles/main/userscripts/github-pr-keys.user.js
// @downloadURL  https://raw.githubusercontent.com/ChiTienHsieh/dotfiles/main/userscripts/github-pr-keys.user.js
// @run-at       document-idle
// @grant        none
// ==/UserScript==
(function () {
  'use strict';
  const TOP_OFFSET = 70; // px hidden under the sticky header; tune if the file header lands under the toolbar

  // Both the classic /files page and the new /changes page anchor each file as id="diff-<64 hex>".
  // Line anchors are "diff-<hash>L12", so the exact-length regex keeps only file containers.
  const files = () =>
    Array.from(document.querySelectorAll('[id^="diff-"]')).filter(
      (el) => /^diff-[0-9a-f]{64}$/.test(el.id) && el.getBoundingClientRect().height > 0,
    );

  const currentIndex = () => {
    const list = files();
    let idx = 0;
    for (let i = 0; i < list.length; i++) {
      if (list[i].getBoundingClientRect().top - TOP_OFFSET <= 1) idx = i;
      else break;
    }
    return { list, idx };
  };

  const scrollTo = (el) => {
    if (!el) return;
    window.scrollTo({ top: window.scrollY + el.getBoundingClientRect().top - TOP_OFFSET, behavior: 'instant' });
  };

  // Marking a file Viewed makes GitHub collapse it asynchronously, which shifts the layout after our
  // scroll. Re-scroll to the same element a few times while the page settles.
  const settleScroll = (el) => {
    scrollTo(el);
    requestAnimationFrame(() => scrollTo(el));
    [100, 250, 500].forEach((ms) => setTimeout(() => scrollTo(el), ms));
  };

  const viewedControl = (file) => {
    // classic UI
    const cb = file.querySelector('input.js-reviewed-checkbox');
    if (cb) return cb;
    // new UI: a button/label whose own text is "Viewed", or anything aria-labelled viewed
    const byAria = file.querySelector('[aria-label*="viewed" i]');
    if (byAria) return byAria;
    return Array.from(file.querySelectorAll('button, label')).find(
      (b) => b.textContent.trim().toLowerCase() === 'viewed',
    );
  };

  const toggleControl = (file) => Array.from(file.querySelectorAll('button')).find((button) => {
    const label = button.getAttribute('aria-label') ||
      (button.getAttribute('aria-labelledby') || '').split(/\s+/)
        .map((id) => document.getElementById(id)?.textContent || '').join(' ');
    return /^(Expand|Collapse) file$/.test(label.trim());
  });

  const typing = (e) => {
    const t = e.target;
    return (
      t.isContentEditable ||
      /^(input|textarea|select)$/i.test(t.tagName) ||
      e.metaKey || e.altKey
    );
  };

  // vim-style paging: Ctrl-D/U half page, Ctrl-F/B full page
  const PAGE = { d: 0.5, u: -0.5, f: 0.9, b: -0.9 };

  // ⌘⇧Enter twice = Approve. Press 1 opens the review dialog and selects Approve; press 2 submits.
  // A single press never submits, and press 2 only submits when Approve is already selected.
  // Text-based lookups so both the classic Files changed page and the new /changes page work.
  const buttonByText = (root, re) =>
    Array.from(root.querySelectorAll('button')).find((b) => re.test(b.textContent.trim()));
  const reviewDialog = () =>
    Array.from(document.querySelectorAll('[role="dialog"], form.js-reviews-container, .js-reviews-container')).find(
      (d) => d.getBoundingClientRect().height > 0 && /finish your review|submit review/i.test(d.textContent),
    );
  const approveRadio = (dialog) =>
    dialog.querySelector('input[type="radio"][value="approve" i]') ||
    Array.from(dialog.querySelectorAll('input[type="radio"]')).find((r) => {
      const label = r.labels?.[0] || r.closest('label') || dialog.querySelector(`label[for="${r.id}"]`);
      return /^approve\b/i.test((label?.textContent || '').trim());
    });
  const selectApprove = (dialog) => {
    const radio = approveRadio(dialog);
    if (radio && !radio.checked) (radio.labels?.[0] || radio).click();
    dialog.querySelector('textarea')?.focus();
  };
  const approveReview = () => {
    const dialog = reviewDialog();
    if (!dialog) {
      const opener = buttonByText(document, /^submit review/i);
      if (!opener) return;
      opener.click();
      let tries = 0;
      const waitForDialog = () => {
        const d = reviewDialog();
        if (d) selectApprove(d);
        else if (tries++ < 40) setTimeout(waitForDialog, 50);
      };
      setTimeout(waitForDialog, 50);
      return;
    }
    const radio = approveRadio(dialog);
    if (!radio?.checked) {
      selectApprove(dialog);
      return;
    }
    buttonByText(dialog, /^submit review/i)?.click();
  };

  document.addEventListener('keydown', (e) => {
    if (e.metaKey && e.shiftKey && !e.ctrlKey && !e.altKey && e.key === 'Enter') {
      approveReview();
      e.preventDefault();
      e.stopPropagation();
      return;
    }
    if (typing(e)) return;
    if (e.ctrlKey) {
      const factor = PAGE[e.key];
      if (factor === undefined) return;
      window.scrollBy({ top: window.innerHeight * factor, behavior: 'instant' });
      e.preventDefault();
      e.stopPropagation();
      return;
    }
    const { list, idx } = currentIndex();
    if (!list.length) return;
    switch (e.key) {
      case 'j':
        scrollTo(list[Math.min(idx + 1, list.length - 1)]);
        break;
      case 'k':
        scrollTo(list[Math.max(idx - 1, 0)]);
        break;
      case 'v': {
        const ctl = viewedControl(list[idx]);
        const next = list[Math.min(idx + 1, list.length - 1)];
        if (ctl) ctl.click();
        settleScroll(next);
        break;
      }
      case 'o': {
        const btn = toggleControl(list[idx]);
        if (btn) btn.click();
        break;
      }
      default:
        return;
    }
    e.preventDefault();
    e.stopPropagation();
  }, true);
})();
