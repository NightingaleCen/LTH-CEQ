<template>
  <div class="trend-chart">
    <p class="instruction">💡 Click on any point in the chart to view the full evaluation report</p>
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
  
  // Create datasets with error bands (std deviation)
  Object.keys(scoreLabels).forEach((key, idx) => {
    const color = colors[idx]
    
    // Main line dataset
    datasets.push({
      label: scoreLabels[key],
      data: sortedEvals.map(e => e.scores[key]?.score),
      borderColor: color,
      backgroundColor: color + '20',
      borderWidth: 2,
      pointRadius: 6,
      pointHoverRadius: 8,
      tension: 0.3
    })
    
    // Upper bound (score + std)
    datasets.push({
      label: scoreLabels[key] + ' (Upper)',
      data: sortedEvals.map(e => {
        const score = e.scores[key]?.score
        const std = e.scores[key]?.std
        return score != null && std != null ? score + std : null
      }),
      borderColor: color + '40',
      backgroundColor: 'transparent',
      borderWidth: 1,
      pointRadius: 0,
      pointHoverRadius: 0,
      tension: 0.3,
      fill: false
    })
    
    // Lower bound (score - std)
    datasets.push({
      label: scoreLabels[key] + ' (Lower)',
      data: sortedEvals.map(e => {
        const score = e.scores[key]?.score
        const std = e.scores[key]?.std
        return score != null && std != null ? score - std : null
      }),
      borderColor: color + '40',
      backgroundColor: color + '10',
      borderWidth: 1,
      pointRadius: 0,
      pointHoverRadius: 0,
      tension: 0.3,
      fill: '-1'  // Fill to the previous dataset (upper bound)
    })
  })

  chart = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
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
            padding: 15,
            filter: (item) => {
              // Only show main line datasets in legend, hide upper/lower bound datasets
              return !item.text.includes('(Upper)') && !item.text.includes('(Lower)')
            }
          },
          onClick: (e, legendItem, legend) => {
            const index = legendItem.datasetIndex
            const ci = legend.chart
            
            // Calculate indices for the group (main, upper, lower)
            // Each metric has 3 datasets: main, upper, lower at indices 0,1,2 then 3,4,5 etc.
            const groupStart = Math.floor(index / 3) * 3
            const groupIndices = [groupStart, groupStart + 1, groupStart + 2]
            
            // Toggle all datasets in the group
            groupIndices.forEach(idx => {
              if (ci.isDatasetVisible(idx)) {
                ci.hide(idx)
              } else {
                ci.show(idx)
              }
            })
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const val = context.parsed.y
              // Skip tooltips for upper/lower bound datasets
              if (context.dataset.label.includes('(Upper)') || context.dataset.label.includes('(Lower)')) {
                return null
              }
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
  margin: 0 0 15px 0;
  padding: 10px 15px;
  background: #e3f2fd;
  border-left: 3px solid #3498db;
  color: #2c3e50;
  font-size: 14px;
  border-radius: 0 6px 6px 0;
}

/* Mobile styles */
@media (max-width: 768px) {
  .trend-chart {
    height: 400px;
    padding-bottom: 40px;
  }

  .instruction {
    font-size: 13px;
    padding: 12px;
  }
}
</style>
