// VEXORA shared UI: loading screen + language toggle + mobile menu
(function () {
  const LANG_DATA = {
    id: {
      search_placeholder: "Cari judul donghua...",
      search_btn: "CARI",
      welcome_title: "Pusat Streaming donghua Terlengkap",
      welcome_sub: "Pilih judul di bawah atau gunakan pencarian.",
      loading: "MEMUAT • LOADING...",
      loading_sub: "Memuat konten terbaik untukmu",
      nav: ["Beranda","Genre","Schedule","Terbaru","Bookmark","Riwayat"],
      menu_nav: "Navigasi",
      menu_lang: "Bahasa",
      footer_crafted: "CRAFTED BY",
      footer_copy: "© 2026 VEXORA • Dibuat oleh Vexalyn Developer [Vio Atmajaya]"
    },
    en: {
      search_placeholder: "Search donghua title...",
      search_btn: "SEARCH",
      welcome_title: "Most Complete donghua Streaming Center",
      welcome_sub: "Pick a title below or use search.",
      loading: "LOADING...",
      loading_sub: "Loading the best content for you",
      nav: ["Home","Genre","Schedule","Latest","Bookmark","History"],
      menu_nav: "Navigation",
      menu_lang: "Language",
      footer_crafted: "CRAFTED BY",
      footer_copy: "© 2026 VEXORA • Made by Vexalyn Developer [Vio Atmajaya]"
    },
    ja: {
      search_placeholder: "動画タイトルを検索...",
      search_btn: "検索",
      welcome_title: "最高峰の動画配信センター",
      welcome_sub: "以下のタイトルを選択するか、検索を使用してください。",
      loading: "読み込み中...",
      loading_sub: "最良のコンテンツを読み込み中",
      nav: ["ホーム","ジャンル","スケジュール","最新","ブックマーク","履歴"],
      menu_nav: "ナビゲーション",
      menu_lang: "言語",
      footer_crafted: "制作者",
      footer_copy: "© 2026 VEXORA • Vexalyn Developer [Vio Atmajaya] が制作"
    },
    zh: {
      search_placeholder: "搜索动画标题...",
      search_btn: "搜索",
      welcome_title: "最完整的流媒体中心",
      welcome_sub: "选择下面的标题或使用搜索。",
      loading: "加载中...",
      loading_sub: "正在为您加载最佳内容",
      nav: ["首页","类型","日程","最新","收藏","历史"],
      menu_nav: "导航",
      menu_lang: "语言",
      footer_crafted: "制作者",
      footer_copy: "© 2026 VEXORA • 由 Vexalyn Developer [Vio Atmajaya] 制作"
    }
  };

  let currentLang = localStorage.getItem('vexora_lang') || 'id';

  const STYLE = `
  #loadingScreen{position:fixed;inset:0;z-index:9999;background:#0a0a0a;display:flex;flex-direction:column;align-items:center;justify-content:center;transition:opacity .5s ease,visibility .5s ease}
  #loadingScreen.hide{opacity:0;visibility:hidden;pointer-events:none}
  .loader-logo{font-family:'Bebas Neue',sans-serif;font-size:48px;letter-spacing:6px;color:#fff;margin-bottom:40px;animation:logoPulse 1.5s ease-in-out infinite}
  .loader-bar-track{width:200px;height:3px;background:rgba(255,255,255,0.1);border-radius:2px;overflow:hidden}
  .loader-bar{height:100%;background:linear-gradient(90deg,#e50914,#ff3b44,#e50914);border-radius:2px;width:0%;animation:loaderFill 1.8s ease-in-out forwards}
  .loader-dots{display:flex;gap:6px;margin-top:20px}
  .loader-dots span{width:6px;height:6px;border-radius:50%;background:#555;animation:dotPulse 1.2s ease-in-out infinite}
  .loader-dots span:nth-child(2){animation-delay:.15s}
  .loader-dots span:nth-child(3){animation-delay:.3s}
  .loader-text{color:#525252;font-size:11px;margin-top:16px;letter-spacing:2px;text-transform:uppercase}
  @keyframes logoPulse{0%,100%{opacity:1}50%{opacity:.7}}
  @keyframes loaderFill{0%{width:0%}60%{width:85%}100%{width:100%}}
  @keyframes dotPulse{0%,100%{background:#555}50%{background:#e50914}}
  #mobileMenu{max-height:0;overflow:hidden;transition:max-height .35s cubic-bezier(.4,0,.2,1),opacity .25s ease;opacity:0;padding:0 1rem}
  #mobileMenu.open{max-height:600px;opacity:1;padding:0.75rem 1rem}
  #mobileMenuDetail,#mobileMenuPlayer{max-height:0;overflow:hidden;opacity:0;transition:max-height .35s cubic-bezier(.4,0,.2,1),opacity .25s ease}
  #mobileMenuDetail.open,#mobileMenuPlayer.open{max-height:600px;opacity:1}
  .lang-btn{flex:1;padding:6px 0;font-size:11px;font-weight:700;border-radius:6px;background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.6)}
  .lang-btn.active{background:#e50914;color:#fff}
  .ftr-lang{padding:2px 8px;font-size:10px;font-weight:700;border-radius:6px;background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.5)}
  .ftr-lang.active{background:#e50914;color:#fff}
  `;

  function injectStyle() {
    const s = document.createElement('style');
    s.textContent = STYLE;
    document.head.appendChild(s);
  }

  function updateLangBtns() {
    document.querySelectorAll('.lang-btn').forEach(b => {
      b.className = 'lang-btn' + (b.id === 'lang-' + currentLang ? ' active' : '');
    });
    document.querySelectorAll('.ftr-lang').forEach(b => {
      b.className = 'ftr-lang' + (b.id === 'ftr-lang-' + currentLang ? ' active' : '');
    });
  }

  function applyLang() {
    const d = LANG_DATA[currentLang] || LANG_DATA.id;
    let si = document.getElementById('searchInput'); if (si) si.placeholder = d.search_placeholder;
    let sm = document.getElementById('searchInputMobile'); if (sm) sm.placeholder = d.search_placeholder;
    document.querySelectorAll('button').forEach(b => {
      const t = (b.textContent || '').trim();
      if (t === 'CARI' || t === 'SEARCH' || t === '検索' || t === '搜索') b.textContent = d.search_btn;
    });
    let wf = document.querySelector('#heroFallback h2'); if (wf) wf.textContent = d.welcome_title;
    let wp = document.querySelector('#heroFallback p'); if (wp) wp.textContent = d.welcome_sub;
    let lt = document.querySelector('.loader-text'); if (lt) lt.textContent = d.loading_sub;
    let navIds = ['navBeranda','navGenre','navSchedule','navTerbaru','navBookmark','navRiwayat'];
    navIds.forEach((id, i) => {
      let el = document.getElementById(id);
      if (el && d.nav[i]) { let ic = el.querySelector('i'); el.innerHTML = ic ? ic.outerHTML + ' ' + d.nav[i] : d.nav[i]; }
    });
    document.querySelectorAll('#mobileMenu > a, #mobileMenuDetail > a, #mobileMenuPlayer > a').forEach((a, i) => {
      if (d.nav[i]) { let ic = a.querySelector('i'); a.innerHTML = ic ? ic.outerHTML + ' ' + d.nav[i] : d.nav[i]; }
    });
    let fc = document.getElementById('footerCopy'); if (fc) fc.textContent = d.footer_copy;
    let fcr = document.getElementById('footerCrafted'); if (fcr) fcr.textContent = d.footer_crafted;
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const k = el.getAttribute('data-i18n');
      if (d[k] != null) el.textContent = d[k];
    });
  }

  window.setLang = function (lang) {
    currentLang = lang;
    try { localStorage.setItem('vexora_lang', lang); } catch (e) {}
    applyLang();
    updateLangBtns();
  };

  window.toggleMobileMenu = function () {
    ['mobileMenu', 'mobileMenuDetail', 'mobileMenuPlayer'].forEach(id => {
      let m = document.getElementById(id);
      if (m) m.classList.toggle('open');
    });
  };

  window.hideLoading = function () {
    let l = document.getElementById('loadingScreen');
    if (l) l.classList.add('hide');
  };
  window.showLoading = function () {
    let l = document.getElementById('loadingScreen');
    if (l) l.classList.remove('hide');
  };

  function init() {
    injectStyle();
    applyLang();
    updateLangBtns();
    const l = document.getElementById('loadingScreen');
    if (l) {
      const done = () => setTimeout(() => l.classList.add('hide'), 500);
      if (document.readyState === 'complete') done();
      else window.addEventListener('load', done);
      // safety: hide after 4s regardless
      setTimeout(() => l.classList.add('hide'), 4000);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
