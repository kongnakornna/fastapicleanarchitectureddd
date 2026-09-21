import Alpine from 'alpinejs';

// ═══════════════════════════════════════════════
// 🎨 Theme Store (แทน LayoutService.theme*)
// ═══════════════════════════════════════════════
Alpine.store('theme', {
  mode: localStorage.getItem('tabler-theme') || 'light',
  primary: localStorage.getItem('tabler-theme-primary') || 'blue',
  font: localStorage.getItem('tabler-theme-font') || 'sans-serif',
  base: localStorage.getItem('tabler-theme-base') || 'slate',
  radius: localStorage.getItem('tabler-theme-radius') || '0.5',

  _apply() {
    const html = document.documentElement;
    html.setAttribute('data-bs-theme', this.mode);
    html.classList.toggle('dark', this.mode === 'dark');
    html.style.setProperty('--tblr-primary', `var(--tblr-${this.primary})`);
    html.style.setProperty('--tblr-font-sans-serif',
      this.font === 'serif' ? 'Georgia, serif'
      : this.font === 'monospace' ? 'ui-monospace, monospace'
      : this.font === 'comic' ? '"Comic Sans MS", cursive'
      : '"Inter","Sarabun",sans-serif');
    html.style.setProperty('--tblr-border-radius', `${this.radius}rem`);
    html.setAttribute('data-bs-theme-base', this.base);
  },

  toggle() { this.set(this.mode === 'dark' ? 'light' : 'dark'); },
  set(mode) { this.mode = mode; localStorage.setItem('tabler-theme', mode); this._apply(); },
  setPrimary(v) { this.primary = v; localStorage.setItem('tabler-theme-primary', v); this._apply(); },
  setFont(v) { this.font = v; localStorage.setItem('tabler-theme-font', v); this._apply(); },
  setBase(v) { this.base = v; localStorage.setItem('tabler-theme-base', v); this._apply(); },
  setRadius(v) { this.radius = v; localStorage.setItem('tabler-theme-radius', v); this._apply(); },

  reset() {
    localStorage.removeItem('tabler-theme');
    localStorage.removeItem('tabler-theme-primary');
    localStorage.removeItem('tabler-theme-font');
    localStorage.removeItem('tabler-theme-base');
    localStorage.removeItem('tabler-theme-radius');
    this.mode = 'light'; this.primary = 'blue';
    this.font = 'sans-serif'; this.base = 'slate'; this.radius = '0.5';
    this._apply();
  },
});

// ═══════════════════════════════════════════════
// 🧱 Layout Store (แทน LayoutService.layout)
// ═══════════════════════════════════════════════
Alpine.store('layout', {
  mode: localStorage.getItem('tabler-layout') || 'fluid',
  sidebarCollapsed: false,

  set(mode) {
    this.mode = mode;
    localStorage.setItem('tabler-layout', mode);
    document.body.classList.toggle('layout-boxed', mode === 'boxed' || mode === 'boxed-2');
    document.body.classList.toggle('layout-boxed-2', mode === 'boxed-2');
  },

  toggleSidebar() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
    document.body.classList.toggle('sidebar-collapsed', this.sidebarCollapsed);
  },
});

// ═══════════════════════════════════════════════
// 🧩 Components
// ═══════════════════════════════════════════════
Alpine.data('appShell', () => ({
  init() {
    Alpine.store('theme')._apply();
    Alpine.store('layout').set(Alpine.store('layout').mode);
  },
}));

Alpine.data('headerComponent', () => ({
  menuOpen: false,
  unreadCount: 3,
  showLogoutConfirm: false,

  toggleMenu() { this.menuOpen = !this.menuOpen; },

  openFullscreen() {
    const el = document.documentElement;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (el.requestFullscreen) {
      el.requestFullscreen();
    } else if (el.webkitRequestFullscreen) {
      el.webkitRequestFullscreen();
    } else if (el.msRequestFullscreen) {
      el.msRequestFullscreen();
    } else if (el.mozRequestFullScreen) {
      el.mozRequestFullScreen();
    }
  },

  openLogoutConfirm() {
    window.dispatchEvent(new CustomEvent('open-modal', { detail: 'logout-confirm' }));
  },
}));

Alpine.data('sidebarComponent', () => ({
  init() {
    // Sync with layout store
    this.$watch('$store.layout.sidebarCollapsed', (v) => {
      document.body.classList.toggle('sidebar-collapsed', v);
    });
  },
}));

Alpine.data('confirmModal', () => ({
  visible: false,
  onConfirm: null,
  init() {
    window.addEventListener('open-modal', (e) => {
      if (e.detail === 'logout-confirm') {
        this.visible = true;
        this.onConfirm = () => this.logout();
      }
    });
  },
  cancel() { this.visible = false; },
  confirm() {
    this.visible = false;
    if (this.onConfirm) this.onConfirm();
  },
  async logout() {
    // Preserve theme keys (from Angular logout())
    const preserve = {};
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k?.startsWith('tabler-')) preserve[k] = localStorage.getItem(k);
    }
    localStorage.clear();
    Object.entries(preserve).forEach(([k, v]) => localStorage.setItem(k, v));

    // Call FastAPI logout via HTMX/Django proxy
    try {
      await fetch('/auth/logout-all/', { method: 'POST', credentials: 'include' });
    } finally {
      window.location.href = '/login';
    }
  },
}));

window.Alpine = Alpine;
Alpine.start();