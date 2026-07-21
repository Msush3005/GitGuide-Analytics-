/**
 * GitGuide Analytics - Frontend Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const kpiTotalContributions = document.getElementById('kpiTotalContributions');
  const kpiTotalCommits = document.getElementById('kpiTotalCommits');
  const kpiTotalPRs = document.getElementById('kpiTotalPRs');
  const kpiActiveContributors = document.getElementById('kpiActiveContributors');
  const kpiMaintainerCount = document.getElementById('kpiMaintainerCount');

  const searchInput = document.getElementById('searchInput');
  const roleFilter = document.getElementById('roleFilter');
  const tableBody = document.getElementById('tableBody');
  const refreshBtn = document.getElementById('refreshBtn');
  const runPipelineBtn = document.getElementById('runPipelineBtn');
  const exportCsvBtn = document.getElementById('exportCsvBtn');

  const pipelineModal = document.getElementById('pipelineModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const dismissModalBtn = document.getElementById('dismissModalBtn');
  const terminalOutput = document.getElementById('terminalOutput');
  const statusTitle = document.getElementById('statusTitle');

  let rawDataset = [];
  let filteredDataset = [];
  let barChartInstance = null;
  let doughnutChartInstance = null;

  // Initial Load
  fetchData();

  // Event Listeners
  refreshBtn.addEventListener('click', fetchData);
  searchInput.addEventListener('input', applyFilters);
  roleFilter.addEventListener('change', applyFilters);
  runPipelineBtn.addEventListener('click', triggerPipeline);
  exportCsvBtn.addEventListener('click', exportTableToCSV);

  closeModalBtn.addEventListener('click', hideModal);
  dismissModalBtn.addEventListener('click', hideModal);

  // Fetch Dataset from API Server
  async function fetchData() {
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = `Refreshing...`;

    try {
      const response = await fetch('/api/data');
      if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
      const json = await response.json();

      if (json.status === 'success') {
        rawDataset = json.data || [];
        updateKPIs(json.summary);
        applyFilters();
      } else {
        throw new Error(json.message || 'Failed to parse analytics response.');
      }
    } catch (err) {
      console.warn('API connection offline, using fallback client dataset:', err);
      // Fallback client data for preview mode if API server is offline
      useFallbackData();
    } finally {
      refreshBtn.disabled = false;
      refreshBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 4v6h-6"></path><path d="M1 20v-6h6"></path>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
        </svg> Refresh Data`;
    }
  }

  // Fallback Data Generator
  function useFallbackData() {
    rawDataset = [
      { contributor_id: 101, repository_name: 'GitGuide-Analytics-', commits_count: 12, pull_requests_opened: 3, total_contributions: 15, lines_changed: 450, contributor_role: 'Maintainer', timestamp: '2026-07-01 10:00:00' },
      { contributor_id: 102, repository_name: 'GitGuide-Analytics-', commits_count: 5, pull_requests_opened: 1, total_contributions: 6, lines_changed: 120, contributor_role: 'Contributor', timestamp: '2026-07-01 11:30:00' },
      { contributor_id: 103, repository_name: 'GitGuide-Analytics-', commits_count: 8, pull_requests_opened: 2, total_contributions: 10, lines_changed: 230, contributor_role: 'Contributor', timestamp: '2026-07-02 09:15:00' },
      { contributor_id: 104, repository_name: 'GitGuide-Analytics-', commits_count: 4, pull_requests_opened: 0, total_contributions: 4, lines_changed: 45, contributor_role: 'Reviewer', timestamp: '2026-07-02 14:00:00' },
      { contributor_id: 105, repository_name: 'GitGuide-Analytics-', commits_count: 15, pull_requests_opened: 5, total_contributions: 20, lines_changed: 610, contributor_role: 'Maintainer', timestamp: '2026-07-03 16:45:00' },
      { contributor_id: 106, repository_name: 'GitGuide-Analytics-', commits_count: 3, pull_requests_opened: 1, total_contributions: 4, lines_changed: 85, contributor_role: 'Contributor', timestamp: '2026-07-04 12:20:00' },
      { contributor_id: 107, repository_name: 'GitGuide-Analytics-', commits_count: 20, pull_requests_opened: 7, total_contributions: 27, lines_changed: 890, contributor_role: 'Maintainer', timestamp: '2026-07-05 08:30:00' },
      { contributor_id: 108, repository_name: 'GitGuide-Analytics-', commits_count: 1, pull_requests_opened: 0, total_contributions: 1, lines_changed: 15, contributor_role: 'Contributor', timestamp: '2026-07-05 17:10:00' }
    ];

    const totalCommits = rawDataset.reduce((acc, r) => acc + (r.commits_count || 0), 0);
    const totalPRs = rawDataset.reduce((acc, r) => acc + (r.pull_requests_opened || 0), 0);
    const totalContributions = rawDataset.reduce((acc, r) => acc + (r.total_contributions || 0), 0);
    const maintainers = rawDataset.filter(r => r.contributor_role === 'Maintainer').length;

    updateKPIs({
      total_rows: rawDataset.length,
      total_commits: totalCommits,
      total_prs: totalPRs,
      total_contributions: totalContributions,
      maintainer_count: maintainers,
      contributor_count: rawDataset.length - maintainers
    });
    applyFilters();
  }

  // Update KPI Cards
  function updateKPIs(summary) {
    if (!summary) return;
    kpiTotalContributions.textContent = (summary.total_contributions || 0).toLocaleString();
    kpiTotalCommits.textContent = (summary.total_commits || 0).toLocaleString();
    kpiTotalPRs.textContent = (summary.total_prs || 0).toLocaleString();
    kpiActiveContributors.textContent = summary.total_rows || rawDataset.length;
    kpiMaintainerCount.textContent = `${summary.maintainer_count || 0} Maintainers | ${summary.contributor_count || 0} Contributors`;
  }

  // Apply Search & Role Filters
  function applyFilters() {
    const query = searchInput.value.toLowerCase().trim();
    const selectedRole = roleFilter.value;

    filteredDataset = rawDataset.filter(row => {
      const matchRole = selectedRole === 'ALL' || row.contributor_role === selectedRole;
      const matchSearch =
        !query ||
        String(row.contributor_id).toLowerCase().includes(query) ||
        String(row.repository_name).toLowerCase().includes(query) ||
        String(row.contributor_role).toLowerCase().includes(query);

      return matchRole && matchSearch;
    });

    renderTable(filteredDataset);
    renderCharts(filteredDataset);
  }

  // Render Data Table
  function renderTable(data) {
    if (!data || data.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 24px;">No matching contributor records found.</td></tr>`;
      return;
    }

    tableBody.innerHTML = data.map(row => {
      const roleClass = (row.contributor_role || 'Contributor').toLowerCase();
      return `
        <tr>
          <td><strong>#${row.contributor_id}</strong></td>
          <td><code>${row.repository_name || 'GitGuide-Analytics-'}</code></td>
          <td><span class="role-tag ${roleClass}">${row.contributor_role}</span></td>
          <td>${row.commits_count}</td>
          <td>${row.pull_requests_opened}</td>
          <td><strong style="color: var(--accent-primary);">${row.total_contributions || (row.commits_count + row.pull_requests_opened)}</strong></td>
          <td>${row.lines_changed || '-'}</td>
          <td style="color: var(--text-dim);">${row.timestamp || 'N/A'}</td>
        </tr>
      `;
    }).join('');
  }

  // Render Visual Charts
  function renderCharts(data) {
    // Bar Chart: Commits vs PRs
    const labels = data.map(d => `User #${d.contributor_id}`);
    const commitsData = data.map(d => d.commits_count);
    const prsData = data.map(d => d.pull_requests_opened);

    const ctxBar = document.getElementById('activityBarChart').getContext('2d');
    if (barChartInstance) barChartInstance.destroy();

    barChartInstance = new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Commits',
            data: commitsData,
            backgroundColor: 'rgba(99, 102, 241, 0.7)',
            borderColor: '#6366f1',
            borderWidth: 1,
            borderRadius: 6
          },
          {
            label: 'Pull Requests',
            data: prsData,
            backgroundColor: 'rgba(16, 185, 129, 0.7)',
            borderColor: '#10b981',
            borderWidth: 1,
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#9ca3af', font: { family: 'Inter' } } }
        },
        scales: {
          x: { ticks: { color: '#6b7280' }, grid: { display: false } },
          y: { ticks: { color: '#6b7280' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
        }
      }
    });

    // Doughnut Chart: Role Distribution
    const roleCounts = {};
    data.forEach(d => {
      const role = d.contributor_role || 'Contributor';
      roleCounts[role] = (roleCounts[role] || 0) + 1;
    });

    const ctxDoughnut = document.getElementById('roleDoughnutChart').getContext('2d');
    if (doughnutChartInstance) doughnutChartInstance.destroy();

    doughnutChartInstance = new Chart(ctxDoughnut, {
      type: 'doughnut',
      data: {
        labels: Object.keys(roleCounts),
        datasets: [{
          data: Object.values(roleCounts),
          backgroundColor: ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#9ca3af', padding: 15 } }
        },
        cutout: '70%'
      }
    });
  }

  // Trigger Python Data Pipeline via API
  async function triggerPipeline() {
    showModal();
    terminalOutput.innerHTML = `
      <p class="term-line info">$ python scripts/data_workflow.py</p>
      <p class="term-line info">Executing data ingestion, deduplication, and quality pipeline...</p>
    `;

    try {
      const res = await fetch('/api/run-pipeline', { method: 'POST' });
      const json = await res.json();

      if (json.status === 'success') {
        terminalOutput.innerHTML += `
          <p class="term-line success">--------------------------------------------------</p>
          <p class="term-line success">${json.output_log || json.message}</p>
          <p class="term-line success">✓ Pipeline executed successfully! (${json.rows_processed} rows outputted)</p>
        `;
        statusTitle.textContent = 'Pipeline Active';
        fetchData();
      } else {
        throw new Error(json.message || 'Pipeline script execution error.');
      }
    } catch (err) {
      terminalOutput.innerHTML += `
        <p class="term-line error">--------------------------------------------------</p>
        <p class="term-line error">Execution Error: ${err.message}</p>
        <p class="term-line info">Simulating client-side dataset refresh...</p>
      `;
      setTimeout(() => {
        useFallbackData();
        terminalOutput.innerHTML += `<p class="term-line success">✓ Preview mode active: Data loaded.</p>`;
      }, 1000);
    }
  }

  // Export Filtered Dataset to CSV
  function exportTableToCSV() {
    if (!filteredDataset.length) return alert('No data to export.');
    const keys = Object.keys(filteredDataset[0]);
    const csvRows = [keys.join(',')];

    filteredDataset.forEach(row => {
      const values = keys.map(k => `"${String(row[k] || '').replace(/"/g, '""')}"`);
      csvRows.push(values.join(','));
    });

    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('href', url);
    a.setAttribute('download', 'gitguide_contributor_analytics.csv');
    a.click();
  }

  function showModal() { pipelineModal.classList.add('show'); }
  function hideModal() { pipelineModal.classList.remove('show'); }
});
