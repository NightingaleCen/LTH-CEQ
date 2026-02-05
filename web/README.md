# LTH Course Evaluation Viewer

A Vue.js web application for browsing and comparing Lund University (LTH) course evaluation data.

## Features

- **Browse Courses**: Scrollable list of all MMSR program courses
- **Course Details**: View latest CEQ scores with standard deviations and historical trends
- **Compare Courses**: Side-by-side comparison of two courses' latest evaluation data
- **Interactive Charts**: Click any point in trend charts to open the full evaluation report
- **Standard Deviation Bands**: Visual representation of score uncertainty in trend charts

## Tech Stack

- Vue 3 + Vite
- Vue Router
- Chart.js
- Vanilla CSS

## Data Source

All course and CEQ information comes from official LTH websites:
- Course data: [LTH Course API](https://api.lth.lu.se/lot/)
- CEQ reports: [LTH CEQ Archive](https://www.ceq.lth.se/rapporter/)

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Project Structure

```
src/
├── components/
│   ├── CourseDetail.vue      # Single course view with trends
│   ├── CompareView.vue       # Two-course comparison
│   ├── TrendChart.vue        # Chart.js component for trends
│   ├── CourseSidebar.vue     # Scrollable course list
│   └── WelcomeView.vue       # Home page with stats
├── composables/
│   └── useCourseData.js      # Data loading logic
└── router/
    └── index.js              # Route configuration
```
