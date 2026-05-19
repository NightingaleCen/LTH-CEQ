<template>
  <div class="trend-chart">
    <p class="instruction">Click points to view reports · Click legend items to show/hide metrics</p>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  evaluations: {
    type: Array,
    required: true
  }
})

const chartCanvas = ref(null)
let chart = null

const scoreLabels = {
  good_teaching: 'Good Teaching',
  clear_goals_and_standards: 'Clear Goals & Standards',
  appropriate_assessment: 'Appropriate Assessment',
  appropriate_workload: 'Appropriate Workload',
  important_for_education: 'Important for Education',
  overall_satisfaction: 'Overall Satisfaction'
}

const colors = [
  '#3498db',
  '#e74c3c',
  '#2ecc71',
  '#f39c12',
  '#9b59b6',
  '#1abc9c'
]

const pointStyles = ['circle', 'triangle', 'rectRounded', 'rect', 'star', 'crossRot']

const createChart = () => {
  if (!chartCanvas.value || !props.evaluations.length) return

  const ctx = chartCanvas.value.getContext('2d')

  if (chart) {
    chart.destroy()
  }

  // Sort evaluations by time (oldest first for the chart)
  const sortedEvals = [...props.evaluations].reverse()

  const labels = sortedEvals.map(e =>
    `${e.academic_year} ${e.semester} ${e.period}`
  )

  // Store URLs for click handler
  const urls = sortedEvals.map(e => e.url)

  const datasets = []

  Object.keys(scoreLabels).forEach((key, idx) => {
    const color = colors[idx]

    datasets.push({
      label: scoreLabels[key],
      data: sortedEvals.map(e => e.scores[key]?.score),
      borderColor: color,
      backgroundColor: color + '20',
      borderWidth: 2,
      pointStyle: pointStyles[idx],
      pointRadius: 6,
      pointHoverRadius: 8,
      tension: 0.3
    })
  })

  chart = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'nearest',
        intersect: false
      },
      onClick: (event, elements) => {
        if (elements && elements.length > 0) {
          const index = elements[0].index
          const url = urls[index]
          if (url) {
            window.open(url, '_blank')
          }
        }
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            usePointStyle: true,
            padding: 15
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const val = context.parsed.y
              const eval_ = sortedEvals[context.dataIndex]
              const key = Object.keys(scoreLabels).find(k => scoreLabels[k] === context.dataset.label)
              const std = eval_?.scores[key]?.std
              return `${context.dataset.label}: ${val?.toFixed(2) || 'N/A'} ${std ? `(±${std.toFixed(2)})` : ''}`
            }
          }
        }
      },
      scales: {
        y: {
          min: -100,
          max: 100,
          title: {
            display: true,
            text: 'Score (-100 to 100)'
          }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  })
}

onMounted(createChart)
watch(() => props.evaluations, createChart, { deep: true })
</script>

<style scoped>
.trend-chart {
  height: 600px;
  position: relative;
  padding-bottom: 20px;
}

.instruction {
  margin: 0 0 12px 0;
  color: #999;
  font-size: 12px;
  text-align: center;
}

/* Mobile styles */
@media (max-width: 768px) {
  .trend-chart {
    height: 400px;
    padding-bottom: 40px;
  }

  .instruction {
    font-size: 11px;
  }
}
</style>
