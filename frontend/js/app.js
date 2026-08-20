/**
 * AegisFlow Single Page Application Controller
 * Pure Vanilla JavaScript
 */

let currentPage = 'dashboard';

/* ============================================
   LANDING PAGE
   ============================================ */
function enterApp() {
  const landing = document.getElementById('landing-page');
  const app = document.getElementById('app');
  if (landing) {
    landing.classList.add('hiding');
    setTimeout(() => {
      landing.classList.add('hidden');
      if (app) {
        app.classList.remove('app-hidden');
        // Sidebar layout: row, not column
        app.style.display = 'flex';
        app.style.flexDirection = 'row';
        app.style.height = '100vh';
      }
      initNavigation();
      checkBackendHealth();
      loadDashboard();
    }, 400);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Show landing page first; enterApp() is called from buttons
});

/**
 * Navigation Router
 */
function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link, .nav-item');
  const views = document.querySelectorAll('.page-view');

  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetPage = link.getAttribute('data-page');
      if (targetPage) {
        navigateToPage(targetPage);
      }
    });
  });
}

// Human-readable breadcrumb labels for the topbar
const PAGE_LABELS = {
  dashboard:       'Executive Dashboard',
  inventory:       'Inventory',
  suppliers:       'Suppliers',
  shipments:       'Shipments',
  map:             'Supply Chain Map',
  risks:           'Risk Intelligence',
  scenarios:       'What-If Scenarios',
  recommendations: 'AI Actions',
  compliance:      'Compliance',
  news:            'Supply Chain News',
  reports:         'Executive Reports',
};

function navigateToPage(targetPage) {
  currentPage = targetPage;

  // Update Nav link active state
  const navLinks = document.querySelectorAll('.nav-link, .nav-item');
  navLinks.forEach(n => {
    if (n.getAttribute('data-page') === targetPage) {
      n.classList.add('active');
    } else {
      n.classList.remove('active');
    }
  });

  // Update topbar breadcrumb
  const breadcrumb = document.getElementById('topbar-breadcrumb');
  if (breadcrumb) {
    breadcrumb.textContent = PAGE_LABELS[targetPage] || targetPage;
  }

  // Close mobile sidebar overlay if open
  const sidebar = document.getElementById('app-sidebar');
  if (sidebar && sidebar.classList.contains('mobile-open')) {
    sidebar.classList.remove('mobile-open');
  }

  // Update View active state
  const views = document.querySelectorAll('.page-view');
  views.forEach(v => v.classList.remove('active'));

  const targetView = document.getElementById(`view-${targetPage}`);
  if (targetView) {
    targetView.classList.add('active');
  }

  // Load target page data
  switch (targetPage) {
    case 'dashboard':   loadDashboard();         break;
    case 'risks':       loadRisks();             break;
    case 'suppliers':   loadSuppliers();         break;
    case 'shipments':   loadShipments();         break;
    case 'inventory':   loadInventory();         break;
    case 'scenarios':   loadScenarios();         break;
    case 'recommendations': loadRecommendations(); break;
    case 'compliance':  loadCompliance();        break;
    case 'map':         loadSupplyChainMap();    break;
    case 'news':        loadNews();              break;
    case 'reports':     loadReports();           break;
    default:            loadDashboard();
  }
}

function refreshCurrentView() {
  const btn = document.getElementById('global-refresh-btn');
  if (btn) {
    btn.classList.add('spinning');
    setTimeout(() => btn.classList.remove('spinning'), 1000);
  }
  navigateToPage(currentPage);
}

/* ============================================
   REFRESH BUTTON HELPERS
   ============================================ */
function setRefreshBtnState(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  if (loading) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
  } else {
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
  }
}

async function loadDashboardWithRefreshState() {
  setRefreshBtnState('dashboard-refresh-btn', true);
  try { await loadDashboard(); }
  finally { setRefreshBtnState('dashboard-refresh-btn', false); }
}

async function loadRisksWithRefreshState() {
  setRefreshBtnState('risks-refresh-btn', true);
  try { await loadRisks(); }
  finally { setRefreshBtnState('risks-refresh-btn', false); }
}

async function loadSuppliersWithRefreshState() {
  setRefreshBtnState('suppliers-refresh-btn', true);
  try { await loadSuppliers(); }
  finally { setRefreshBtnState('suppliers-refresh-btn', false); }
}

async function loadShipmentsWithRefreshState() {
  setRefreshBtnState('shipments-refresh-btn', true);
  try { await loadShipments(); }
  finally { setRefreshBtnState('shipments-refresh-btn', false); }
}

async function loadInventoryWithRefreshState() {
  setRefreshBtnState('inventory-refresh-btn', true);
  try { await loadInventory(); }
  finally { setRefreshBtnState('inventory-refresh-btn', false); }
}

async function refreshMapWithState() {
  setRefreshBtnState('map-refresh-btn', true);
  try { await loadSupplyChainMap(); }
  finally { setRefreshBtnState('map-refresh-btn', false); }
}

/**
 * Backend Health & Connection Status
 */
async function checkBackendHealth() {
  const indicator = document.getElementById('system-status-indicator');
  const text = document.getElementById('system-status-text');

  if (typeof API === 'undefined') {
    updateStatusPill(false, 'API Client Missing');
    return;
  }

  try {
    const health = await API.checkHealth();
    if (health && (health.status === 'healthy' || health.status === 'running')) {
      updateStatusPill(true, 'Backend Connected');
    } else {
      updateStatusPill(false, 'Backend Unhealthy');
    }
  } catch (err) {
    updateStatusPill(false, 'Backend Disconnected');
  }
}

function updateStatusPill(isConnected, message) {
  const indicator = document.getElementById('system-status-indicator');
  const text = document.getElementById('system-status-text');
  if (!indicator) return;

  // Use sidebar pill class (the topbar pill is gone)
  if (isConnected) {
    indicator.className = 'sidebar-status-pill connected';
    if (text) text.textContent = message || 'Connected';
  } else {
    indicator.className = 'sidebar-status-pill disconnected';
    if (text) text.textContent = message || 'Offline';
  }
}

/**
 * 1. Load Executive Dashboard Data
 * Pulls from dashboard summary + suppliers + shipments + risks
 * to populate ALL KPI cards with real live data.
 */
async function loadDashboard() {
  try {
    if (typeof API === 'undefined') {
      throw new Error('API client module unavailable');
    }

    // -------------------------------------------------------
    // Fetch all data in parallel — dashboard summary + detail
    // -------------------------------------------------------
    const [dashData, suppliers, shipments, risks] = await Promise.all([
      API.getDashboardSummary().catch(() => ({})),
      API.getSuppliers().catch(() => []),
      API.getShipments().catch(() => []),
      API.getRisks().catch(() => [])
    ]);

    updateStatusPill(true, 'Backend Connected');

    // -------------------------------------------------------
    // RISK KPI
    // -------------------------------------------------------
    const riskLevel = dashData.overall_risk_level || dashData.risk_level || 'LOW';
    const riskScore = dashData.overall_risk_score ?? (risks.length > 0
      ? Math.round(risks.reduce((s, r) => s + (r.risk_score || r.score || 0), 0) / risks.length)
      : 0);
    const criticalCount = dashData.critical_risks ?? dashData.critical_risks_count ??
      risks.filter(r => (r.severity || r.risk_level || '').toUpperCase() === 'CRITICAL').length;

    const elRiskLevel = document.getElementById('overall-risk-level');
    const elRiskScore = document.getElementById('overall-risk-score');
    const elRiskProgress = document.getElementById('overall-risk-progress');
    const elCriticalFooter = document.getElementById('kpi-critical-risks-footer');
    const elCriticalCount = document.getElementById('kpi-critical-risks-count');

    if (elRiskLevel) elRiskLevel.textContent = riskLevel;
    if (elRiskScore) {
      elRiskScore.textContent = `${riskScore} / 100`;
      const cls = riskScore <= 30 ? 'badge-low' : riskScore <= 50 ? 'badge-moderate' : riskScore <= 70 ? 'badge-high' : 'badge-critical';
      elRiskScore.className = `kpi-badge ${cls}`;
    }
    if (elRiskProgress) elRiskProgress.style.width = `${Math.min(100, Math.max(2, riskScore))}%`;
    if (elCriticalFooter) elCriticalFooter.textContent = `${criticalCount} critical risk${criticalCount !== 1 ? 's' : ''}`;
    if (elCriticalCount) elCriticalCount.textContent = criticalCount;

    // -------------------------------------------------------
    // SUPPLIERS KPI — always use live supplier data
    // -------------------------------------------------------
    const totalSuppliers = suppliers.length || dashData.total_suppliers || 0;
    const atRiskSuppliers = dashData.suppliers_at_risk ?? dashData.suppliers_at_risk_count ??
      suppliers.filter(s => {
        const lvl = (s.current_risk_level || s.risk_level || '').toUpperCase();
        return lvl === 'HIGH' || lvl === 'CRITICAL';
      }).length;

    const avgReliability = suppliers.length > 0
      ? Math.round(suppliers.reduce((s, sup) => s + (sup.reliability_score || 90), 0) / suppliers.length)
      : (dashData.average_supplier_reliability ? Math.round(dashData.average_supplier_reliability) : null);

    const elActiveSuppliers = document.getElementById('kpi-active-suppliers');
    const elSuppliersAtRisk = document.getElementById('kpi-suppliers-at-risk');
    const elAvgReliability = document.getElementById('kpi-avg-reliability');

    if (elActiveSuppliers) elActiveSuppliers.textContent = totalSuppliers > 0 ? totalSuppliers : '—';
    if (elSuppliersAtRisk) {
      elSuppliersAtRisk.textContent = `${atRiskSuppliers} at risk`;
      elSuppliersAtRisk.className = `kpi-badge ${atRiskSuppliers > 0 ? 'badge-warn' : 'badge-low'}`;
    }
    if (elAvgReliability) {
      elAvgReliability.textContent = avgReliability !== null ? `${avgReliability}%` : '—';
    }

    // -------------------------------------------------------
    // SHIPMENTS KPI — always use live shipment data
    // -------------------------------------------------------
    const totalShipments = shipments.length || dashData.total_shipments || 0;
    const delayedShipments = dashData.at_risk_shipments ?? dashData.delayed_shipments ??
      shipments.filter(s => (s.delay_days || 0) > 0 ||
        ['DELAYED', 'AT_RISK'].includes((s.status || '').toUpperCase())).length;

    const delayedOnly = shipments.filter(s => (s.delay_days || 0) > 0);
    const avgDelay = delayedOnly.length > 0
      ? (delayedOnly.reduce((s, sh) => s + (sh.delay_days || 0), 0) / delayedOnly.length).toFixed(1)
      : null;

    const elTotalShipments = document.getElementById('kpi-total-shipments');
    const elDelayedShipments = document.getElementById('kpi-delayed-shipments');
    const elAvgDelay = document.getElementById('kpi-avg-delay');

    if (elTotalShipments) elTotalShipments.textContent = totalShipments > 0 ? totalShipments : '—';
    if (elDelayedShipments) {
      elDelayedShipments.textContent = `${delayedShipments} delayed`;
      elDelayedShipments.className = `kpi-badge ${delayedShipments > 0 ? 'badge-danger' : 'badge-low'}`;
    }
    if (elAvgDelay) {
      elAvgDelay.textContent = avgDelay !== null ? `${avgDelay} days` : '0 days';
    }

    // -------------------------------------------------------
    // FINANCIAL EXPOSURE KPI
    // -------------------------------------------------------
    const potentialImpact = dashData.potential_impact;
    const elImpact = document.getElementById('kpi-potential-impact');
    const elImpactBadge = document.getElementById('kpi-impact-badge');

    if (elImpact) {
      if (potentialImpact !== undefined && potentialImpact !== null && potentialImpact !== 0) {
        elImpact.textContent = dashData.potential_impact_formatted || `$${Number(potentialImpact).toLocaleString()}`;
      } else if (criticalCount > 0) {
        // Calculate rough exposure from critical risks
        const critRisks = risks.filter(r => (r.severity || r.risk_level || '').toUpperCase() === 'CRITICAL');
        const exposure = critRisks.length * 50000; // conservative placeholder
        elImpact.textContent = exposure > 0 ? `$${exposure.toLocaleString()}` : 'N/A';
      } else {
        elImpact.textContent = criticalCount === 0 && risks.length > 0 ? '$0' : 'N/A';
      }
    }
    if (elImpactBadge) {
      elImpactBadge.textContent = criticalCount > 0 ? 'Elevated' : 'Normal';
      elImpactBadge.className = `kpi-badge ${criticalCount > 0 ? 'badge-warn' : 'badge-low'}`;
    }

    // -------------------------------------------------------
    // RISK CHART — bar chart from actual risk data
    // -------------------------------------------------------
    renderRiskChart(risks);

  } catch (error) {
    console.error('Failed to load dashboard data:', error);
    updateStatusPill(false, 'Connection Failed');
    showToast(`Unable to connect to AegisFlow API: ${error.message}`, 'error');
    // Show error states in KPIs
    ['overall-risk-level','kpi-active-suppliers','kpi-total-shipments','kpi-potential-impact'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = 'Error';
    });
    const chartBody = document.getElementById('risk-chart-body');
    if (chartBody) {
      chartBody.innerHTML = `<div class="chart-loading" style="color:#DC2626;">
        <i class="fas fa-exclamation-triangle"></i> Unable to load risk data.
        <button class="btn-outline" style="margin-left:10px;padding:5px 12px;font-size:0.78rem;" onclick="loadDashboard()">
          <i class="fas fa-redo"></i> Retry
        </button>
      </div>`;
    }
  }
}

/**
 * Render a bar chart from live risk data using inline SVG.
 */
function renderRiskChart(risks) {
  const container = document.getElementById('risk-chart-body');
  if (!container) return;

  if (!risks || risks.length === 0) {
    container.innerHTML = '<div class="chart-loading" style="color:var(--text-muted)"><i class="fas fa-info-circle"></i> No risk data available.</div>';
    return;
  }

  // Show up to 10 risks sorted by score descending
  const sorted = [...risks]
    .sort((a, b) => (b.risk_score || b.score || 0) - (a.risk_score || a.score || 0))
    .slice(0, 10);

  const maxScore = 100;
  const barH = 22;
  const gap = 6;
  const labelW = 140;
  const chartW = 340;
  const totalH = sorted.length * (barH + gap) + 20;

  const bars = sorted.map((r, i) => {
    const score = r.risk_score || r.score || 0;
    const sev = (r.severity || r.risk_level || 'LOW').toUpperCase();
    const barColor = sev === 'CRITICAL' ? '#DC2626' : sev === 'HIGH' ? '#EA580C' : sev === 'MEDIUM' || sev === 'MODERATE' ? '#D97706' : '#059669';
    const barW = Math.max(4, Math.round((score / maxScore) * chartW));
    const y = i * (barH + gap) + 10;
    const label = (r.title || r.entity_type || 'Risk').substring(0, 20) + ((r.title || '').length > 20 ? '…' : '');

    return `
      <g>
        <text x="${labelW - 6}" y="${y + barH / 2 + 4}" text-anchor="end" font-size="11" fill="#64748B" font-family="Inter,sans-serif">${escapeHtml(label)}</text>
        <rect x="${labelW}" y="${y}" width="${barW}" height="${barH}" rx="4" fill="${barColor}" opacity="0.85"/>
        <text x="${labelW + barW + 6}" y="${y + barH / 2 + 4}" font-size="11" fill="#374151" font-weight="700" font-family="Inter,sans-serif">${score}</text>
      </g>`;
  }).join('');

  container.innerHTML = `
    <div class="risk-bar-chart">
      <svg width="100%" viewBox="0 0 ${labelW + chartW + 60} ${totalH}" style="min-height:${totalH}px; display:block;">
        ${bars}
      </svg>
    </div>
    <div style="display:flex; gap:12px; margin-top:10px; flex-wrap:wrap;">
      <span style="font-size:0.7rem; display:flex; align-items:center; gap:4px;"><span style="width:10px;height:10px;background:#DC2626;border-radius:2px;display:inline-block;"></span> Critical</span>
      <span style="font-size:0.7rem; display:flex; align-items:center; gap:4px;"><span style="width:10px;height:10px;background:#EA580C;border-radius:2px;display:inline-block;"></span> High</span>
      <span style="font-size:0.7rem; display:flex; align-items:center; gap:4px;"><span style="width:10px;height:10px;background:#D97706;border-radius:2px;display:inline-block;"></span> Medium</span>
      <span style="font-size:0.7rem; display:flex; align-items:center; gap:4px;"><span style="width:10px;height:10px;background:#059669;border-radius:2px;display:inline-block;"></span> Low</span>
    </div>`;
}

function updateRiskBadges(data) {
  // Retained for backward compat — dashboard now uses inline logic
}

/**
 * 2. Load Risks View
 */
async function loadRisks() {
  const tbody = document.getElementById('risks-table-body');
  const badge = document.getElementById('risks-count-badge');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="7" class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Fetching risk telemetry...</td></tr>';

  try {
    const risks = await API.getRisks();
    if (badge) badge.textContent = `${risks.length} Risks`;

    if (!risks || risks.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">No active risks detected in supply chain.</td></tr>';
      return;
    }

    tbody.innerHTML = risks.map(r => {
      const score = r.risk_score || r.score || 0;
      const severity = (r.severity || r.risk_level || 'LOW').toUpperCase();
      const sevClass = `badge-sev-${severity.toLowerCase()}`;

      return `
        <tr>
          <td><strong>#${r.id}</strong></td>
          <td><strong>${escapeHtml(r.title || 'Risk Event')}</strong></td>
          <td><span class="badge-count">${escapeHtml(r.entity_type || 'General')}</span></td>
          <td><strong>${score}</strong> / 100</td>
          <td><span class="badge-sev ${sevClass}">${severity}</span></td>
          <td>${escapeHtml(r.impact_description || r.risk_reason || 'No description provided.')}</td>
          <td><span class="status-badge connected"><i class="fas fa-circle"></i> ${escapeHtml(r.status || 'ACTIVE')}</span></td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading risks:', err);
    tbody.innerHTML = `<tr><td colspan="7" class="loading-cell" style="color:#EF4444;"><i class="fas fa-exclamation-triangle"></i> Failed to load risks: ${escapeHtml(err.message)}</td></tr>`;
    showToast(`API Error: ${err.message}`, 'error');
  }
}

/* ============================================
   SUPPLIER MANAGEMENT WITH FILTER & SEARCH
   ============================================ */
let _allSuppliers = [];  // cache for filtering

/**
 * 3. Load Suppliers View — all suppliers from API
 */
async function loadSuppliers() {
  const tbody = document.getElementById('suppliers-table-body');
  const badge = document.getElementById('suppliers-count-badge');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="9" class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Loading supplier directory...</td></tr>';

  try {
    const suppliers = await API.getSuppliers();
    _allSuppliers = suppliers || [];

    if (!suppliers || suppliers.length === 0) {
      if (badge) badge.textContent = '0 Suppliers';
      tbody.innerHTML = '<tr><td colspan="9" class="loading-cell"><i class="fas fa-info-circle"></i> No supplier records found.</td></tr>';
      return;
    }

    // Populate filter dropdowns
    const countries = [...new Set(suppliers.map(s => s.country).filter(Boolean))].sort();
    const categories = [...new Set(suppliers.map(s => s.category).filter(Boolean))].sort();

    const countryFilter = document.getElementById('supplier-country-filter');
    const categoryFilter = document.getElementById('supplier-category-filter');

    if (countryFilter) {
      countryFilter.innerHTML = '<option value="">All Countries</option>' +
        countries.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
    }
    if (categoryFilter) {
      categoryFilter.innerHTML = '<option value="">All Categories</option>' +
        categories.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
    }

    // Render all suppliers
    renderSupplierTable(_allSuppliers, badge);

  } catch (err) {
    console.error('Error loading suppliers:', err);
    tbody.innerHTML = `<tr><td colspan="9" class="loading-cell" style="color:#DC2626;"><i class="fas fa-exclamation-triangle"></i> Unable to load suppliers. <button class="btn-outline" style="margin-left:8px;padding:4px 10px;font-size:0.78rem;" onclick="loadSuppliers()"><i class="fas fa-redo"></i> Retry</button></td></tr>`;
    showToast(`Unable to load supplier data: ${err.message}`, 'error');
  }
}

function filterSuppliers() {
  if (!_allSuppliers.length) return;

  const search   = (document.getElementById('supplier-search')?.value || '').toLowerCase();
  const country  = (document.getElementById('supplier-country-filter')?.value || '').toLowerCase();
  const category = (document.getElementById('supplier-category-filter')?.value || '').toLowerCase();
  const risk     = (document.getElementById('supplier-risk-filter')?.value || '').toUpperCase();
  const sortBy   = document.getElementById('supplier-sort')?.value || 'name';

  const riskOrder = { LOW: 1, MEDIUM: 2, MODERATE: 2, HIGH: 3, CRITICAL: 4 };

  let filtered = _allSuppliers.filter(s => {
    const name = (s.name || '').toLowerCase();
    const sc = (s.country || '').toLowerCase();
    const scat = (s.category || '').toLowerCase();
    const srisk = (s.current_risk_level || s.risk_level || 'LOW').toUpperCase();

    return (
      (!search   || name.includes(search) || sc.includes(search) || scat.includes(search)) &&
      (!country  || sc === country) &&
      (!category || scat === category) &&
      (!risk     || srisk === risk)
    );
  });

  filtered.sort((a, b) => {
    if (sortBy === 'reliability')  return (b.reliability_score || 0) - (a.reliability_score || 0);
    if (sortBy === 'on_time')      return (b.on_time_delivery || 0) - (a.on_time_delivery || 0);
    if (sortBy === 'risk_asc')     return (riskOrder[(a.current_risk_level||a.risk_level||'LOW').toUpperCase()]||1) - (riskOrder[(b.current_risk_level||b.risk_level||'LOW').toUpperCase()]||1);
    if (sortBy === 'risk_desc')    return (riskOrder[(b.current_risk_level||b.risk_level||'LOW').toUpperCase()]||1) - (riskOrder[(a.current_risk_level||a.risk_level||'LOW').toUpperCase()]||1);
    return (a.name || '').localeCompare(b.name || '');
  });

  const badge = document.getElementById('suppliers-count-badge');
  renderSupplierTable(filtered, badge, filtered.length !== _allSuppliers.length);
}

function renderSupplierTable(suppliers, badge, filtered = false) {
  const tbody = document.getElementById('suppliers-table-body');
  if (!tbody) return;

  if (badge) {
    badge.textContent = filtered
      ? `${suppliers.length} of ${_allSuppliers.length} Suppliers`
      : `${suppliers.length} Suppliers`;
  }

  if (suppliers.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" class="loading-cell"><i class="fas fa-search"></i> No suppliers match your filters.</td></tr>';
    return;
  }

  tbody.innerHTML = suppliers.map(s => {
    const rel    = s.reliability_score || 90;
    const onTime = s.on_time_delivery || 92;
    const qual   = s.quality_score || 98;
    const riskLvl = (s.current_risk_level || s.risk_level || 'LOW').toUpperCase();
    const sevClass = `badge-sev-${riskLvl.toLowerCase()}`;
    const relColor = rel >= 90 ? '#059669' : rel >= 70 ? '#D97706' : '#DC2626';

    return `
      <tr>
        <td><strong style="color:var(--text-muted);">${s.id}</strong></td>
        <td><strong>${escapeHtml(s.name)}</strong></td>
        <td>${escapeHtml(s.country || '—')}</td>
        <td><span class="badge-count" style="font-size:0.68rem;">${escapeHtml(s.category || 'General')}</span></td>
        <td>
          <div style="font-weight:700;color:${relColor};font-size:0.9rem;">${rel}%</div>
          <div class="progress-bar-sm"><div class="progress-bar-sm-fill" style="width:${rel}%;background:${relColor};"></div></div>
        </td>
        <td>${onTime}%</td>
        <td>${qual}%</td>
        <td><span class="badge-sev ${sevClass}">${riskLvl}</span></td>
        <td>
          <button class="action-btn-sm" onclick="triggerAnalyzeSupplier(${s.id})">
            <i class="fas fa-robot"></i> Analyze
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

// triggerAnalyzeSupplier → full implementation further below (SUPPLIER AI ANALYSIS MODAL)

/**
 * 4. Load Shipments View
 */
async function loadShipments() {
  const tbody = document.getElementById('shipments-table-body');
  const badge = document.getElementById('shipments-count-badge');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="8" class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Loading shipment telemetry...</td></tr>';

  try {
    const shipments = await API.getShipments();
    if (badge) badge.textContent = `${shipments.length} Shipments`;

    if (!shipments || shipments.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="loading-cell">No active shipment records found.</td></tr>';
      return;
    }

    tbody.innerHTML = shipments.map(shp => {
      const delay = shp.delay_days || 0;
      const riskLvl = (shp.risk_level || 'LOW').toUpperCase();
      const sevClass = `badge-sev-${riskLvl.toLowerCase()}`;

      return `
        <tr>
          <td><strong>${escapeHtml(shp.shipment_code || `#${shp.id}`)}</strong></td>
          <td>${escapeHtml(shp.cargo_description || 'General Freight')}</td>
          <td>${escapeHtml(shp.carrier || 'Ocean Carrier')}</td>
          <td>${escapeHtml(shp.origin || 'Origin')}</td>
          <td>${escapeHtml(shp.destination || 'Destination')}</td>
          <td><strong style="color:${delay > 0 ? '#EF4444' : '#10B981'};">${delay} Days</strong></td>
          <td><span class="badge-sev ${sevClass}">${riskLvl}</span></td>
          <td><span class="status-badge connected"><i class="fas fa-circle"></i> ${escapeHtml(shp.status || 'IN_TRANSIT')}</span></td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading shipments:', err);
    tbody.innerHTML = `<tr><td colspan="8" class="loading-cell" style="color:#EF4444;"><i class="fas fa-exclamation-triangle"></i> Failed to load shipments: ${escapeHtml(err.message)}</td></tr>`;
    showToast(`API Error: ${err.message}`, 'error');
  }
}

/**
 * 5. Load Inventory View
 */
async function loadInventory() {
  const tbody = document.getElementById('inventory-table-body');
  const badge = document.getElementById('inventory-count-badge');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="8" class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Loading inventory buffer tracking...</td></tr>';

  try {
    const inventory = await API.getInventory();
    if (badge) badge.textContent = `${inventory.length} SKUs`;

    if (!inventory || inventory.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="loading-cell">No inventory records found.</td></tr>';
      return;
    }

    tbody.innerHTML = inventory.map(item => {
      const days = item.days_remaining || 0;
      const riskLvl = (item.stockout_risk_level || item.stockout_risk || 'LOW').toUpperCase();
      const sevClass = `badge-sev-${riskLvl.toLowerCase()}`;

      return `
        <tr>
          <td><strong>${escapeHtml(item.sku || `SKU-${item.id}`)}</strong></td>
          <td><strong>${escapeHtml(item.product_name || 'Component Item')}</strong></td>
          <td>${item.current_stock || 0}</td>
          <td>${item.daily_demand || 0} / day</td>
          <td>${item.reorder_level || 0}</td>
          <td><strong style="color:${days <= 7 ? '#EF4444' : '#10B981'};">${days} Days</strong></td>
          <td>$${(item.unit_cost || 0).toFixed(2)}</td>
          <td><span class="badge-sev ${sevClass}">${riskLvl}</span></td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading inventory:', err);
    tbody.innerHTML = `<tr><td colspan="8" class="loading-cell" style="color:#EF4444;"><i class="fas fa-exclamation-triangle"></i> Failed to load inventory: ${escapeHtml(err.message)}</td></tr>`;
    showToast(`API Error: ${err.message}`, 'error');
  }
}

/**
 * 6. Load Scenario Simulation View
 */

const DISRUPTION_LABELS = {
  SUPPLIER_FAILURE:    'Supplier Failure',
  PORT_STRIKE:         'Port Strike',
  TYPHOON_DISRUPTION:  'Typhoon / Weather Event',
  GEOPOLITICAL_TENSION:'Geopolitical Tension',
  DEMAND_SPIKE:        'Demand Spike',
  LOGISTICS_DELAY:     'Logistics Delay',
  QUALITY_FAILURE:     'Quality Failure',
  PRICE_SHOCK:         'Price / Cost Shock',
  NATURAL_DISASTER:    'Natural Disaster',
  CYBER_INCIDENT:      'Cyber Incident',
};

function selectDisruptionType(type) {
  // Sync dropdown
  const sel = document.getElementById('scenario-disruption-select');
  if (sel) sel.value = type;

  // Sync chip active state
  const chips = document.querySelectorAll('.scenario-quick-chips .chip-btn-light');
  chips.forEach(chip => {
    const chipType = chip.getAttribute('onclick')?.match(/'([^']+)'/)?.[1];
    chip.classList.toggle('active', chipType === type);
  });

  loadScenarios();
}

function onDisruptionTypeChange() {
  const sel = document.getElementById('scenario-disruption-select');
  if (sel) selectDisruptionType(sel.value);
}

async function loadScenarios() {
  const container = document.getElementById('scenarios-grid');
  if (!container) return;

  const sel = document.getElementById('scenario-disruption-select');
  const disruptionType = sel ? sel.value : 'SUPPLIER_FAILURE';
  const disruptionLabel = DISRUPTION_LABELS[disruptionType] || disruptionType;

  container.innerHTML = `<div class="card"><p class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Simulating ${escapeHtml(disruptionLabel)} scenarios...</p></div>`;

  try {
    const scenarios = await API.getScenarios(disruptionType);

    if (!scenarios || scenarios.length === 0) {
      container.innerHTML = '<div class="card"><p class="loading-cell">No scenario models found for this disruption type.</p></div>';
      return;
    }

    // Find the recommended scenario for comparison baseline
    const recScenario = scenarios.find(s => s.is_recommended);
    const doNothing   = scenarios.find(s => (s.option_key || '').toUpperCase() === 'DO_NOTHING');

    container.innerHTML = scenarios.map(sc => {
      const isRec      = sc.is_recommended;
      const isDoNothing = (sc.option_key || '').toUpperCase() === 'DO_NOTHING';
      const costDelta  = sc.cost_delta || 0;
      const costStr    = costDelta >= 0
        ? `+$${costDelta.toLocaleString()}`
        : `-$${Math.abs(costDelta).toLocaleString()}`;

      // Risk colour
      const riskColor  = sc.risk_score > 70 ? '#EF4444' : sc.risk_score > 40 ? '#F59E0B' : '#10B981';
      // Cost colour: 0 = grey, high cost = amber, recommended even if higher cost = green
      const costColor  = isDoNothing ? '#6B7280' : costDelta > 40000 ? '#F59E0B' : '#10B981';

      return `
        <div class="scenario-card ${isRec ? 'recommended' : ''} ${isDoNothing ? 'do-nothing' : ''}">
          <div>
            <div class="scenario-header">
              <h4>${escapeHtml(sc.scenario_name || 'Scenario Option')}</h4>
              ${isRec ? '<span class="kpi-badge badge-low"><i class="fas fa-star"></i> Recommended</span>' : ''}
              ${isDoNothing ? '<span class="kpi-badge badge-high">Baseline Risk</span>' : ''}
            </div>
            <div class="scenario-body">
              <p>${escapeHtml(sc.details || 'Evaluates supply chain trade-offs between cost, lead time, and risk mitigation.')}</p>
            </div>
          </div>
          <div>
            <div class="scenario-metrics">
              <div><span>Cost Delta</span><strong style="color:${costColor};">${costStr}</strong></div>
              <div><span>Lead Time</span><strong>${sc.delay_days > 0 ? '+' : ''}${sc.delay_days || 0} Days</strong></div>
              <div><span>Risk Score</span><strong style="color:${riskColor};">${sc.risk_score} / 100</strong></div>
            </div>
            <div style="font-size:0.8rem; font-weight:600; color:var(--primary); text-align:right; margin-top:6px;">
              Net Impact: ${escapeHtml(sc.net_impact || 'Calculated')}
            </div>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading scenarios:', err);
    container.innerHTML = `<div class="card"><p class="loading-cell" style="color:#EF4444;"><i class="fas fa-exclamation-triangle"></i> Failed to run scenario simulation: ${escapeHtml(err.message)}</p></div>`;
    showToast(`API Error: ${err.message}`, 'error');
  }
}

/**
 * 7. Load AI Recommendations View
 */
async function loadRecommendations() {
  const container = document.getElementById('recommendations-list');
  if (!container) return;

  container.innerHTML = '<div class="card"><p class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Generating IBM Granite AI recommendations...</p></div>';

  try {
    const recs = await API.getRecommendations();

    if (!recs || recs.length === 0) {
      container.innerHTML = '<div class="card"><p class="loading-cell">No pending recommendations available.</p></div>';
      return;
    }

    container.innerHTML = recs.map(r => {
      const isApproved = (r.status || '').toUpperCase() === 'APPROVED';
      const conf = Math.round((r.confidence || r.confidence_score || 0.9) * 100);

      return `
        <div class="recommendation-card">
          <div class="rec-icon"><i class="fas fa-robot"></i></div>
          <div class="rec-content">
            <h4>${escapeHtml(r.action_title || r.recommendation || 'AI Action Recommendation')}</h4>
            <p>${escapeHtml(r.reasoning || r.reason || r.recommendation || 'Action proposed to mitigate disruption.')}</p>
            <div class="rec-meta">
              <span><i class="fas fa-bolt"></i> Priority: <strong>${escapeHtml(r.priority || 'High')}</strong></span>
              <span><i class="fas fa-chart-line"></i> Confidence: <strong>${conf}%</strong></span>
              <span><i class="fas fa-tag"></i> Type: <strong>${escapeHtml(r.entity_type || 'General')}</strong></span>
            </div>
          </div>
          <div>
            ${isApproved ?
              '<button class="action-btn-sm approved"><i class="fas fa-check-circle"></i> Approved</button>' :
              `<button class="action-btn-sm" onclick="triggerApproveRec(${r.id})"><i class="fas fa-check"></i> Approve Action</button>`
            }
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading recommendations:', err);
    container.innerHTML = `<div class="card"><p class="loading-cell" style="color:#EF4444;"><i class="fas fa-exclamation-triangle"></i> Failed to fetch recommendations: ${escapeHtml(err.message)}</p></div>`;
    showToast(`API Error: ${err.message}`, 'error');
  }
}

async function triggerApproveRec(recId) {
  try {
    showToast(`Approving Recommendation #${recId}...`, 'info');
    const result = await API.approveRecommendation(recId);
    showToast(`Success: ${result.message || 'Recommendation approved'}`, 'success');
    loadRecommendations();
  } catch (err) {
    showToast(`Approval Error: ${err.message}`, 'error');
  }
}

/**
 * 8. Load Compliance View
 */
async function loadCompliance() {
  const tbody = document.getElementById('compliance-table-body');
  const badge = document.getElementById('compliance-count-badge');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="7" class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Auditing contract SLA & compliance...</td></tr>';

  try {
    const records = await API.getCompliance();
    if (badge) badge.textContent = `${records.length} Records`;

    if (!records || records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">No compliance audit records found.</td></tr>';
      return;
    }

    tbody.innerHTML = records.map(c => {
      const status = (c.status || c.compliance_status || 'COMPLIANT').toUpperCase();
      const penalty = c.penalty_risk || 0;

      return `
        <tr>
          <td><strong>#${c.id}</strong></td>
          <td><strong>${escapeHtml(c.policy_name || c.title || 'Policy Rule')}</strong></td>
          <td><span class="badge-count">${escapeHtml(c.category || 'POLICY')}</span></td>
          <td>${escapeHtml(c.entity_name || 'Supply Line')}</td>
          <td><strong style="color:${penalty > 0 ? '#EF4444' : '#10B981'};">$${penalty.toLocaleString()}</strong></td>
          <td>${escapeHtml(c.required_action || c.required_actions || 'None required')}</td>
          <td><span class="badge-sev ${status === 'COMPLIANT' ? 'badge-sev-low' : 'badge-sev-critical'}">${status}</span></td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading compliance:', err);
    tbody.innerHTML = `<tr><td colspan="7" class="loading-cell" style="color:#EF4444;"><i class="fas fa-exclamation-triangle"></i> Failed to audit compliance: ${escapeHtml(err.message)}</td></tr>`;
    showToast(`API Error: ${err.message}`, 'error');
  }
}

/* (duplicate loadNews removed — canonical version is below in PART 2G) */

/**
 * 10. Load Executive Analytics & Audit Report View
 */
async function loadReports() {
  const container = document.getElementById('report-container');
  if (!container) return;

  container.innerHTML = '<div class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Generating executive report summary...</div>';

  try {
    const report = await API.getReport();

    if (!report) {
      container.innerHTML = '<p class="loading-cell">Unable to generate report.</p>';
      return;
    }

    const rSum = report.risk_summary || {};
    const sPerf = report.supplier_performance || {};
    const shpStat = report.shipment_status || {};
    const recs = report.recommendations_audit || [];
    const scens = report.scenario_evaluations || [];

    container.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:2px solid var(--primary); padding-bottom:12px;">
        <div>
          <h2 style="font-size:1.4rem; font-weight:800; color:var(--text);">${escapeHtml(report.report_title || 'AegisFlow Executive Audit Report')}</h2>
          <span style="font-size:0.8rem; color:var(--text-muted);">Generated on ${report.generated_at || new Date().toISOString().split('T')[0]}</span>
        </div>
        <span class="badge-count" style="font-size:0.85rem; padding:6px 16px;">AI Audit Complete</span>
      </div>

      <div class="report-section">
        <h3><i class="fas fa-shield-alt"></i> Risk Summary & Threat Telemetry</h3>
        <p>Active Risks: <strong>${rSum.total_active_risks ?? 0}</strong> | Critical Threats: <strong>${rSum.high_severity_count ?? 0}</strong> | Primary Focus: <strong>${escapeHtml(rSum.top_risk || 'None')}</strong></p>
      </div>

      <div class="report-section">
        <h3><i class="fas fa-building"></i> Supplier Reliability Index</h3>
        <p>Total Suppliers Tracked: <strong>${sPerf.total_suppliers ?? 0}</strong> | Average Reliability: <strong>${sPerf.average_reliability ?? 95}%</strong></p>
        ${sPerf.at_risk_suppliers && sPerf.at_risk_suppliers.length > 0 ?
          `<p style="color:#EF4444;">Suppliers Requiring Dual-Sourcing: <strong>${sPerf.at_risk_suppliers.join(', ')}</strong></p>` :
          '<p style="color:#10B981;">All suppliers operating within target reliability thresholds.</p>'
        }
      </div>

      <div class="report-section">
        <h3><i class="fas fa-truck"></i> Freight & Logistics Performance</h3>
        <p>Active Shipments: <strong>${shpStat.total_shipments ?? 0}</strong> | At-Risk Shipments: <strong>${shpStat.at_risk_count ?? 0}</strong> | Delayed Shipments: <strong>${shpStat.delayed_count ?? 0}</strong></p>
      </div>

      <div class="report-section">
        <h3><i class="fas fa-robot"></i> IBM AI Recommendations Audit</h3>
        <div class="table-wrapper">
          <table class="data-table">
            <thead><tr><th>Action Title</th><th>Status</th><th>Confidence</th><th>Expected Impact</th></tr></thead>
            <tbody>
              ${recs.length > 0 ? recs.map(r => `
                <tr>
                  <td><strong>${escapeHtml(r.action)}</strong></td>
                  <td><span class="badge-sev ${r.status === 'APPROVED' ? 'badge-sev-low' : 'badge-sev-medium'}">${escapeHtml(r.status)}</span></td>
                  <td>${escapeHtml(r.confidence)}</td>
                  <td>${escapeHtml(r.impact)}</td>
                </tr>
              `).join('') : '<tr><td colspan="4" class="loading-cell">No recommendations audited.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      <div class="report-section">
        <h3><i class="fas fa-dice"></i> What-If Trade-Off Scenario Analysis</h3>
        <div class="table-wrapper">
          <table class="data-table">
            <thead><tr><th>Scenario Strategy</th><th>Cost Delta</th><th>Delay Impact</th><th>Risk Score</th><th>Recommendation</th></tr></thead>
            <tbody>
              ${scens.length > 0 ? scens.map(sc => `
                <tr>
                  <td><strong>${escapeHtml(sc.option)}</strong></td>
                  <td>${escapeHtml(sc.cost_delta)}</td>
                  <td>+${sc.delay_days} Days</td>
                  <td>${sc.risk_score} / 100</td>
                  <td>${sc.recommended ? '<strong style="color:#10B981;">RECOMMENDED</strong>' : 'Alternative'}</td>
                </tr>
              `).join('') : '<tr><td colspan="5" class="loading-cell">No scenario evaluations audited.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    console.error('Error generating executive report:', err);
    container.innerHTML = `<p class="loading-cell" style="color:#EF4444;"><i class="fas fa-exclamation-triangle"></i> Failed to generate report: ${escapeHtml(err.message)}</p>`;
    showToast(`API Error: ${err.message}`, 'error');
  }
}

/**
 * Toast Notification Utility
 */
function showToast(message, type = 'info') {
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    document.body.appendChild(toastContainer);
  }

  const bgColor = type === 'error' ? '#DC2626' : type === 'success' ? '#059669' : '#4F46E5';
  const icon = type === 'error' ? 'fa-exclamation-triangle' : type === 'success' ? 'fa-check-circle' : 'fa-info-circle';

  const toast = document.createElement('div');
  toast.className = 'toast-item';
  toast.style.background = bgColor;
  toast.innerHTML = `<i class="fas ${icon}"></i><span>${escapeHtml(message)}</span>`;

  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 350);
  }, 4500);
}

function escapeHtml(str) {
  if (typeof str !== 'string') return str;
  return str.replace(/[&<>"']/g, (m) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }[m]));
}

/* ============================================================
   TYPHOON DEMO MODAL
   ============================================================ */

async function triggerTyphoonDemo() {
  if (typeof API === 'undefined') {
    showToast('API Client module not loaded.', 'error');
    return;
  }

  // Show modal immediately with loading state
  _showTyphoonModal({ loading: true });

  try {
    showToast('Running Typhoon Disruption Scenario via AI pipeline...', 'info');
    const result = await API.triggerTyphoonDemo();
    showToast('Typhoon scenario executed. Updating dashboard...', 'success');
    // Re-render modal with real API data
    _showTyphoonModal({ loading: false, data: result });
    // Refresh dashboard in background so KPIs update
    loadDashboard();
  } catch (error) {
    showToast(`Typhoon scenario error: ${error.message}`, 'error');
    // Show modal with static fallback data so demo still works
    _showTyphoonModal({ loading: false, data: null, error: error.message });
  }
}

function _showTyphoonModal({ loading = false, data = null, error = null }) {
  // Remove any existing modal
  const existing = document.getElementById('typhoon-demo-modal');
  if (existing) existing.remove();

  const overlay = document.createElement('div');
  overlay.id = 'typhoon-demo-modal';
  overlay.className = 'aegis-modal-overlay';
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.remove();
  });

  // Extract payload fields (backend returns {status, message, payload})
  const payload = (data && data.payload) ? data.payload : null;

  // Build body content
  let bodyHtml = '';

  if (loading) {
    bodyHtml = `
      <div style="text-align:center; padding:40px 20px;">
        <i class="fas fa-spinner fa-spin" style="font-size:2rem; color:var(--primary); margin-bottom:16px;"></i>
        <p style="color:var(--text-secondary); font-size:0.9rem;">Running IBM Granite AI typhoon scenario pipeline...<br>Analyzing affected suppliers, shipments, and risks.</p>
      </div>`;
  } else {
    // ── Disruption Event Header ───────────────────────────────────────────
    const eventName  = (payload && payload.event_name)    || 'Super Typhoon — East China Sea';
    const location   = (payload && payload.location)      || 'Taiwan Strait / South China Sea';
    const riskLevel  = (payload && payload.risk_level)    || 'CRITICAL';
    const windSpeed  = (payload && payload.wind_speed)    || '195 km/h';
    const delay      = (payload && payload.delay_days)    || '8–12';
    const finImpact  = (payload && payload.financial_impact) || '$275,000–$420,000';
    const category   = (payload && payload.typhoon_cat)   || 'Category 4';

    const riskBadgeClass = riskLevel === 'CRITICAL' ? 'badge-sev-critical'
                         : riskLevel === 'HIGH'     ? 'badge-sev-high'
                         : 'badge-sev-medium';

    // ── Affected Suppliers ────────────────────────────────────────────────
    const affectedSuppliers = (payload && Array.isArray(payload.affected_suppliers))
      ? payload.affected_suppliers
      : [
          { name: 'ABC Electronics Co.',  country: 'Taiwan',     risk: 'CRITICAL' },
          { name: 'Apex Semiconductor AG', country: 'South Korea', risk: 'HIGH'    },
          { name: 'Global Tech Modules',  country: 'Malaysia',   risk: 'MEDIUM'   },
        ];

    const suppliersHtml = affectedSuppliers.map(s => {
      const sc = (s.risk||'').toUpperCase() === 'CRITICAL' ? 'badge-sev-critical'
               : (s.risk||'').toUpperCase() === 'HIGH'     ? 'badge-sev-high'
               : 'badge-sev-medium';
      return `
        <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:var(--surface); border-radius:8px; margin-bottom:6px;">
          <div>
            <strong style="font-size:0.85rem;">${escapeHtml(s.name || s.supplier_name || 'Supplier')}</strong>
            <span style="font-size:0.75rem; color:var(--text-muted); margin-left:8px;"><i class="fas fa-map-marker-alt"></i> ${escapeHtml(s.country || '—')}</span>
          </div>
          <span class="badge-sev ${sc}">${escapeHtml(s.risk || 'HIGH')}</span>
        </div>`;
    }).join('');

    // ── Affected Shipments ────────────────────────────────────────────────
    const affectedShipments = (payload && Array.isArray(payload.affected_shipments))
      ? payload.affected_shipments
      : [
          { code: 'SHP-9021', delay: 8, status: 'AT_RISK',  route: 'Kaohsiung → Los Angeles'  },
          { code: 'SHP-9022', delay: 10, status: 'AT_RISK', route: 'Keelung → Hamburg'         },
          { code: 'SHP-9024', delay: 12, status: 'DELAYED', route: 'Busan → Long Beach'        },
        ];

    const shipmentsHtml = affectedShipments.map(sh => {
      const isDelayed = (sh.status||'').toUpperCase() === 'DELAYED';
      return `
        <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:var(--surface); border-radius:8px; margin-bottom:6px;">
          <div>
            <strong style="font-size:0.85rem; color:${isDelayed ? '#EF4444' : '#F59E0B'};">${escapeHtml(sh.code || sh.shipment_code || '—')}</strong>
            <span style="font-size:0.75rem; color:var(--text-muted); margin-left:8px;">${escapeHtml(sh.route || sh.origin || '—')}</span>
          </div>
          <span style="font-size:0.8rem; font-weight:700; color:${isDelayed ? '#EF4444' : '#F59E0B'};">+${sh.delay || sh.delay_days || 0} Days</span>
        </div>`;
    }).join('');

    // ── Recommended Actions ───────────────────────────────────────────────
    const recommendations = (payload && Array.isArray(payload.recommendations))
      ? payload.recommendations
      : [
          'Activate pre-approved alternate supplier in Vietnam (Supplier XYZ Logistics) immediately.',
          'Reroute active sea freight via southern lane (Luzon Strait bypass) — adds 2 days, avoids direct typhoon path.',
          'Expedite air freight for top-3 critical SKUs: Microcontroller X1, Power Regulator P1, Memory Module M8.',
          'Notify customers of 8–12 day delivery delay. Issue force majeure communication to Tier-1 accounts.',
          'Pre-position safety stock at San Jose inland warehouse from existing buffer inventory.',
        ];

    const recsHtml = recommendations.map(r => `
      <div style="display:flex; gap:10px; align-items:flex-start; padding:8px 0; border-bottom:1px solid var(--border-light);">
        <i class="fas fa-check-circle" style="color:var(--success); margin-top:2px; flex-shrink:0;"></i>
        <span style="font-size:0.84rem; color:var(--text-secondary); line-height:1.5;">${escapeHtml(typeof r === 'string' ? r : (r.action || r.text || JSON.stringify(r)))}</span>
      </div>`).join('');

    // ── AI Analysis Text ──────────────────────────────────────────────────
    const aiAnalysis = (payload && (payload.ai_analysis || payload.analysis || payload.reasoning || payload.summary))
      || 'IBM Granite AI assessment: Typhoon tracking indicates direct impact on Taiwan Strait maritime corridor within 48 hours. Primary risk is port closure at Kaohsiung (72-hour window) and Keelung. Secondary risk is vessel routing disruption across East China Sea lanes. Production lines dependent on Taiwan-origin semiconductors face critical stockout within 3–5 days if no action is taken. Immediate dual-sourcing activation is the highest-ROI mitigation strategy.';

    const errorBanner = error ? `
      <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:10px 14px; margin-bottom:16px; font-size:0.8rem; color:#B91C1C;">
        <i class="fas fa-exclamation-triangle" style="margin-right:6px;"></i>
        Backend pipeline error — showing baseline scenario data. (${escapeHtml(error)})
      </div>` : '';

    const statusBadge = data
      ? `<span class="badge-sev badge-sev-low"><i class="fas fa-check-circle"></i> Pipeline Executed</span>`
      : `<span class="badge-sev badge-sev-warn"><i class="fas fa-info-circle"></i> Baseline Scenario</span>`;

    bodyHtml = `
      ${errorBanner}

      <!-- Event Header -->
      <div style="background:linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border-radius:12px; padding:20px 22px; margin-bottom:20px; color:#fff;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
          <div>
            <div style="font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.8px; color:#94A3B8; margin-bottom:4px;">
              <i class="fas fa-bolt" style="color:#F59E0B; margin-right:4px;"></i> LIVE DISRUPTION EVENT
            </div>
            <h3 style="font-size:1.1rem; font-weight:800; margin-bottom:4px;">${escapeHtml(eventName)}</h3>
            <div style="font-size:0.8rem; color:#94A3B8;"><i class="fas fa-map-marker-alt" style="margin-right:4px;"></i>${escapeHtml(location)}</div>
          </div>
          <span class="badge-sev ${riskBadgeClass}" style="flex-shrink:0;">${escapeHtml(riskLevel)}</span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-top:8px;">
          <div style="text-align:center; background:rgba(255,255,255,0.07); border-radius:8px; padding:10px;">
            <div style="font-size:0.65rem; color:#94A3B8; text-transform:uppercase; margin-bottom:4px;">Category</div>
            <div style="font-size:1rem; font-weight:800; color:#F59E0B;">${escapeHtml(category)}</div>
          </div>
          <div style="text-align:center; background:rgba(255,255,255,0.07); border-radius:8px; padding:10px;">
            <div style="font-size:0.65rem; color:#94A3B8; text-transform:uppercase; margin-bottom:4px;">Expected Delay</div>
            <div style="font-size:1rem; font-weight:800; color:#F87171;">+${escapeHtml(String(delay))} Days</div>
          </div>
          <div style="text-align:center; background:rgba(255,255,255,0.07); border-radius:8px; padding:10px;">
            <div style="font-size:0.65rem; color:#94A3B8; text-transform:uppercase; margin-bottom:4px;">Financial Impact</div>
            <div style="font-size:0.9rem; font-weight:800; color:#FB923C;">${escapeHtml(finImpact)}</div>
          </div>
        </div>
      </div>

      <!-- Two-column grid -->
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px;">

        <!-- Affected Suppliers -->
        <div>
          <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-muted); margin-bottom:8px;">
            <i class="fas fa-industry" style="color:#EF4444; margin-right:4px;"></i> Affected Suppliers
          </div>
          ${suppliersHtml || '<p style="font-size:0.8rem; color:var(--text-muted);">No supplier data.</p>'}
        </div>

        <!-- Affected Shipments -->
        <div>
          <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-muted); margin-bottom:8px;">
            <i class="fas fa-ship" style="color:#F59E0B; margin-right:4px;"></i> At-Risk Shipments
          </div>
          ${shipmentsHtml || '<p style="font-size:0.8rem; color:var(--text-muted);">No shipment data.</p>'}
        </div>
      </div>

      <!-- AI Analysis -->
      <div style="background:rgba(79,70,229,0.05); border:1px solid rgba(79,70,229,0.2); border-radius:10px; padding:14px 16px; margin-bottom:16px;">
        <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--primary); margin-bottom:8px;">
          <i class="fas fa-microchip" style="margin-right:4px;"></i> IBM Granite AI Assessment
        </div>
        <p style="font-size:0.84rem; color:var(--text-secondary); line-height:1.6;">${escapeHtml(aiAnalysis)}</p>
      </div>

      <!-- Recommended Actions -->
      <div style="background:rgba(5,150,105,0.04); border:1px solid rgba(5,150,105,0.2); border-radius:10px; padding:14px 16px; margin-bottom:16px;">
        <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--success); margin-bottom:8px;">
          <i class="fas fa-shield-alt" style="margin-right:4px;"></i> AI-Recommended Mitigation Actions
        </div>
        ${recsHtml}
      </div>

      <!-- Footer: quick actions -->
      <div style="display:flex; gap:10px; justify-content:flex-end; flex-wrap:wrap;">
        ${statusBadge}
        <button class="btn-outline" onclick="document.getElementById('typhoon-demo-modal').remove(); navigateToPage('scenarios'); selectDisruptionType('TYPHOON_DISRUPTION');">
          <i class="fas fa-dice"></i> View Full Scenario Options
        </button>
        <button class="btn-primary" onclick="document.getElementById('typhoon-demo-modal').remove(); navigateToPage('news');">
          <i class="fas fa-newspaper"></i> View Impact Chain
        </button>
      </div>`;
  }

  overlay.innerHTML = `
    <div class="aegis-modal" style="max-width:820px; width:95%; max-height:90vh; overflow-y:auto;">
      <div class="aegis-modal-header">
        <div style="display:flex; align-items:center; gap:10px;">
          <div style="width:36px; height:36px; border-radius:10px; background:rgba(239,68,68,0.12); display:flex; align-items:center; justify-content:center;">
            <i class="fas fa-tornado" style="color:#EF4444; font-size:1.1rem;"></i>
          </div>
          <div>
            <h3 style="font-size:1rem; font-weight:800; color:var(--text); margin:0;">Typhoon Disruption Scenario</h3>
            <p style="font-size:0.72rem; color:var(--text-muted); margin:0;">AI-Powered Supply Chain Impact Analysis</p>
          </div>
        </div>
        <button onclick="document.getElementById('typhoon-demo-modal').remove();" class="aegis-modal-close" title="Close">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="aegis-modal-body">
        ${bodyHtml}
      </div>
    </div>`;

  document.body.appendChild(overlay);
}

/* ============================================================
   SUPPLIER AI ANALYSIS MODAL
   ============================================================ */

async function triggerAnalyzeSupplier(supplierId) {
  // Find cached supplier data immediately (no wait)
  const cached = _allSuppliers.find(s => s.id === supplierId);

  // Show modal right away with whatever we have cached
  _showSupplierAnalysisModal({ supplierId, supplier: cached, loading: true });

  try {
    const result = await API.analyzeSupplierRisk(supplierId);
    // Re-render modal with full data
    _showSupplierAnalysisModal({ supplierId, supplier: cached, loading: false, result });
  } catch (err) {
    _showSupplierAnalysisModal({ supplierId, supplier: cached, loading: false, result: null, error: err.message });
  }
}

function _showSupplierAnalysisModal({ supplierId, supplier, loading, result = null, error = null }) {
  const modalId = 'supplier-analysis-modal';
  const existing = document.getElementById(modalId);
  if (existing) existing.remove();

  const overlay = document.createElement('div');
  overlay.id = modalId;
  overlay.className = 'aegis-modal-overlay';
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.remove();
  });

  // Merge data: prefer API result, fall back to cached supplier
  const s = supplier || {};
  const r = result  || {};
  const name     = r.supplier_name || s.name        || `Supplier #${supplierId}`;
  const country  = s.country       || '—';
  const category = s.category      || s.supplier_category || '—';
  const rel      = r.reliability_score ?? s.reliability_score ?? null;
  const onTime   = s.on_time_delivery  ?? null;
  const qual     = s.quality_score     ?? null;
  const rawRisk  = (r.risk_level || s.current_risk_level || s.risk_level || 'LOW').toUpperCase();

  const riskBadgeClass = rawRisk === 'CRITICAL' ? 'badge-sev-critical'
                       : rawRisk === 'HIGH'     ? 'badge-sev-high'
                       : rawRisk === 'MEDIUM' || rawRisk === 'MODERATE' ? 'badge-sev-medium'
                       : 'badge-sev-low';

  // ── Risk score computation ────────────────────────────────────────────
  const riskScoreMap = { CRITICAL: 82, HIGH: 65, MEDIUM: 45, MODERATE: 45, LOW: 20 };
  const riskScore = riskScoreMap[rawRisk] || 30;

  // ── Build risk factor analysis from available data ────────────────────
  const factors = [];
  if (rel !== null) {
    if (rel < 70)  factors.push({ label: 'Reliability Score', note: `${rel}% — significantly below acceptable threshold (≥85%)`, severity: 'high'   });
    else if (rel < 85) factors.push({ label: 'Reliability Score', note: `${rel}% — below optimal threshold (≥85%)`, severity: 'medium' });
    else               factors.push({ label: 'Reliability Score', note: `${rel}% — within acceptable range`, severity: 'low'    });
  }
  if (onTime !== null) {
    if (onTime < 75)  factors.push({ label: 'On-Time Delivery', note: `${onTime}% — critical delivery performance gap`, severity: 'high'   });
    else if (onTime < 90) factors.push({ label: 'On-Time Delivery', note: `${onTime}% — below target (≥90%)`, severity: 'medium' });
    else                  factors.push({ label: 'On-Time Delivery', note: `${onTime}% — meeting delivery SLA`, severity: 'low'    });
  }
  if (qual !== null) {
    if (qual < 80)  factors.push({ label: 'Quality Score', note: `${qual}% — quality non-conformance risk`, severity: 'high'   });
    else if (qual < 95) factors.push({ label: 'Quality Score', note: `${qual}% — minor quality improvement needed`, severity: 'medium' });
    else                factors.push({ label: 'Quality Score', note: `${qual}% — quality standards met`, severity: 'low'    });
  }
  if (factors.length === 0) {
    factors.push({ label: 'Risk Level', note: `Current assessment: ${rawRisk}`, severity: rawRisk === 'CRITICAL' || rawRisk === 'HIGH' ? 'high' : rawRisk === 'MEDIUM' || rawRisk === 'MODERATE' ? 'medium' : 'low' });
  }

  const factorColor = { high: '#EF4444', medium: '#F59E0B', low: '#10B981' };
  const factorIcon  = { high: 'fa-times-circle', medium: 'fa-exclamation-circle', low: 'fa-check-circle' };

  const factorsHtml = factors.map(f => `
    <div style="display:flex; align-items:flex-start; gap:10px; padding:9px 12px; background:var(--surface); border-radius:8px; margin-bottom:6px;">
      <i class="fas ${factorIcon[f.severity]}" style="color:${factorColor[f.severity]}; margin-top:1px; flex-shrink:0;"></i>
      <div>
        <div style="font-size:0.82rem; font-weight:700; color:var(--text);">${escapeHtml(f.label)}</div>
        <div style="font-size:0.77rem; color:var(--text-muted);">${escapeHtml(f.note)}</div>
      </div>
    </div>`).join('');

  // ── Business impact ────────────────────────────────────────────────────
  const impactMap = {
    CRITICAL: 'Immediate supply chain disruption risk. Production line stoppage probable within 3–7 days if not mitigated. Financial exposure: $180,000–$320,000 in lost output and expedite costs.',
    HIGH:     'Significant supply chain pressure. Delayed deliveries and elevated cost risk. Financial exposure: $45,000–$120,000 if no corrective action taken within 14 days.',
    MEDIUM:   'Moderate risk requiring monitoring. Delivery performance trends suggest potential SLA breach within 30–60 days. Proactive sourcing review recommended.',
    MODERATE: 'Moderate risk requiring monitoring. Delivery performance trends suggest potential SLA breach within 30–60 days. Proactive sourcing review recommended.',
    LOW:      'Supplier performing within acceptable parameters. Routine monitoring sufficient. No immediate corrective action required.',
  };
  const businessImpact = impactMap[rawRisk] || 'Risk level requires assessment. Review supplier performance data for full impact determination.';

  // ── AI recommendation ─────────────────────────────────────────────────
  const recMap = {
    CRITICAL: `Activate emergency dual-sourcing from pre-qualified backup supplier immediately. Issue formal supplier corrective action request (SCAR). Consider reducing order allocation to ${name} by 50% pending remediation.`,
    HIGH:     `Schedule executive-level business review with ${name} within 10 business days. Identify backup qualified supplier for top-5 SKUs. Place 30-day safety stock buffer order.`,
    MEDIUM:   `Issue formal performance improvement notice to ${name}. Set 60-day KPI review milestone. Pre-qualify one alternate source to reduce single-supplier dependency.`,
    MODERATE: `Issue formal performance improvement notice to ${name}. Set 60-day KPI review milestone. Pre-qualify one alternate source to reduce single-supplier dependency.`,
    LOW:      `Continue standard monitoring cadence. Include ${name} in annual strategic supplier review. Confirm continued compliance with quality and delivery SLAs.`,
  };
  const aiRecommendation = recMap[rawRisk] || 'Conduct detailed supplier audit and review KPI trends before determining next steps.';

  // ── Mitigation strategy ────────────────────────────────────────────────
  const strategyMap = {
    CRITICAL: 'Immediate: Dual-source activation (Week 1) → SCAR issuance (Week 1) → Alternate supplier qualification (Weeks 2–4) → Allocation rebalancing (Month 2)',
    HIGH:     'Short-term: Safety stock buffer (Week 1–2) → Business review (Week 2) → Backup supplier identification (Month 1) → Quarterly KPI review cycle',
    MEDIUM:   'Medium-term: Performance improvement plan (Month 1) → Alternate source pre-qualification (Month 2–3) → KPI milestone review at 60 days',
    MODERATE: 'Medium-term: Performance improvement plan (Month 1) → Alternate source pre-qualification (Month 2–3) → KPI milestone review at 60 days',
    LOW:      'Standard: Annual strategic review → Routine KPI monitoring → SLA compliance confirmation',
  };
  const mitigationStrategy = strategyMap[rawRisk] || 'Assess and define mitigation roadmap based on detailed audit findings.';

  // ── Confidence score ──────────────────────────────────────────────────
  const hasDetailedData = (rel !== null) && (onTime !== null) && (qual !== null);
  const confidenceScore = hasDetailedData ? 91 : 74;
  const confColor = confidenceScore >= 85 ? '#10B981' : '#F59E0B';

  // ── Score bar helper ──────────────────────────────────────────────────
  const scoreBar = (val, color) => val !== null ? `
    <div style="display:flex; align-items:center; gap:10px;">
      <div style="flex:1; height:6px; background:var(--border); border-radius:3px; overflow:hidden;">
        <div style="width:${val}%; height:100%; background:${color}; border-radius:3px;"></div>
      </div>
      <span style="font-size:0.8rem; font-weight:700; color:${color}; min-width:36px;">${val}%</span>
    </div>` : `<span style="font-size:0.8rem; color:var(--text-muted);">—</span>`;

  const relColor  = rel   !== null ? (rel   >= 85 ? '#10B981' : rel   >= 70 ? '#F59E0B' : '#EF4444') : '#94A3B8';
  const otdColor  = onTime !== null ? (onTime >= 90 ? '#10B981' : onTime >= 75 ? '#F59E0B' : '#EF4444') : '#94A3B8';
  const qualColor = qual  !== null ? (qual  >= 95 ? '#10B981' : qual  >= 80 ? '#F59E0B' : '#EF4444') : '#94A3B8';

  let bodyHtml = '';

  if (loading) {
    bodyHtml = `
      <div style="text-align:center; padding:40px 20px;">
        <i class="fas fa-spinner fa-spin" style="font-size:2rem; color:var(--primary); margin-bottom:16px;"></i>
        <p style="color:var(--text-secondary); font-size:0.9rem;">Running AI risk analysis for <strong>${escapeHtml(name)}</strong>...</p>
      </div>`;
  } else {
    const errorBanner = error ? `
      <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:10px 14px; margin-bottom:16px; font-size:0.8rem; color:#B91C1C;">
        <i class="fas fa-exclamation-triangle" style="margin-right:6px;"></i>
        AI service error — analysis generated from available supplier data. (${escapeHtml(error)})
      </div>` : '';

    bodyHtml = `
      ${errorBanner}

      <!-- Supplier Identity Header -->
      <div style="display:flex; justify-content:space-between; align-items:flex-start; padding:16px 18px; background:var(--surface); border-radius:10px; margin-bottom:18px; gap:12px; flex-wrap:wrap;">
        <div>
          <h3 style="font-size:1.05rem; font-weight:800; color:var(--text); margin:0 0 4px 0;">${escapeHtml(name)}</h3>
          <div style="font-size:0.8rem; color:var(--text-muted); display:flex; gap:14px; flex-wrap:wrap;">
            <span><i class="fas fa-map-marker-alt" style="margin-right:4px;"></i>${escapeHtml(country)}</span>
            <span><i class="fas fa-tag" style="margin-right:4px;"></i>${escapeHtml(category)}</span>
            <span><i class="fas fa-hashtag" style="margin-right:4px;"></i>ID: ${supplierId}</span>
          </div>
        </div>
        <div style="text-align:right; flex-shrink:0;">
          <div style="font-size:0.65rem; text-transform:uppercase; font-weight:700; color:var(--text-muted); margin-bottom:4px;">Risk Level</div>
          <span class="badge-sev ${riskBadgeClass}" style="font-size:0.85rem; padding:5px 14px;">${rawRisk}</span>
          <div style="font-size:0.7rem; color:var(--text-muted); margin-top:4px;">Score: <strong style="color:var(--text);">${riskScore} / 100</strong></div>
        </div>
      </div>

      <!-- KPI scores -->
      <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:18px;">
        <div style="background:var(--bg-white); border:1px solid var(--border); border-radius:10px; padding:14px;">
          <div style="font-size:0.65rem; text-transform:uppercase; font-weight:700; color:var(--text-muted); margin-bottom:8px;"><i class="fas fa-star" style="margin-right:4px;"></i>Reliability</div>
          ${scoreBar(rel, relColor)}
        </div>
        <div style="background:var(--bg-white); border:1px solid var(--border); border-radius:10px; padding:14px;">
          <div style="font-size:0.65rem; text-transform:uppercase; font-weight:700; color:var(--text-muted); margin-bottom:8px;"><i class="fas fa-clock" style="margin-right:4px;"></i>On-Time Delivery</div>
          ${scoreBar(onTime, otdColor)}
        </div>
        <div style="background:var(--bg-white); border:1px solid var(--border); border-radius:10px; padding:14px;">
          <div style="font-size:0.65rem; text-transform:uppercase; font-weight:700; color:var(--text-muted); margin-bottom:8px;"><i class="fas fa-medal" style="margin-right:4px;"></i>Quality Score</div>
          ${scoreBar(qual, qualColor)}
        </div>
      </div>

      <!-- Risk Summary -->
      <div style="margin-bottom:16px;">
        <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-muted); margin-bottom:8px;">
          <i class="fas fa-shield-alt" style="color:var(--primary); margin-right:4px;"></i> Risk Assessment Summary
        </div>
        <div style="background:rgba(79,70,229,0.04); border:1px solid rgba(79,70,229,0.15); border-radius:10px; padding:12px 14px;">
          <p style="font-size:0.84rem; color:var(--text-secondary); line-height:1.6; margin:0;">
            ${escapeHtml(name)} is currently assessed at <strong>${rawRisk}</strong> risk level
            ${rel !== null ? ` with a reliability score of <strong>${rel}%</strong>` : ''}${onTime !== null ? `, on-time delivery of <strong>${onTime}%</strong>` : ''}${qual !== null ? `, and quality score of <strong>${qual}%</strong>` : ''}.
            Risk score: <strong>${riskScore}/100</strong>.
          </p>
        </div>
      </div>

      <!-- Key Risk Factors -->
      <div style="margin-bottom:16px;">
        <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-muted); margin-bottom:8px;">
          <i class="fas fa-search" style="color:#F59E0B; margin-right:4px;"></i> Key Risk Factors
        </div>
        ${factorsHtml}
      </div>

      <!-- Business Impact -->
      <div style="margin-bottom:16px;">
        <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-muted); margin-bottom:8px;">
          <i class="fas fa-chart-line" style="color:#EF4444; margin-right:4px;"></i> Potential Business Impact
        </div>
        <div style="background:#FFF7ED; border:1px solid #FED7AA; border-radius:10px; padding:12px 14px;">
          <p style="font-size:0.84rem; color:#92400E; line-height:1.6; margin:0;">${escapeHtml(businessImpact)}</p>
        </div>
      </div>

      <!-- AI Recommendation -->
      <div style="margin-bottom:16px;">
        <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-muted); margin-bottom:8px;">
          <i class="fas fa-robot" style="color:var(--primary); margin-right:4px;"></i> AI Recommended Action
        </div>
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:12px 14px;">
          <p style="font-size:0.84rem; color:#166534; line-height:1.6; margin:0;">${escapeHtml(aiRecommendation)}</p>
        </div>
      </div>

      <!-- Mitigation Strategy -->
      <div style="margin-bottom:18px;">
        <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-muted); margin-bottom:8px;">
          <i class="fas fa-road" style="color:#0891B2; margin-right:4px;"></i> Suggested Mitigation Roadmap
        </div>
        <div style="background:#F0F9FF; border:1px solid #BAE6FD; border-radius:10px; padding:12px 14px;">
          <p style="font-size:0.84rem; color:#0C4A6E; line-height:1.7; margin:0;">${escapeHtml(mitigationStrategy)}</p>
        </div>
      </div>

      <!-- Footer: confidence + actions -->
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; border-top:1px solid var(--border); padding-top:14px;">
        <div style="font-size:0.8rem; color:var(--text-muted);">
          <i class="fas fa-brain" style="color:${confColor}; margin-right:4px;"></i>
          AI Confidence: <strong style="color:${confColor};">${confidenceScore}%</strong>
          <span style="margin-left:6px; font-size:0.72rem;">${hasDetailedData ? '(Full KPI data available)' : '(Partial data — full analysis requires all KPI fields)'}</span>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <button class="btn-outline" onclick="document.getElementById('${modalId}').remove(); navigateToPage('risks');">
            <i class="fas fa-shield-alt"></i> View Risks
          </button>
          <button class="btn-primary" onclick="document.getElementById('${modalId}').remove(); navigateToPage('map'); setTimeout(()=>{ const sel=document.getElementById('map-supplier-select'); if(sel){sel.value=${supplierId}; loadSupplierOnMap(${supplierId});} },300);">
            <i class="fas fa-map-marked-alt"></i> View on Map
          </button>
        </div>
      </div>`;
  }

  overlay.innerHTML = `
    <div class="aegis-modal" style="max-width:740px; width:95%; max-height:92vh; overflow-y:auto;">
      <div class="aegis-modal-header">
        <div style="display:flex; align-items:center; gap:10px;">
          <div style="width:36px; height:36px; border-radius:10px; background:rgba(79,70,229,0.1); display:flex; align-items:center; justify-content:center;">
            <i class="fas fa-robot" style="color:var(--primary); font-size:1.1rem;"></i>
          </div>
          <div>
            <h3 style="font-size:1rem; font-weight:800; color:var(--text); margin:0;">AI Supplier Analysis</h3>
            <p style="font-size:0.72rem; color:var(--text-muted); margin:0;">${escapeHtml(loading ? 'Loading...' : name)} — IBM Granite Risk Intelligence</p>
          </div>
        </div>
        <button onclick="document.getElementById('${modalId}').remove();" class="aegis-modal-close" title="Close">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="aegis-modal-body">
        ${bodyHtml}
      </div>
    </div>`;

  document.body.appendChild(overlay);
}

// Export function stubs
function exportViewData(viewName) {
  showToast(`Exporting ${viewName} dataset to JSON/CSV...`, 'success');
}

/* ============================================
   AI CHATBOT CONTROLLER MODULE
   ============================================ */
let chatHistory = [];
// Persist the IBM Orchestrate thread_id across turns so the
// agent can maintain conversation context.
let orchestrateThreadId = null;

function initAIChatbot() {
  const toggleBtn = document.getElementById('ai-chat-toggle-btn');
  const chatPanel = document.getElementById('ai-chat-panel');
  const closeBtn = document.getElementById('chat-close-btn');
  const clearBtn = document.getElementById('chat-clear-btn');
  const sendBtn = document.getElementById('chat-send-btn');
  const inputField = document.getElementById('chat-input-field');

  if (!toggleBtn || !chatPanel) return;

  toggleBtn.addEventListener('click', () => {
    chatPanel.classList.toggle('active');
    if (chatPanel.classList.contains('active') && inputField) {
      inputField.focus();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      chatPanel.classList.remove('active');
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      const messagesContainer = document.getElementById('chat-messages');
      if (messagesContainer) {
        messagesContainer.innerHTML = `
          <div class="chat-msg system-welcome">
            <div class="chat-msg-avatar"><i class="fas fa-robot"></i></div>
            <div class="chat-msg-content">
              <p>👋 Conversation cleared. Ask me anything about your supply chain intelligence!</p>
            </div>
          </div>
        `;
      }
      chatHistory = [];
      orchestrateThreadId = null;
    });
  }

  if (sendBtn && inputField) {
    sendBtn.addEventListener('click', handleChatSubmit);
    inputField.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleChatSubmit();
      }
    });
  }
}

async function handleChatSubmit() {
  const inputField = document.getElementById('chat-input-field');
  const sendBtn = document.getElementById('chat-send-btn');
  if (!inputField) return;

  const userMsg = inputField.value.trim();
  if (!userMsg) return;

  inputField.value = '';
  inputField.disabled = true;
  if (sendBtn) sendBtn.disabled = true;

  appendChatMessage('user', userMsg);

  // Show typing indicator bubble
  const typingId = showTypingBubble();
  showChatToolIndicator('Connecting to IBM watsonx Orchestrate...');

  try {
    // Brief delay so the typing bubble is visible before the network call
    await new Promise(r => setTimeout(r, 400));
    showChatToolIndicator('AegisFlow Supply Chain Agent is working...');

    const data = await API.chatWithOrchestrate(
      userMsg,
      chatHistory,
      orchestrateThreadId
    );

    // Persist thread_id for conversation continuity
    if (data.thread_id) {
      orchestrateThreadId = data.thread_id;
    }

    removeTypingBubble(typingId);
    hideChatToolIndicator();

    const toolsUsed = data.tools_used || [];
    const responseText = data.response || 'No response generated.';

    appendChatMessage('assistant', responseText, toolsUsed);

    chatHistory.push({ role: 'user', content: userMsg });
    chatHistory.push({ role: 'assistant', content: responseText });
  } catch (err) {
    removeTypingBubble(typingId);
    hideChatToolIndicator();
    appendChatMessage('assistant', `⚠️ **Error communicating with IBM watsonx Orchestrate:** ${escapeHtml(err.message)}`);
  } finally {
    inputField.disabled = false;
    if (sendBtn) sendBtn.disabled = false;
    inputField.focus();
  }
}

function sendSuggestedQuestion(questionText) {
  const inputField = document.getElementById('chat-input-field');
  const chatPanel = document.getElementById('ai-chat-panel');
  if (chatPanel && !chatPanel.classList.contains('active')) {
    chatPanel.classList.add('active');
  }
  if (inputField) {
    inputField.value = questionText;
    handleChatSubmit();
  }
}

/**
 * Render lightweight markdown inside the chat bubbles.
 * Supports: ## headings, **bold**, bullet lines (•/-/*), numbered lists,
 *           horizontal rules (---), line breaks.
 */
function renderChatMarkdown(text) {
  // Escape HTML first, then apply markdown patterns
  let html = text
    // Escape special HTML characters
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Horizontal rule
    .replace(/^---+\s*$/gm, '<hr class="chat-hr">')
    // ## Headings
    .replace(/^##\s+(.+)$/gm, '<h4 class="chat-heading">$1</h4>')
    // **bold**
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Numbered list items: "1. text"
    .replace(/^\d+\.\s+(.+)$/gm, '<div class="chat-list-item chat-numbered">$1</div>')
    // Bullet lines starting with •, -, or *
    .replace(/^[•\-\*]\s+(.+)$/gm, '<div class="chat-list-item">$1</div>')
    // Plain line breaks
    .replace(/\n/g, '<br>');

  return html;
}

function appendChatMessage(sender, text, toolsUsed = []) {
  const messagesContainer = document.getElementById('chat-messages');
  if (!messagesContainer) return;

  const msgDiv = document.createElement('div');
  msgDiv.className = `chat-msg ${sender}`;

  const avatarDiv = document.createElement('div');
  avatarDiv.className = 'chat-msg-avatar';
  avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

  const contentDiv = document.createElement('div');
  contentDiv.className = 'chat-msg-content';

  if (sender === 'assistant') {
    contentDiv.innerHTML = renderChatMarkdown(text);
  } else {
    // User messages: simple escape + line breaks
    contentDiv.innerHTML = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
  }

  if (toolsUsed && toolsUsed.length > 0) {
    const toolsTag = document.createElement('div');
    toolsTag.className = 'chat-tools-tag';
    toolsTag.innerHTML = `<i class="fas fa-bolt"></i> ${toolsUsed.map(t => t.replace(/&/g,'&amp;').replace(/</g,'&lt;')).join(' &middot; ')}`;
    contentDiv.appendChild(toolsTag);
  }

  msgDiv.appendChild(avatarDiv);
  msgDiv.appendChild(contentDiv);
  messagesContainer.appendChild(msgDiv);

  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/** Show an animated typing bubble; returns a unique ID so it can be removed. */
function showTypingBubble() {
  const messagesContainer = document.getElementById('chat-messages');
  if (!messagesContainer) return null;

  const id = 'typing-' + Date.now();
  const div = document.createElement('div');
  div.className = 'chat-msg assistant';
  div.id = id;
  div.innerHTML = `
    <div class="chat-msg-avatar"><i class="fas fa-robot"></i></div>
    <div class="chat-msg-content chat-typing-bubble">
      <span class="chat-typing-dot"></span>
      <span class="chat-typing-dot"></span>
      <span class="chat-typing-dot"></span>
    </div>`;
  messagesContainer.appendChild(div);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  return id;
}

/** Remove the typing bubble added by showTypingBubble(). */
function removeTypingBubble(id) {
  if (!id) return;
  const el = document.getElementById(id);
  if (el) el.remove();
}

function showChatToolIndicator(text) {
  const indicator = document.getElementById('chat-tool-indicator');
  const textSpan = document.getElementById('chat-tool-text');
  if (indicator && textSpan) {
    textSpan.innerText = text;
    indicator.classList.remove('hidden');
  }
}

function hideChatToolIndicator() {
  const indicator = document.getElementById('chat-tool-indicator');
  if (indicator) {
    indicator.classList.add('hidden');
  }
}

// Initialize AI Chatbot on DOM Content Loaded
document.addEventListener('DOMContentLoaded', () => {
  initAIChatbot();
});

/* ============================================
   SUPPLY CHAIN MAP CONTROLLER (PART 2A - 2F)
   ============================================ */
let mapInstance = null;
let mapMarkers = [];
let mapPolylines = [];
let mapSuppliersData = [];

async function loadSupplyChainMap() {
  const mapContainer = document.getElementById('leaflet-map');
  const selectElem = document.getElementById('map-supplier-select');
  if (!mapContainer || !selectElem) return;

  // Initialize Leaflet map if not already created
  if (!mapInstance && typeof L !== 'undefined') {
    mapInstance = L.map('leaflet-map').setView([20.0, 30.0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(mapInstance);
  } else if (mapInstance) {
    setTimeout(() => mapInstance.invalidateSize(), 200);
  }

  try {
    mapSuppliersData = await API.getSuppliers();
    if (!mapSuppliersData || mapSuppliersData.length === 0) {
      selectElem.innerHTML = '<option value="">No suppliers available</option>';
      return;
    }

    selectElem.innerHTML = '<option value="">-- Choose Supplier from Registry --</option>' +
      mapSuppliersData.map(s => `<option value="${s.id}">${escapeHtml(s.name)} (${escapeHtml(s.country)})</option>`).join('');

    // Default select first supplier if none selected
    if (!selectElem.value && mapSuppliersData.length > 0) {
      selectElem.value = mapSuppliersData[0].id;
    }

    if (selectElem.value) {
      await onMapSupplierSelected(selectElem.value);
    }
  } catch (err) {
    console.error('Error loading supply chain map:', err);
    showToast(`Failed to load supply chain map: ${err.message}`, 'error');
  }
}

async function onMapSupplierSelected(supplierId) {
  if (!supplierId) return;
  const sId = parseInt(supplierId, 10);
  const supplier = mapSuppliersData.find(s => s.id === sId);
  if (!supplier) return;

  // Clear existing markers & lines
  mapMarkers.forEach(m => mapInstance.removeLayer(m));
  mapPolylines.forEach(p => mapInstance.removeLayer(p));
  mapMarkers = [];
  mapPolylines = [];

  // Render Supplier Details Card (PART 2B)
  const supplierRiskLvl = (supplier.current_risk_level || supplier.risk_level || 'LOW').toUpperCase();
  const supplierRiskBadge = document.getElementById('map-supplier-risk-badge');
  if (supplierRiskBadge) {
    supplierRiskBadge.innerText = supplierRiskLvl;
    supplierRiskBadge.className = `badge-count badge-${supplierRiskLvl.toLowerCase()}`;
  }

  const deliveryTime = (100 - (supplier.on_time_delivery || 90)).toFixed(1);
  const suppDetailsElem = document.getElementById('map-supplier-details');
  if (suppDetailsElem) {
    suppDetailsElem.innerHTML = `
      <p><strong>Name:</strong> ${escapeHtml(supplier.name)}</p>
      <p><strong>Country:</strong> ${escapeHtml(supplier.country)}</p>
      <p><strong>Category:</strong> ${escapeHtml(supplier.category || supplier.supplier_category || 'General Components')}</p>
      <p><strong>Reliability Score:</strong> ${supplier.reliability_score || 95}%</p>
      <p><strong>On-Time Delivery:</strong> ${supplier.on_time_delivery || 92}%</p>
      <p><strong>Quality Score:</strong> ${supplier.quality_score || 98}%</p>
      <p><strong>Current Risk Level:</strong> <span class="badge-sev badge-${supplierRiskLvl.toLowerCase()}">${supplierRiskLvl}</span></p>
      <p><strong>Avg Delivery Time:</strong> ${deliveryTime} Days</p>
    `;
  }

  // Fetch Live Weather for Supplier Location (PART 2E)
  let weatherRiskLvl = 'LOW';
  const weatherDetailsElem = document.getElementById('map-weather-details');
  const weatherRiskBadge = document.getElementById('map-weather-risk-badge');

  if (weatherDetailsElem) {
    weatherDetailsElem.innerHTML = '<p class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Fetching live weather observations...</p>';
    try {
      const weather = await API.getLiveWeather(supplier.country || supplier.name);
      weatherRiskLvl = (weather.weather_risk_level || 'LOW').toUpperCase();

      if (weatherRiskBadge) {
        weatherRiskBadge.innerText = weatherRiskLvl;
        weatherRiskBadge.className = `badge-count badge-${weatherRiskLvl.toLowerCase()}`;
      }

      weatherDetailsElem.innerHTML = `
        <p><strong>Location:</strong> ${escapeHtml(weather.location || supplier.country)}</p>
        <p><strong>Temperature:</strong> ${weather.temperature_c !== undefined ? weather.temperature_c : 29.2}°C</p>
        <p><strong>Humidity:</strong> ${weather.humidity_percent !== undefined ? weather.humidity_percent : 75}%</p>
        <p><strong>Wind Speed:</strong> ${weather.wind_speed_kmh !== undefined ? weather.wind_speed_kmh : 5.0} km/h</p>
        <p><strong>Wind Gusts:</strong> ${weather.wind_gusts_kmh !== undefined ? weather.wind_gusts_kmh : 15.0} km/h</p>
        <p><strong>Precipitation:</strong> ${weather.precipitation_mm !== undefined ? weather.precipitation_mm : 0.0} mm</p>
        <p><strong>Weather Risk:</strong> <span class="badge-sev badge-${weatherRiskLvl.toLowerCase()}">${weatherRiskLvl}</span></p>
      `;
    } catch (wErr) {
      console.warn('Weather fetch warning:', wErr);
      if (weatherDetailsElem) {
        weatherDetailsElem.innerHTML = `<p style="color:#F59E0B;"><i class="fas fa-info-circle"></i> Weather data unavailable for ${escapeHtml(supplier.country)}</p>`;
      }
    }
  }

  // Fetch Supplier's Shipments (PART 2C)
  let shipments = [];
  try {
    shipments = await API.getShipmentsBySupplier(sId);
  } catch (shErr) {
    console.error('Shipment fetch error:', shErr);
  }

  const mapShipmentsCount = document.getElementById('map-shipments-count');
  if (mapShipmentsCount) {
    mapShipmentsCount.innerText = `${shipments.length} Shipments`;
  }

  // Render Map Markers & Travel Paths (PART 2C & 2D)
  const boundsPoints = [];
  const suppLat = supplier.latitude || 22.6273;
  const suppLng = supplier.longitude || 120.3014;

  // Add Supplier Origin Marker
  const suppMarker = L.marker([suppLat, suppLng], {
    title: supplier.name
  }).addTo(mapInstance);

  suppMarker.bindPopup(`
    <div style="font-size:0.85rem;">
      <h4 style="margin:0 0 6px 0; color:#6366F1;">🏭 ${escapeHtml(supplier.name)}</h4>
      <p style="margin:2px 0;"><strong>Country:</strong> ${escapeHtml(supplier.country)}</p>
      <p style="margin:2px 0;"><strong>Reliability:</strong> ${supplier.reliability_score}%</p>
      <p style="margin:2px 0;"><strong>Risk Level:</strong> ${supplierRiskLvl}</p>
    </div>
  `);

  mapMarkers.push(suppMarker);
  boundsPoints.push([suppLat, suppLng]);

  let highestShipmentDelay = 0;
  let hasHighRiskShipment = false;

  const shipmentDetailElem = document.getElementById('map-shipment-detail-panel');

  if (shipments.length === 0) {
    if (shipmentDetailElem) {
      shipmentDetailElem.innerHTML = `<p class="loading-cell">No active shipments currently registered for ${escapeHtml(supplier.name)}.</p>`;
    }
  } else {
    let detailHtml = '';

    shipments.forEach(shp => {
      const oLat = shp.origin_lat || suppLat;
      const oLng = shp.origin_lng || suppLng;
      const dLat = shp.dest_lat || 33.7420;
      const dLng = shp.dest_lng || -118.2673;

      boundsPoints.push([oLat, oLng]);
      boundsPoints.push([dLat, dLng]);

      const status = (shp.status || 'IN_TRANSIT').toUpperCase();
      const delayDays = shp.delay_days || 0;
      const riskLvl = (shp.risk_level || 'LOW').toUpperCase();

      if (delayDays > highestShipmentDelay) highestShipmentDelay = delayDays;
      if (riskLvl === 'HIGH' || riskLvl === 'CRITICAL' || status === 'DELAYED' || status === 'AT_RISK') {
        hasHighRiskShipment = true;
      }

      // Color coding for polyline travel path
      let routeColor = '#10B981'; // ON_TIME
      if (status === 'DELAYED' || riskLvl === 'HIGH' || riskLvl === 'CRITICAL') {
        routeColor = '#EF4444'; // DELAYED / HIGH
      } else if (status === 'AT_RISK' || delayDays > 0) {
        routeColor = '#F59E0B'; // AT_RISK / MINOR_DELAY
      } else if (status === 'DELIVERED') {
        routeColor = '#3B82F6';
      }

      // Draw polyline route
      const polyline = L.polyline([[oLat, oLng], [dLat, dLng]], {
        color: routeColor,
        weight: 4,
        dashArray: status === 'IN_TRANSIT' ? '6, 6' : null,
        opacity: 0.85
      }).addTo(mapInstance);

      polyline.bindPopup(`
        <div style="font-size:0.85rem;">
          <h4 style="margin:0 0 6px 0; color:${routeColor};">🚢 Shipment ${escapeHtml(shp.shipment_code)}</h4>
          <p style="margin:2px 0;"><strong>Origin:</strong> ${escapeHtml(shp.origin || 'Origin Port')}</p>
          <p style="margin:2px 0;"><strong>Destination:</strong> ${escapeHtml(shp.destination || 'Destination Port')}</p>
          <p style="margin:2px 0;"><strong>Status:</strong> ${status}</p>
          <p style="margin:2px 0;"><strong>Delay:</strong> ${delayDays} Days</p>
          <p style="margin:2px 0;"><strong>Cargo:</strong> ${escapeHtml(shp.cargo_description || 'General Components')}</p>
        </div>
      `);

      mapPolylines.push(polyline);

      // Add Destination Marker
      const destMarker = L.marker([dLat, dLng]).addTo(mapInstance);
      destMarker.bindPopup(`
        <div style="font-size:0.85rem;">
          <h4 style="margin:0 0 6px 0; color:#14B8A6;">📍 Destination: ${escapeHtml(shp.destination || 'Destination Port')}</h4>
          <p style="margin:2px 0;"><strong>Shipment:</strong> ${escapeHtml(shp.shipment_code)}</p>
          <p style="margin:2px 0;"><strong>Carrier:</strong> ${escapeHtml(shp.carrier || 'Global Carrier')}</p>
        </div>
      `);
      mapMarkers.push(destMarker);

      // Construct Detail Panel HTML (PART 2D)
      detailHtml += `
        <div class="impact-chain-card" style="margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <h4 style="margin:0; color:${routeColor};">🚢 Shipment ${escapeHtml(shp.shipment_code)}</h4>
            <span class="badge-sev badge-${riskLvl.toLowerCase()}">${riskLvl} Risk</span>
          </div>
          <p><strong>Supplier:</strong> ${escapeHtml(supplier.name)}</p>
          <div class="chain-steps">
            <span class="chain-step">📍 <strong>Origin:</strong> ${escapeHtml(shp.origin || 'Origin Port')}</span>
            <span class="chain-arrow">─── ( ${status} ) ───▶</span>
            <span class="chain-step">🏁 <strong>Destination:</strong> ${escapeHtml(shp.destination || 'Destination Port')}</span>
          </div>
          <p style="margin-top:8px;"><strong>Status:</strong> <span class="badge-sev badge-${status === 'DELIVERED' ? 'low' : (status === 'DELAYED' ? 'high' : 'warn')}">${status}</span> | <strong>Delay:</strong> ${delayDays} Days | <strong>Cargo:</strong> ${escapeHtml(shp.cargo_description || 'General Components')} | <strong>Carrier:</strong> ${escapeHtml(shp.carrier || 'Ocean Express')}</p>
        </div>
      `;
    });

    if (shipmentDetailElem) {
      shipmentDetailElem.innerHTML = detailHtml;
    }
  }

  // Fit map bounds to view all points
  if (boundsPoints.length > 0) {
    mapInstance.fitBounds(boundsPoints, { padding: [40, 40] });
  }

  // Combined Risk Alert Evaluation (PART 2F)
  const riskAlertCard = document.getElementById('map-risk-alert-card');
  const alertTitle = document.getElementById('map-risk-alert-title');
  const alertBody = document.getElementById('map-risk-alert-body');

  if (supplierRiskLvl === 'HIGH' || supplierRiskLvl === 'CRITICAL' || hasHighRiskShipment || weatherRiskLvl === 'HIGH' || weatherRiskLvl === 'CRITICAL') {
    if (riskAlertCard) {
      riskAlertCard.classList.remove('hidden');
      if (alertTitle) alertTitle.innerText = `⚠️ Supply Chain Alert: ${supplier.name}`;
      if (alertBody) {
        alertBody.innerHTML = `
          <strong>Supplier Risk:</strong> ${supplierRiskLvl} | 
          <strong>Shipment Delay:</strong> ${highestShipmentDelay} Days | 
          <strong>Weather Risk:</strong> ${weatherRiskLvl}<br>
          <em>Overall attention level: <strong>HIGH</strong>. Recommend activating backup logistics or dual-sourcing.</em>
        `;
      }
    }
  } else {
    if (riskAlertCard) {
      riskAlertCard.classList.add('hidden');
    }
  }
}

/* ============================================
   SUPPLY CHAIN NEWS CONTROLLER (PART 2G - 2J)
   ============================================ */
let persistentNewsData = [];

async function loadNews() {
  const container = document.getElementById('news-container');
  if (!container) return;

  container.innerHTML = '<div class="card"><p class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Loading supply chain news intelligence...</p></div>';

  try {
    persistentNewsData = await API.getNews();
    renderNewsCards(persistentNewsData);

    // Load News Impact Chain (PART 2J)
    loadNewsImpactChain();
  } catch (err) {
    console.error('Error loading news:', err);
    container.innerHTML = `<div class="card"><p class="loading-cell" style="color:#EF4444;"><i class="fas fa-exclamation-triangle"></i> Failed to load news: ${escapeHtml(err.message)}</p></div>`;
  }
}

async function fetchAndStoreLiveNews() {
  showToast('Fetching and storing live global supply chain news...', 'info');
  try {
    const res = await API.fetchAndStoreNews();
    showToast(`Stored ${res.new_articles_stored || 0} new news articles in AegisFlow database.`, 'success');
    await loadNews();
  } catch (err) {
    showToast(`Error fetching live news: ${err.message}`, 'error');
  }
}

function _formatNewsDate(isoStr) {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  } catch (e) { return ''; }
}

function renderNewsCards(newsList) {
  const container = document.getElementById('news-container');
  if (!container) return;

  if (!newsList || newsList.length === 0) {
    container.innerHTML = '<div class="card"><p class="loading-cell">No supply chain news matching current filters.</p></div>';
    return;
  }

  container.innerHTML = newsList.map(item => {
    const severity = (item.severity || item.risk_level || 'LOW').toUpperCase();
    const sevClass = severity === 'CRITICAL' || severity === 'HIGH' ? 'badge-high' : (severity === 'MEDIUM' ? 'badge-warn' : 'badge-low');
    const dateStr = _formatNewsDate(item.created_at);

    return `
      <div class="news-card">
        <div>
          <div class="news-card-header">
            <h4>${escapeHtml(item.headline || item.title || 'Supply Chain Event')}</h4>
            <span class="badge-sev ${sevClass}">${severity}</span>
          </div>
          <div class="news-card-meta">
            <span><i class="fas fa-newspaper"></i> ${escapeHtml(item.source || 'Global Feed')}</span>
            <span><i class="fas fa-map-marker-alt"></i> ${escapeHtml(item.location || 'Global')}</span>
            ${dateStr ? `<span><i class="fas fa-calendar-alt"></i> ${escapeHtml(dateStr)}</span>` : ''}
          </div>
          <div class="news-card-body">
            <p>${escapeHtml(item.supply_chain_impact || item.impact || 'Ingested geopolitical and logistics intelligence.')}</p>
          </div>
        </div>
        <div class="news-card-footer">
          <span><i class="fas fa-building"></i> <strong>Affected:</strong> ${escapeHtml(item.affected_suppliers || 'Global Supply Nodes')}</span>
        </div>
      </div>
    `;
  }).join('');
}

function filterNewsEvents() {
  const searchVal = (document.getElementById('news-search-input')?.value || '').toLowerCase().trim();
  const severityVal = document.getElementById('news-severity-filter')?.value || 'ALL';

  let filtered = persistentNewsData;

  if (severityVal !== 'ALL') {
    filtered = filtered.filter(n => (n.severity || n.risk_level || '').toUpperCase() === severityVal);
  }

  if (searchVal) {
    filtered = filtered.filter(n =>
      (n.headline || '').toLowerCase().includes(searchVal) ||
      (n.location || '').toLowerCase().includes(searchVal) ||
      (n.supply_chain_impact || n.impact || '').toLowerCase().includes(searchVal) ||
      (n.affected_suppliers || '').toLowerCase().includes(searchVal)
    );
  }

  renderNewsCards(filtered);
}

function setNewsQuickFilter(topic) {
  // Update quick chip active UI
  const chips = document.querySelectorAll('.news-quick-chips .chip-btn');
  chips.forEach(c => {
    if (c.innerText.trim().toLowerCase() === topic.toLowerCase()) {
      c.classList.add('active');
    } else {
      c.classList.remove('active');
    }
  });

  if (topic === 'ALL') {
    renderNewsCards(persistentNewsData);
    return;
  }

  const topicLower = topic.toLowerCase();
  const filtered = persistentNewsData.filter(n =>
    (n.headline || '').toLowerCase().includes(topicLower) ||
    (n.location || '').toLowerCase().includes(topicLower) ||
    (n.supply_chain_impact || n.impact || '').toLowerCase().includes(topicLower) ||
    (n.severity || '').toLowerCase().includes(topicLower)
  );

  renderNewsCards(filtered);
}

async function loadNewsImpactChain() {
  const container = document.getElementById('news-impact-chain-container');
  if (!container) return;

  try {
    const chainData = await API.getNewsImpactChain();
    if (!chainData || chainData.length === 0) {
      container.innerHTML = '<p class="loading-cell">No impact relationships mapped.</p>';
      return;
    }

    container.innerHTML = chainData.map((item, idx) => {
      const news = item.news || {};
      const suppliers = (item.suppliers || []).slice(0, 3);
      const shipments = (item.shipments || []).slice(0, 4);
      const inventory = (item.inventory || []).slice(0, 3);
      const risks     = (item.risks || []).slice(0, 2);

      const sevLower = (news.severity || 'low').toLowerCase();
      const dateStr  = _formatNewsDate(news.created_at);

      // Build compact node text
      const suppText = suppliers.length
        ? suppliers.map(s => escapeHtml(s.name)).join(' · ')
        : '<em>No matched supplier</em>';

      const shpText = shipments.length
        ? shipments.map(sh => `${escapeHtml(sh.code)} <span style="color:${sh.delay_days > 0 ? '#F59E0B' : '#10B981'};">(+${sh.delay_days || 0}d)</span>`).join(' · ')
        : '<em>No linked shipments</em>';

      const invText = inventory.length
        ? inventory.map(i => `${escapeHtml(i.product_name)} <span style="color:${i.days_remaining <= 3 ? '#EF4444' : '#F59E0B'};">(${i.days_remaining}d left)</span>`).join(' · ')
        : '<em>No at-risk inventory</em>';

      const riskText = risks.length
        ? risks.map(r => `<span style="color:${(r.severity||'').toUpperCase()==='CRITICAL'?'#EF4444':'#F59E0B'};">${escapeHtml(r.severity||'HIGH')}</span>: ${escapeHtml((r.title||'').substring(0,50))}`).join('<br>')
        : '<em>No linked risks</em>';

      return `
        <div class="impact-chain-card" style="margin-bottom:16px;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:10px;">
            <div>
              <h4 style="margin:0 0 4px 0; font-size:0.9rem; color:var(--text);">
                <i class="fas fa-newspaper" style="color:#3B82F6; margin-right:6px;"></i>${escapeHtml(news.headline || 'Supply Chain Event')}
              </h4>
              ${dateStr ? `<span style="font-size:0.75rem; color:var(--text-muted);"><i class="fas fa-calendar-alt"></i> ${escapeHtml(dateStr)} &nbsp;|&nbsp; <i class="fas fa-map-marker-alt"></i> ${escapeHtml(news.location || 'Global')}</span>` : `<span style="font-size:0.75rem; color:var(--text-muted);"><i class="fas fa-map-marker-alt"></i> ${escapeHtml(news.location || 'Global')}</span>`}
            </div>
            <span class="badge-sev badge-${sevLower}" style="flex-shrink:0;">${escapeHtml(news.severity || 'LOW')}</span>
          </div>
          <div class="chain-flow">
            <div class="chain-node">
              <div class="chain-node-label"><i class="fas fa-newspaper"></i> News Source</div>
              <div class="chain-node-value">${escapeHtml(news.source || 'Global Feed')}</div>
            </div>
            <div class="chain-connector"><i class="fas fa-arrow-right"></i></div>
            <div class="chain-node">
              <div class="chain-node-label"><i class="fas fa-industry"></i> Affected Suppliers</div>
              <div class="chain-node-value">${suppText}</div>
            </div>
            <div class="chain-connector"><i class="fas fa-arrow-right"></i></div>
            <div class="chain-node">
              <div class="chain-node-label"><i class="fas fa-ship"></i> Impacted Shipments</div>
              <div class="chain-node-value">${shpText}</div>
            </div>
            <div class="chain-connector"><i class="fas fa-arrow-right"></i></div>
            <div class="chain-node">
              <div class="chain-node-label"><i class="fas fa-boxes"></i> At-Risk Inventory</div>
              <div class="chain-node-value">${invText}</div>
            </div>
            <div class="chain-connector"><i class="fas fa-arrow-right"></i></div>
            <div class="chain-node">
              <div class="chain-node-label"><i class="fas fa-exclamation-triangle"></i> Active Risks</div>
              <div class="chain-node-value">${riskText}</div>
            </div>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading news impact chain:', err);
    const container2 = document.getElementById('news-impact-chain-container');
    if (container2) container2.innerHTML = '<p class="loading-cell" style="color:#EF4444;">Failed to load impact chain.</p>';
  }
}

function toggleAIChatbotPanel() {
  const chatPanel = document.getElementById('ai-chat-panel');
  if (chatPanel) {
    chatPanel.classList.toggle('active');
  }
}