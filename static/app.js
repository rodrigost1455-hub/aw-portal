/* AW Portal — vanilla JS */

// ── Currency ──────────────────────────────────────────────────
function fmt(n) {
  if (n === '' || n === null || n === undefined || isNaN(n)) return '—';
  const num = Number(n);
  const sign = num < 0 ? '-' : '';
  return sign + '$' + Math.abs(Math.round(num)).toLocaleString('en-US');
}

// ── SVG icons ─────────────────────────────────────────────────
const SVG = {
  plus:     `<svg class="ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M8 3v10M3 8h10"/></svg>`,
  trash:    `<svg class="ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 4h10M6.5 4V2.5h3V4M4.5 4l.6 9a1 1 0 0 0 1 1h3.8a1 1 0 0 0 1-1l.6-9M6.5 7v4M9.5 7v4"/></svg>`,
  check:    `<svg style="width:10px;height:10px" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8l3 3 7-7"/></svg>`,
  lock:     `<svg class="ico-sm" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="7" width="9" height="7" rx="1"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2"/></svg>`,
  calc:     `<svg style="width:9px;height:9px;vertical-align:-1px" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="2" width="10" height="12" rx="1.5"/><path d="M5 5h6M5.5 8.5h1M8 8.5h1M10.5 8.5h0M5.5 11h1M8 11h1M10.5 11h0"/></svg>`,
  save:     `<svg class="ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2h8l2 2v9a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1z"/><path d="M5 2v4h5V2M5 10h6"/></svg>`,
  download: `<svg class="ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v8m0 0l-3-3m3 3l3-3M2.5 12v1.5a.5.5 0 0 0 .5.5h10a.5.5 0 0 0 .5-.5V12"/></svg>`,
};

// ── Toggle (spouse section) ───────────────────────────────────
function initSpouseToggle() {
  const btn = document.getElementById('spouse-toggle');
  const section = document.getElementById('spouse-section');
  if (!btn || !section) return;

  function apply(on) {
    btn.className = 'toggle-btn' + (on ? ' on' : '');
    section.style.display = on ? 'block' : 'none';
    btn.dataset.on = on ? '1' : '0';
  }

  apply(btn.dataset.on === '1');

  btn.addEventListener('click', () => {
    apply(btn.dataset.on !== '1');
  });
}

// ── Quarter tabs ──────────────────────────────────────────────
function initQuarterTabs() {
  const tabs = document.querySelectorAll('.quarter-tab');
  const hidden = document.getElementById('quarter-hidden');
  if (!tabs.length || !hidden) return;

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      hidden.value = tab.dataset.q;
    });
  });
}

// ── Checkboxes (custom styled) ────────────────────────────────
function initCheckboxes() {
  document.querySelectorAll('.checkbox-item').forEach(item => {
    const input = item.querySelector('input[type=checkbox]');
    const box   = item.querySelector('.checkbox-box');
    if (!input || !box) return;
    function sync() { box.innerHTML = input.checked ? SVG.check : ''; }
    sync();
    input.addEventListener('change', sync);
  });
}

// ── Dynamic account rows (client form) ───────────────────────
let acctIndex = 0;

function buildAccountRow(idx) {
  const div = document.createElement('div');
  div.className = 'account-row';
  div.dataset.idx = idx;
  div.innerHTML = `
    <div class="account-row-top">
      <div class="form-row">
        <label class="field-label">Owner</label>
        <select class="select" name="acct_owner[]">
          <option value="client1">Client 1</option>
          <option value="client2">Client 2</option>
          <option value="joint">Joint</option>
        </select>
      </div>
      <div class="form-row">
        <label class="field-label">Type</label>
        <select class="select acct-type-sel" name="acct_type[]">
          <option value="IRA">IRA</option>
          <option value="RothIRA">Roth IRA</option>
          <option value="401K">401K</option>
          <option value="brokerage">Brokerage</option>
          <option value="trust">Trust</option>
          <option value="liability">Liability</option>
        </select>
      </div>
      <div class="form-row">
        <label class="field-label">Account · last 4</label>
        <input type="text" class="input" name="acct_last4[]" maxlength="4" placeholder="1234">
      </div>
      <div class="form-row" style="align-items:center;margin-bottom:2px;">
        <button type="button" class="btn-icon remove-acct-btn" title="Remove account">${SVG.trash}</button>
      </div>
    </div>
    <div class="account-row-bottom">
      <div class="checkbox-row">
        <label class="checkbox-item">
          <input type="checkbox" name="acct_retirement[]" value="${idx}" class="flag-ret">
          <span class="checkbox-box"></span> Retirement
        </label>
        <label class="checkbox-item">
          <input type="checkbox" name="acct_trust[]" value="${idx}" class="flag-trust">
          <span class="checkbox-box"></span> Trust
        </label>
        <label class="checkbox-item">
          <input type="checkbox" name="acct_liability[]" value="${idx}" class="flag-liab">
          <span class="checkbox-box"></span> Liability
        </label>
      </div>
      <div class="rate-field" style="display:none;">
        <label class="field-label" style="white-space:nowrap;">Interest Rate</label>
        <div class="input-with-suffix" style="width:100px;">
          <input type="text" class="input" name="acct_rate[]" placeholder="0.00">
          <span class="suffix">%</span>
        </div>
      </div>
    </div>`;

  // wire type → auto-flags + rate field
  const typeEl  = div.querySelector('.acct-type-sel');
  const retEl   = div.querySelector('.flag-ret');
  const trustEl = div.querySelector('.flag-trust');
  const liabEl  = div.querySelector('.flag-liab');
  const rateEl  = div.querySelector('.rate-field');

  function applyType(t) {
    retEl.checked   = ['IRA','RothIRA','401K'].includes(t);
    trustEl.checked = t === 'trust';
    liabEl.checked  = t === 'liability';
    rateEl.style.display = t === 'liability' ? 'flex' : 'none';
    div.querySelectorAll('.checkbox-box').forEach((box, i) => {
      const chk = div.querySelectorAll('input[type=checkbox]')[i];
      box.innerHTML = chk.checked ? SVG.check : '';
    });
  }

  typeEl.addEventListener('change', () => applyType(typeEl.value));
  liabEl.addEventListener('change', () => {
    rateEl.style.display = liabEl.checked ? 'flex' : 'none';
  });

  // checkbox visual sync
  div.querySelectorAll('.checkbox-item').forEach(item => {
    const input = item.querySelector('input');
    const box   = item.querySelector('.checkbox-box');
    input.addEventListener('change', () => { box.innerHTML = input.checked ? SVG.check : ''; });
  });

  // remove button
  div.querySelector('.remove-acct-btn').addEventListener('click', () => {
    div.remove();
    updateEmptyState();
  });

  return div;
}

function updateEmptyState() {
  const container = document.getElementById('accounts-container');
  const empty     = document.getElementById('accounts-empty');
  if (!container || !empty) return;
  empty.style.display = container.querySelectorAll('.account-row').length === 0 ? 'block' : 'none';
}

function initClientForm() {
  const container = document.getElementById('accounts-container');
  const addBtn    = document.getElementById('add-account-btn');
  if (!container || !addBtn) return;

  // wire existing rows
  acctIndex = container.querySelectorAll('.account-row').length;
  container.querySelectorAll('.account-row').forEach(row => {
    row.querySelector('.remove-acct-btn')?.addEventListener('click', () => {
      row.remove(); updateEmptyState();
    });
    const liabEl = row.querySelector('.flag-liab');
    const rateEl = row.querySelector('.rate-field');
    liabEl?.addEventListener('change', () => {
      if (rateEl) rateEl.style.display = liabEl.checked ? 'flex' : 'none';
    });
    row.querySelectorAll('.checkbox-item').forEach(item => {
      const input = item.querySelector('input');
      const box   = item.querySelector('.checkbox-box');
      if (input && box) {
        box.innerHTML = input.checked ? SVG.check : '';
        input.addEventListener('change', () => { box.innerHTML = input.checked ? SVG.check : ''; });
      }
    });
  });

  addBtn.addEventListener('click', () => {
    const row = buildAccountRow(acctIndex++);
    container.appendChild(row);
    updateEmptyState();
  });

  updateEmptyState();
}

// ── Private Reserve auto-calc (client form) ───────────────────
function initPRCalc() {
  const expInput = document.getElementById('monthly_expense_budget');
  const prInput  = document.getElementById('private_reserve_target_display');
  if (!expInput || !prInput) return;

  function update() {
    const val = parseFloat(expInput.value) || 0;
    prInput.value = '$' + Math.round(val * 6).toLocaleString('en-US');
  }
  expInput.addEventListener('input', update);
  update();
}

// ── Report form: real-time calculations ───────────────────────
function initReportCalc() {
  const form = document.getElementById('report-form');
  if (!form) return;

  function val(id) { return parseFloat(document.getElementById(id)?.value) || 0; }
  function setTxt(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }
  function setInp(id, v) { const el = document.getElementById(id); if (el) el.value = v; }

  function recalc() {
    const inflow  = val('inflow');
    const outflow = val('outflow');
    const excess  = inflow - outflow;

    // readonly excess field
    setInp('excess_display', Math.round(excess).toLocaleString('en-US'));

    // live panel
    setTxt('p-inflow',  fmt(inflow));
    setTxt('p-outflow', fmt(outflow));
    setTxt('p-excess',  fmt(excess));

    const excessRow = document.getElementById('p-excess-row');
    if (excessRow) {
      excessRow.querySelector('.value').className =
        'value ' + (excess >= 0 ? 'value-blue' : 'value-red');
    }

    // PR
    const prBal    = val('private_reserve_balance');
    const prTarget = parseFloat(document.getElementById('pr_target_val')?.dataset.target) || 0;
    setTxt('p-pr', fmt(prBal));
    setTxt('p-pr-target', fmt(prTarget));

    // accounts
    let c1Ret = 0, c2Ret = 0, nonRet = 0, trust = 0, liab = 0;
    document.querySelectorAll('.balance-input').forEach(inp => {
      const v      = parseFloat(inp.value) || 0;
      const owner  = inp.dataset.owner;
      const isRet  = inp.dataset.retirement === 'true';
      const isTrust = inp.dataset.trust === 'true';
      const isLiab = inp.dataset.liability === 'true';
      if (isLiab)       liab  += v;
      else if (isTrust) trust += v;
      else if (isRet && owner === 'client1') c1Ret += v;
      else if (isRet && owner === 'client2') c2Ret += v;
      else if (isRet && owner === 'joint')   { c1Ret += v/2; c2Ret += v/2; }
      else                                   nonRet += v;
    });

    const grand = c1Ret + c2Ret + nonRet + trust;
    setTxt('p-c1-ret',  fmt(c1Ret));
    setTxt('p-c2-ret',  fmt(c2Ret));
    setTxt('p-non-ret', fmt(nonRet));
    setTxt('p-trust',   fmt(trust));
    setTxt('p-grand',   fmt(grand));
    setTxt('p-liab',    fmt(liab));

    // required fields warning
    const requiredEmpty = document.querySelectorAll('.balance-input[data-required="true"]')
      .length > 0
      ? [...document.querySelectorAll('.balance-input[data-required="true"]')]
          .filter(i => i.value === '' || i.value === '0').length
      : 0;

    const warnEl = document.getElementById('required-warn');
    const readyEl = document.getElementById('ready-msg');
    const warnCount = document.getElementById('warn-count');
    if (warnEl && readyEl) {
      // always show ready since all fields have defaults
      warnEl.style.display = 'none';
      readyEl.style.display = 'flex';
    }
  }

  form.addEventListener('input', recalc);
  recalc();
}

// ── action bar: form submission routing ───────────────────────
function initActionBar() {
  const saveBtn = document.getElementById('btn-save');
  const pdfBtn  = document.getElementById('btn-pdf');
  const form    = document.getElementById('report-form');
  const actionInput = document.getElementById('form-action');
  if (!form) return;

  saveBtn?.addEventListener('click', () => {
    if (actionInput) actionInput.value = 'save';
    form.submit();
  });
  pdfBtn?.addEventListener('click', () => {
    if (actionInput) actionInput.value = 'generate_pdf';
    form.submit();
  });
}

// ── Init ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initSpouseToggle();
  initQuarterTabs();
  initCheckboxes();
  initClientForm();
  initPRCalc();
  initReportCalc();
  initActionBar();
});
