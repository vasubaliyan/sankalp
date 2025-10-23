document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("tablesContainer");
  const template = document.querySelector(".table-template");

  // Create 10 tables dynamically
  for (let i = 1; i <= 10; i++) {
    const tableClone = template.cloneNode(true);
    tableClone.style.display = "block";
    tableClone.classList.remove("table-template");
    tableClone.querySelector("h3").textContent = `Table ${i}`;

    const tbody = tableClone.querySelector("tbody");

    for (let j = 1; j <= 5; j++) {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>Item ${String.fromCharCode(64 + j)}${i}</td>
        <td>${Math.floor(Math.random() * 1000)}</td>
      `;
      tbody.appendChild(row);
    }

    container.appendChild(tableClone);
  }

  // Sidebar tab functionality
  const tabs = document.querySelectorAll(".sidebar ul li a");
  const sections = document.querySelectorAll(".tab-section");

  tabs.forEach(tab => {
    tab.addEventListener("click", (e) => {
      e.preventDefault();
      const target = tab.dataset.tab;

      sections.forEach(sec => {
        sec.style.display = sec.id === target ? "block" : "none";
      });
    });
  });

  // Placeholder Charts using Chart.js
  const ctxUsers = document.getElementById('usersChart').getContext('2d');
  const usersChart = new Chart(ctxUsers, {
    type: 'line',
    data: {
      labels: ['Jan','Feb','Mar','Apr','May','Jun'],
      datasets: [{
        label: 'Users',
        data: [120, 200, 150, 300, 250, 400],
        backgroundColor: 'rgba(203,12,159,0.2)',
        borderColor: 'rgba(203,12,159,1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: { responsive: true }
  });

  const ctxRevenue = document.getElementById('revenueChart').getContext('2d');
  const revenueChart = new Chart(ctxRevenue, {
    type: 'bar',
    data: {
      labels: ['Jan','Feb','Mar','Apr','May','Jun'],
      datasets: [{
        label: 'Revenue',
        data: [5000, 7000, 4000, 8000, 6000, 10000],
        backgroundColor: 'rgba(23,193,232,0.7)',
        borderColor: 'rgba(23,193,232,1)',
        borderWidth: 1
      }]
    },
    options: { responsive: true }
  });
});


// Detailed Charts
const ctxPie = document.getElementById('pieChart').getContext('2d');
const pieChart = new Chart(ctxPie, {
  type: 'pie',
  data: {
    labels: ['Red', 'Blue', 'Yellow', 'Green'],
    datasets: [{
      label: 'Pie Dataset',
      data: [10, 20, 30, 40],
      backgroundColor: [
        'rgba(255,99,132,0.7)',
        'rgba(54,162,235,0.7)',
        'rgba(255,206,86,0.7)',
        'rgba(75,192,192,0.7)'
      ],
      borderWidth: 1
    }]
  },
  options: { responsive: true }
});

const ctxBar = document.getElementById('barChart').getContext('2d');
const barChart = new Chart(ctxBar, {
  type: 'bar',
  data: {
    labels: ['A', 'B', 'C', 'D', 'E'],
    datasets: [{
      label: 'Bar Dataset',
      data: [12, 19, 3, 5, 2],
      backgroundColor: 'rgba(255,159,64,0.7)',
      borderColor: 'rgba(255,159,64,1)',
      borderWidth: 1
    }]
  },
  options: { responsive: true }
});

const ctxScatter = document.getElementById('scatterChart').getContext('2d');
const scatterChart = new Chart(ctxScatter, {
  type: 'scatter',
  data: {
    datasets: [{
      label: 'Scatter Dataset',
      data: [
        {x: 10, y: 20},
        {x: 15, y: 10},
        {x: 7, y: 25},
        {x: 20, y: 5}
      ],
      backgroundColor: 'rgba(153,102,255,0.7)'
    }]
  },
  options: {
    responsive: true,
    scales: {
      x: { type: 'linear', position: 'bottom' },
      y: { beginAtZero: true }
    }
  }
});


// Sidebar tab functionality
const tabs = document.querySelectorAll(".sidebar ul li a");
const sections = document.querySelectorAll(".tab-section");
const tables = tabs[0];
// Add active class to tables tab first
tables.classList.add("active-tab")

tabs.forEach(tab => {
  tab.addEventListener("click", (e) => {
    e.preventDefault();
    const target = tab.dataset.tab;

    // Show the selected section and hide others
    sections.forEach(sec => {
      sec.style.display = sec.id === target ? "block" : "none";
    });

    // Remove 'active-tab' from all tabs
    tabs.forEach(t => t.classList.remove("active-tab"));

    // Add 'active-tab' to the clicked tab
    tab.classList.add("active-tab");
  });
});


