// Simulate fetching data from backend
function fetchMeasurements() {
  return [
    { device: "Fridge", power_w: 150.3, ts: "2025-09-13 10:40" },
    { device: "Washer", power_w: 800.5, ts: "2025-09-13 10:40" },
    { device: "AC", power_w: 1200.2, ts: "2025-09-13 10:40" },
    { device: "Lights", power_w: 60.7, ts: "2025-09-13 10:40" }
  ];
}

async function fetchLatestData() {
  try {
    const response = await fetch("http://127.0.0.1:8000/readings/latest");
    const result = await response.json();
    return result.readings || [];
  } catch (err) {
    console.error("Error fetching data:", err);
    return [];
  }
}

async function fetchTotalConsumption() {
  try {
    const response = await fetch("http://127.0.0.1:8000/usage/total");
    const result = await response.json();
    return result.total_consumption || 0;
  } catch (err) {
    console.error("Error fetching total consumption:", err);
    return 0;
  }
}

async function updateDashboard() {
  const [data, total] = await Promise.all([fetchLatestData(), fetchTotalConsumption()]);

  // Update total consumption
  document.getElementById("total").textContent = (total / 1000).toFixed(2) + " kWh";

  // Update peak device and table
  if (data.length > 0) {
    const peak = data.reduce((max, d) => d.power_w > max.power_w ? d : max, data[0]);
    document.getElementById("peak").textContent = `${peak.device} (${peak.power_w} W)`;
  } else {
    document.getElementById("peak").textContent = "";
  }

  const table = document.getElementById("device-table");
  table.innerHTML = "";
  data.forEach(d => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${d.device}</td>
      <td>${d.power_w}</td>
      <td>${d.ts}</td>
    `;
    table.appendChild(row);
  });

  // Cost estimate (₹7/kWh)
  const cost = (total / 1000) * 7;
  document.getElementById("cost").textContent = "₹" + cost.toFixed(2);
}
async function fetchDailyUsage() {
  const res = await fetch("http://127.0.0.1:8000/usage/daily");
  const data = await res.json();
  return data.daily;
}

async function fetchMonthlyUsage() {
  const res = await fetch("http://127.0.0.1:8000/usage/monthly");
  const data = await res.json();
  return data.monthly;
}

async function renderCharts() {
  const daily = await fetchDailyUsage();
  const monthly = await fetchMonthlyUsage();

  // Daily chart
  new Chart(document.getElementById("dailyChart"), {
    type: "line",
    data: {
      labels: daily.map(d => d.day),
      datasets: [{
        label: "Daily Consumption (Wh)",
        data: daily.map(d => d.total),
        borderColor: "blue",
        fill: false
      }]
    }
  });

  // Monthly chart
  new Chart(document.getElementById("monthlyChart"), {
    type: "bar",
    data: {
      labels: monthly.map(m => m.month),
      datasets: [{
        label: "Monthly Consumption (Wh)",
        data: monthly.map(m => m.total),
        backgroundColor: "orange"
      }]
    }
  });
}

// Refresh every 5 seconds
setInterval(updateDashboard, 5000);

// First load
updateDashboard();

// Call once when page loads
renderCharts();