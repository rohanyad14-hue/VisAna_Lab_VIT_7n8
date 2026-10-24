// app.js — Containerized Dashboard Logic with Apache ECharts and REST API Integration
// Incorporating User Cyber-Neon Color Palettes:
// Primary Palette: ['#34EDF3', '#FF007A', '#A700FF', '#FFEA00', '#6FFFE9', '#FF8FAB', '#00FFB3', '#0313A6']

const PALETTE = ['#34EDF3', '#FF007A', '#A700FF', '#FFEA00', '#6FFFE9', '#FF8FAB', '#00FFB3', '#0313A6'];

// Category-specific color mapping from user palette
const CATEGORY_COLORS = {
  "Electronics": "#34EDF3",
  "Clothing": "#FF007A",
  "Home": "#A700FF",
  "Sports": "#FFEA00"
};

// Region-specific color mapping from user palette
const REGION_COLORS = {
  "East": "#34EDF3",
  "North": "#FF007A",
  "South": "#A700FF",
  "West": "#FFEA00"
};

const API_BASE = (window.location.protocol.startsWith("http"))
  ? `${window.location.origin}/api`
  : "http://127.0.0.1:5000/api";

console.log("[VeloceAnalytics] Configured API Base:", API_BASE);

let monthlyChart = null;
let shareChart = null;
let categoryChart = null;
let comboChart = null;
let drillCategory = null;

document.addEventListener("DOMContentLoaded", () => {
  initCharts();
  setupFilterEventListeners();
  checkApiHealth();

  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("drill")) {
    drillCategory = urlParams.get("drill");
    document.getElementById("drillIndicator").style.display = "flex";
    document.getElementById("drillCategoryName").textContent = drillCategory;
  }

  loadAllDashboardData();
  setInterval(checkApiHealth, 15000);
});

function initCharts() {
  const chartTheme = "dark";
  monthlyChart = echarts.init(document.getElementById("monthlyChart"), chartTheme);
  shareChart = echarts.init(document.getElementById("shareChart"), chartTheme);
  categoryChart = echarts.init(document.getElementById("categoryChart"), chartTheme);
  comboChart = echarts.init(document.getElementById("comboChart"), chartTheme);

  // Click drilldown on Share Donut Chart
  shareChart.on("click", (params) => {
    if (params.name) {
      drillCategory = params.name;
      document.getElementById("drillIndicator").style.display = "flex";
      document.getElementById("drillCategoryName").textContent = drillCategory;
      loadAllDashboardData();
    }
  });

  window.addEventListener("resize", () => {
    monthlyChart.resize();
    shareChart.resize();
    categoryChart.resize();
    comboChart.resize();
  });
}

function setupFilterEventListeners() {
  document.querySelectorAll(".checkbox-pills .pill").forEach(pill => {
    pill.addEventListener("click", (e) => {
      const checkbox = pill.querySelector("input[type='checkbox']");
      if (e.target !== checkbox) {
        checkbox.checked = !checkbox.checked;
      }
      pill.classList.toggle("active", checkbox.checked);
    });
  });

  document.getElementById("applyFiltersBtn").addEventListener("click", () => {
    loadAllDashboardData();
  });

  document.getElementById("resetFiltersBtn").addEventListener("click", () => {
    document.querySelectorAll(".checkbox-pills .pill").forEach(pill => {
      pill.classList.add("active");
      pill.querySelector("input[type='checkbox']").checked = true;
    });
    document.getElementById("startDate").value = "2025-01-01";
    document.getElementById("endDate").value = "2025-12-31";
    drillCategory = null;
    document.getElementById("drillIndicator").style.display = "none";
    loadAllDashboardData();
  });

  document.getElementById("clearDrillBtn").addEventListener("click", () => {
    drillCategory = null;
    document.getElementById("drillIndicator").style.display = "none";
    loadAllDashboardData();
  });
}

function checkApiHealth() {
  const dot = document.getElementById("apiStatusDot");
  const text = document.getElementById("apiStatusText");
  const telDb = document.getElementById("telDb");

  fetch(`${API_BASE}/health`)
    .then(r => r.json())
    .then(data => {
      if (data.status === "UP" && data.sql && data.sql.ok) {
        dot.className = "status-dot online";
        text.textContent = `Connected (SQL: ${data.sql.rows.toLocaleString()} rows)`;
        if (telDb) {
          telDb.textContent = `${data.sql.source} (${data.sql.rows.toLocaleString()} records)`;
        }
      } else {
        dot.className = "status-dot offline";
        text.textContent = "Database Disconnected";
      }
    })
    .catch(() => {
      dot.className = "status-dot offline";
      text.textContent = "API Offline";
    });
}

function buildQueryString() {
  const params = new URLSearchParams();

  const selectedRegions = Array.from(document.querySelectorAll("#regionPills .pill.active input"))
    .map(input => input.value);
  if (selectedRegions.length > 0 && selectedRegions.length < 4) {
    params.set("region", selectedRegions.join(","));
  }

  if (drillCategory) {
    params.set("category", drillCategory);
  } else {
    const selectedCats = Array.from(document.querySelectorAll("#categoryPills .pill.active input"))
      .map(input => input.value);
    if (selectedCats.length > 0 && selectedCats.length < 4) {
      params.set("category", selectedCats.join(","));
    }
  }

  const start = document.getElementById("startDate").value;
  const end = document.getElementById("endDate").value;
  if (start) params.set("start", start);
  if (end) params.set("end", end);

  return params.toString();
}

function loadAllDashboardData() {
  const qs = buildQueryString();

  // 1. KPI Summary
  fetch(`${API_BASE}/sales/summary?${qs}`)
    .then(r => r.json())
    .then(d => {
      document.getElementById("kpiTotalSales").textContent = "$" + d.total_sales.toLocaleString("en-US", {minimumFractionDigits: 2});
      document.getElementById("kpiAvgDaily").textContent = "$" + d.avg_daily_sales.toLocaleString("en-US", {minimumFractionDigits: 2});
      document.getElementById("kpiOrders").textContent = `${d.orders.toLocaleString()} transactions recorded`;
      document.getElementById("kpiTopRegion").textContent = d.top_region || "N/A";
      document.getElementById("kpiTopCategory").textContent = d.top_category || "N/A";
    })
    .catch(err => console.error("KPI error:", err));

  // 2. Monthly Regional Sales Trend
  fetch(`${API_BASE}/sales/monthly?${qs}`)
    .then(r => r.json())
    .then(d => {
      const styledSeries = (d.series || []).map((s, idx) => {
        const color = REGION_COLORS[s.name] || PALETTE[idx % PALETTE.length];
        return {
          ...s,
          lineStyle: { width: 3, color: color },
          itemStyle: { color: color },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: color + "40" },
              { offset: 1, color: color + "00" }
            ])
          }
        };
      });

      monthlyChart.setOption({
        color: PALETTE,
        backgroundColor: "transparent",
        tooltip: { trigger: "axis" },
        legend: { top: 0, textStyle: { color: "#E0E1DD" } },
        grid: { top: 40, left: 60, right: 30, bottom: 50 },
        xAxis: { 
          type: "category", 
          data: d.months, 
          axisLine: { lineStyle: { color: "#2C3E5A" } }, 
          axisLabel: { color: "#94A3B8" } 
        },
        yAxis: { 
          type: "value", 
          splitLine: { lineStyle: { color: "rgba(44, 62, 90, 0.4)" } }, 
          axisLabel: { color: "#94A3B8" } 
        },
        dataZoom: [{ 
          type: "inside" 
        }, { 
          type: "slider", 
          bottom: 5, 
          height: 18, 
          borderColor: "#2C3E5A", 
          textStyle: { color: "#E0E1DD" },
          fillerColor: "rgba(52, 237, 243, 0.2)"
        }],
        series: styledSeries
      }, true);
    })
    .catch(err => console.error("Monthly trend error:", err));

  // 3. Category Revenue Share Donut
  fetch(`${API_BASE}/sales/share?by=category&${qs}`)
    .then(r => r.json())
    .then(d => {
      const coloredData = (d.data || []).map((item, idx) => ({
        ...item,
        itemStyle: {
          color: CATEGORY_COLORS[item.name] || PALETTE[idx % PALETTE.length]
        }
      }));

      shareChart.setOption({
        color: PALETTE,
        backgroundColor: "transparent",
        tooltip: { trigger: "item", formatter: "{b}: ${c} ({d}%)" },
        legend: { bottom: 0, textStyle: { color: "#E0E1DD" } },
        series: [{
          name: "Category",
          type: "pie",
          radius: ["42%", "72%"],
          itemStyle: { borderRadius: 8, borderColor: "#1B263B", borderWidth: 3 },
          label: { formatter: "{b}\n{d}%", color: "#FFFFFF", fontWeight: "bold" },
          emphasis: { scale: true, focus: 'self' },
          data: coloredData
        }]
      }, true);
    })
    .catch(err => console.error("Share error:", err));

  // 4. Category Stacked Bar Chart
  fetch(`${API_BASE}/sales/by-category?${qs}`)
    .then(r => r.json())
    .then(d => {
      const styledCategorySeries = (d.series || []).map((s, idx) => {
        const color = REGION_COLORS[s.name] || PALETTE[idx % PALETTE.length];
        return {
          ...s,
          itemStyle: { color: color, borderRadius: [2, 2, 0, 0] }
        };
      });

      categoryChart.setOption({
        color: PALETTE,
        backgroundColor: "transparent",
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        legend: { top: 0, textStyle: { color: "#E0E1DD" } },
        grid: { top: 40, left: 60, right: 20, bottom: 25 },
        xAxis: { 
          type: "category", 
          data: d.categories, 
          axisLine: { lineStyle: { color: "#2C3E5A" } }, 
          axisLabel: { color: "#94A3B8" } 
        },
        yAxis: { 
          type: "value", 
          splitLine: { lineStyle: { color: "rgba(44, 62, 90, 0.4)" } }, 
          axisLabel: { color: "#94A3B8" } 
        },
        series: styledCategorySeries
      }, true);
    })
    .catch(err => console.error("Category error:", err));

  // 5. Dual-Axis Combo Chart
  fetch(`${API_BASE}/sales/combo?${qs}`)
    .then(r => r.json())
    .then(d => {
      comboChart.setOption({
        color: ["#34EDF3", "#FF007A"],
        backgroundColor: "transparent",
        tooltip: { trigger: "axis" },
        legend: { top: 0, textStyle: { color: "#E0E1DD" } },
        grid: { top: 40, left: 60, right: 60, bottom: 25 },
        xAxis: { 
          type: "category", 
          data: d.months, 
          axisLine: { lineStyle: { color: "#2C3E5A" } }, 
          axisLabel: { color: "#94A3B8" } 
        },
        yAxis: [
          { type: "value", name: "Monthly", splitLine: { lineStyle: { color: "rgba(44, 62, 90, 0.4)" } }, axisLabel: { color: "#94A3B8" } },
          { type: "value", name: "Cumulative", splitLine: { show: false }, axisLabel: { color: "#94A3B8" } }
        ],
        series: [
          { 
            name: "Monthly Sales", 
            type: "bar", 
            data: d.monthly, 
            itemStyle: { 
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "#34EDF3" },
                { offset: 1, color: "#0313A6" }
              ]),
              borderRadius: [4, 4, 0, 0]
            } 
          },
          { 
            name: "Cumulative Sales", 
            type: "line", 
            yAxisIndex: 1, 
            smooth: true, 
            data: d.cumulative, 
            lineStyle: { width: 3.5, color: "#FF007A" },
            itemStyle: { color: "#FF007A" },
            shadowColor: "rgba(255, 0, 122, 0.5)",
            shadowBlur: 10
          }
        ]
      }, true);
    })
    .catch(err => console.error("Combo error:", err));
}
