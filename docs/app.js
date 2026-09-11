// ============ 工具函数 ============

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

async function loadCSV(path) {
  try {
    const resp = await fetch(path + '?t=' + Date.now());
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return parseCSV(await resp.text());
  } catch (e) {
    console.warn(`加载 ${path} 失败:`, e);
    return [];
  }
}

// 关键：按日期列排序（从旧到新）
function sortByDate(rows, dateKeys) {
  return [...rows].sort((a, b) => {
    const getDate = (r) => {
      for (const k of dateKeys) {
        if (r[k]) {
          // 支持 "2026-08-31" / "2026年08月份" / "2026-08" 等格式
          return r[k].replace(/[年月]/g, '-').replace(/月份?/, '').replace(/-+$/, '').padEnd(7, '0');
        }
      }
      return '';
    };
    return getDate(a).localeCompare(getDate(b));
  });
}

function updateCard(cardId, value, period) {
  const card = document.getElementById(cardId);
  if (!card) return;
  card.querySelector('.value').textContent = value || '—';
  card.querySelector('.period').textContent = period || '—';
}

// 通用折线图
function drawLineChart(canvasId, labels, values, color) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  new Chart(el, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        borderColor: color,
        backgroundColor: color + '22',
        tension: 0.3,
        fill: true,
        pointRadius: 2,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: false } }
    }
  });
}

// ============ 主逻辑 ============
async function init() {
  // ---------- 制造业 PMI ----------
  const pmiData = sortByDate(
    await loadCSV('data/pmi_manufacturing.csv'),
    ['月份', '日期']
  );
  if (pmiData.length > 0) {
    const latest = pmiData[pmiData.length - 1];
    updateCard('card-pmi', latest['制造业-指数'], latest['月份']);

    const recent = pmiData.slice(-24);
    drawLineChart('chart-pmi',
      recent.map(d => d['月份']),
      recent.map(d => parseFloat(d['制造业-指数'])),
      '#667eea'
    );
  }

  // ---------- 公路物流运价指数（月） ----------
  const priceMonth = sortByDate(
    await loadCSV('data/price_index_month.csv'),
    ['日期']
  );
  if (priceMonth.length > 0) {
    const latest = priceMonth[priceMonth.length - 1];
    updateCard('card-price-month', latest['定基指数'], latest['日期']);

    const recent = priceMonth.slice(-24);
    drawLineChart('chart-price-month',
      recent.map(d => d['日期']),
      recent.map(d => parseFloat(d['定基指数'])),
      '#10b981'
    );
  }

  // ---------- 公路物流运量指数 ----------
  const volumeData = sortByDate(
    await loadCSV('data/volume_index_month.csv'),
    ['日期']
  );
  if (volumeData.length > 0) {
    const latest = volumeData[volumeData.length - 1];
    updateCard('card-volume', latest['定基指数'], latest['日期']);

    const recent = volumeData.slice(-24);
    drawLineChart('chart-volume',
      recent.map(d => d['日期']),
      recent.map(d => parseFloat(d['定基指数'])),
      '#f59e0b'
    );
  }

  // ---------- 物流景气指数 ----------
  const lpiData = await loadCSV('data/lpi.csv');
  if (lpiData.length > 0) {
    const keys = Object.keys(lpiData[0]);
    const dateKey = keys.find(k => k.includes('日期') || k.includes('月份') || k.includes('时间')) || keys[0];
    const valueKey = keys.find(k => k.includes('指数') && k !== dateKey) || keys[1];

    const sorted = sortByDate(lpiData, [dateKey]);
    const latest = sorted[sorted.length - 1];
    updateCard('card-lpi', latest[valueKey], latest[dateKey]);

    const recent = sorted.slice(-24);
    drawLineChart('chart-lpi',
      recent.map(d => d[dateKey]),
      recent.map(d => parseFloat(d[valueKey])),
      '#8b5cf6'
    );
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
    const allDates = [...new Set(routeData.map(r => r['发布日期']))].sort();
    const latestDate = allDates[allDates.length - 1];
    const latestRows = routeData.filter(r => r['发布日期'] === latestDate);

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
  } catch (e) {}
}

init();
