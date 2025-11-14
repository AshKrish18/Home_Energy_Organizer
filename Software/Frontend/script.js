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

async function fetchAnomalies() {
  try {
    const response = await fetch("http://127.0.0.1:8000/anomalies");
    const result = await response.json();
    return result.anomalies || {};
  } catch (err) {
    console.error("Error fetching anomalies:", err);
    return {};
  }
}

async function fetchPrediction() {
  try {
    const response = await fetch("http://127.0.0.1:8000/predict/next_hour");
    const result = await response.json();
    return result.predicted_hourly_usage || 0;
  } catch (err) {
    console.error("Error fetching prediction:", err);
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

  const prediction = await fetchPrediction();
  const predictionElem = document.getElementById("prediction");
  if (predictionElem) {
    predictionElem.textContent = (prediction / 1000).toFixed(2) + " kWh";
  }

  // Cost estimate (₹7/kWh)
  const cost = (total / 1000) * 7;
  document.getElementById("cost").textContent = "₹" + cost.toFixed(2);
}

async function updateAlerts() {
  const anomalies = await fetchAnomalies();
  const alertList = document.getElementById("alert-list");
  if (!alertList) return;

  alertList.innerHTML = "";

  let hasAlerts = false;

  for (const device in anomalies) {
    const deviceAnoms = anomalies[device];
    if (deviceAnoms.length > 0) {
      hasAlerts = true;

      deviceAnoms.forEach(a => {
        const li = document.createElement("li");
        const time = new Date(a.timestamp * 1000).toLocaleString();

        li.innerHTML = `
          <strong>${device.toUpperCase()}</strong> anomaly at ${time} —
          ${a.power_w} W (z-score: ${a.z_score.toFixed(2)})
        `;
        alertList.appendChild(li);
      });
    }
  }

  if (!hasAlerts) {
    alertList.innerHTML = "<li>No anomalies detected 🎉</li>";
  }
}

// Refresh every 5 seconds
setInterval(() => {
  updateDashboard();
  updateAlerts();
}, 5000);

// First load
updateDashboard();
updateAlerts();
