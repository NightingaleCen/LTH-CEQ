# LTH Course Evaluation Scraper

A Python scraper that fetches course information and CEQ (Course Experience Questionnaire) evaluation data from Lund University's Faculty of Engineering (LTH).

## Features

- Fetches course information from LTH API
- Scrapes historical course evaluation data from CEQ reports
- Stores data in SQLite database
- Exports data to JSON format

## Usage

### Run the full pipeline

```bash
python scraper.py
```

This will:
1. Initialize the database
2. Fetch courses for the MMSR program
3. Scrape all course evaluations
4. Export data to `output/courses_data.json`

### Custom program code

Modify the last line in `scraper.py`:
```python
if __name__ == "__main__":
    main("YOUR_PROGRAM_CODE")  # e.g., "MMSR", "D", etc.
```

### Use individual functions

```python
from scraper import init_db, get_courses, fetch_and_store_evaluations, export_to_json

# initialize database
init_db()

# fetch courses for a program
get_courses("MMSR")

# fetch evaluations for a specific course
fetch_and_store_evaluations("FMAN20")

# export to JSON
export_to_json()
```

## Output

The script generates:
- `lth_data.db` - SQLite database with three tables:
  - `courses` - Basic course information
  - `course_offerings` - Course offering details (multiple per course)
  - `course_evaluations` - CEQ evaluation scores
- `output/courses_data.json` - JSON file with all data for frontend use

## Database Schema

### courses
- course_code (PRIMARY KEY)
- name, credits, grading_scale
- course_syllabus_url, course_evaluation_archive_url

### course_offerings
- id (PRIMARY KEY)
- course_code, start_period, end_period
- start_year, end_year

### course_evaluations
- id (PRIMARY KEY)
- course_code, academic_year, semester, period, url
- Six CEQ metrics (score + std for each):
  - good_teaching
  - clear_goals_and_standards
  - appropriate_assessment
  - appropriate_workload
  - important_for_education
  - overall_satisfaction

## Notes

- The scraper includes delays between requests to be respectful to servers
