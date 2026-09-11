// ============ 工具函数 ============

// 简易 CSV 解析
function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim().replace(/^"|"$/g, ''));
    const row = {};
    headers.forEach((h, idx) => row[h] = values[idx] || '');
    rows.push(row);
  }
  return rows;
}

// 加载 CSV
async function loadCSV(path) {
  try {
    const resp = await fetch(path + '?t=' + Date.now());
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const text = await resp.text();
    return parseCSV(text);
  } catch (e) {
    console.warn(`加载 ${path} 失败:`, e);
    return [];
  }
}

// 更新卡片
function updateCard(cardId, value, period) {
  const card = document.getElementById(cardId);
  if (!card) return;
  card.querySelector('.value').textContent = value || '—';
  card.querySelector('.period').textContent = period || '—';
}

// ============ 各数据的加载与图表 ============

async function init() {
  // ---------- 制造业 PMI ----------
  const pmiData = await loadCSV('data/pmi_manufacturing.csv');
  if (pmiData.length > 0) {
    // 取最新一行
    const latest = pmiData[pmiData.length - 1];
    const month = latest['月份'] || '';
    const value = latest['制造业-指数'] || '';
    updateCard('card-pmi', value, month);

    // 图表（取最近 24 个月）
    const recent = pmiData.slice(-24);
    const labels = recent.map(d => d['月份']);
    const values = recent.map(d => parseFloat(d['制造业-指数']));

    new Chart(document.getElementById('chart-pmi'), {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: '制造业 PMI',
          data: values,
          borderColor: '#667eea',
          backgroundColor: 'rgba(102,126,234,0.1)',
          tension: 0.3,
          fill: true,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: false } }
      }
    });
  }

  // ---------- 公路物流运价指数（月） ----------
  const priceMonth = await loadCSV('data/price_index_month.csv');
  if (priceMonth.length > 0) {
    const latest = priceMonth[priceMonth.length - 1];
    const date = latest['日期'] || '';
    const value = latest['定基指数'] || '';
    updateCard('card-price-month', value, date);

    const recent = priceMonth.slice(-24);
    const labels = recent.map(d => d['日期']);
    const values = recent.map(d => parseFloat(d['定基指数']));

    new Chart(document.getElementById('chart-price-month'), {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: '运价指数',
          data: values,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16,185,129,0.1)',
          tension: 0.3,
          fill: true,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } }
      }
    });
  }

  // ---------- 公路物流运量指数 ----------
  const volumeData = await loadCSV('data/volume_index_month.csv');
  if (volumeData.length > 0) {
    const latest = volumeData[volumeData.length - 1];
    const date = latest['日期'] || '';
    const value = latest['定基指数'] || '';
    updateCard('card-volume', value, date);

    const recent = volumeData.slice(-24);
    const labels = recent.map(d => d['日期']);
    const values = recent.map(d => parseFloat(d['定基指数']));

    new Chart(document.getElementById('chart-volume'), {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: '运量指数',
          data: values,
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245,158,11,0.1)',
          tension: 0.3,
          fill: true,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } }
      }
    });
  }

  // ---------- 物流景气指数 ----------
  const lpiData = await loadCSV('data/lpi.csv');
  if (lpiData.length > 0) {
    const latest = lpiData[lpiData.length - 1];
    // 列名需要根据实际 CSV 调整
    const keys = Object.keys(latest);
    const dateKey = keys.find(k => k.includes('日期') || k.includes('月份') || k.includes('时间')) || keys[0];
    const valueKey = keys.find(k => k.includes('指数') && !k.includes('日期')) || keys[1];
    updateCard('card-lpi', latest[valueKey], latest[dateKey]);
  }

  // ---------- 仓储指数 ----------
  const warehouseData = await loadCSV('data/warehouse_index.csv');
  if (warehouseData.length > 0) {
    const latest = warehouseData[warehouseData.length - 1];
    updateCard('card-warehouse', latest['综合指数'], latest['期数']);
  }

  // ---------- 分线路运价表 ----------
  const routeData = await loadCSV('data/route_price.csv');
  if (routeData.length > 0) {
    // 找最新一期
    const allDates = [...new Set(routeData.map(r => r['发布日期']))].sort();
    const latestDate = allDates[allDates.length - 1];
    const latestRows = routeData.filter(r => r['发布日期'] === latestDate);

    // 透视成表格：线路 × 车型
    const routes = [...new Set(latestRows.map(r => r['线路']))];
    const types = [...new Set(latestRows.map(r => r['车型']))];

    let html = `<p style="color:#7f8c8d;font-size:0.85rem;margin-bottom:1rem;">发布日期：${latestDate}</p>`;
    html += '<table><thead><tr><th>车型</th>';
    routes.forEach(r => html += `<th>${r}</th>`);
    html += '</tr></thead><tbody>';

    types.forEach(t => {
      html += `<tr><td><strong>${t}</strong></td>`;
      routes.forEach(r => {
        const row = latestRows.find(x => x['车型'] === t && x['线路'] === r);
        if (row) {
          const change = parseFloat(row['环比(%)']);
          const color = change > 0 ? '#e74c3c' : (change < 0 ? '#27ae60' : '#7f8c8d');
          html += `<td>${row['价格']} <span style="color:${color};font-size:0.8rem;">(${row['环比(%)']}%)</span></td>`;
        } else {
          html += '<td>—</td>';
        }
      });
      html += '</tr>';
    });
    html += '</tbody></table>';
    document.getElementById('route-table-content').innerHTML = html;
  } else {
    document.getElementById('route-table-content').textContent = '暂无数据';
  }

  // ---------- 最后更新时间 ----------
  try {
    const resp = await fetch('data/_UPDATE_INFO.txt?t=' + Date.now());
    if (resp.ok) {
      const text = await resp.text();
      const m = text.match(/最后更新:\s*(.+)/);
      if (m) {
        document.getElementById('last-update').textContent = ' · 最后更新：' + m[1].slice(0, 19).replace('T', ' ');
      }
    }
  } catch (e) {
    // 忽略
  }
}

init();
