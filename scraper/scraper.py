"""
LTH Course Evaluation Scraper

This script scrapes course information and evaluation data from Lund University's
Faculty of Engineering (LTH).

Contact:
Pengjun Cen <nightingalecen@outlook.com>
"""

import requests
import sqlite3
import sys
import time
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm

# get script directory to ensure files are created in the correct location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "lth_data.db")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")


def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # drop all existing tables
    cursor.execute("DROP TABLE IF EXISTS course_evaluations")
    cursor.execute("DROP TABLE IF EXISTS course_offerings")
    cursor.execute("DROP TABLE IF EXISTS program_courses")
    cursor.execute("DROP TABLE IF EXISTS courses")
    cursor.execute("DROP TABLE IF EXISTS programmes")

    # programme list
    cursor.execute("""
    CREATE TABLE programmes (
    programme_code TEXT PRIMARY KEY,
    name_sv TEXT,
    name_en TEXT
    )
    """)

    # basic course information
    cursor.execute("""
    CREATE TABLE courses (
    course_code TEXT PRIMARY KEY,
    name TEXT,
    credits REAL,
    grading_scale TEXT,
    course_syllabus_url TEXT,
    course_evaluation_archive_url TEXT
    )
    """)

    # programme-course mapping
    cursor.execute("""
    CREATE TABLE program_courses (
    programme_code TEXT,
    course_code TEXT,
    PRIMARY KEY (programme_code, course_code),
    FOREIGN KEY (course_code) REFERENCES courses(course_code)
    )
    """)

    # course offering information
    cursor.execute("""
    CREATE TABLE course_offerings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT,
    start_period INT,
    end_period INT,
    start_year TEXT,
    end_year TEXT,
    FOREIGN KEY (course_code) REFERENCES courses(course_code)
    )
    """)

    # course evaluation data
    cursor.execute("""
    CREATE TABLE course_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT,
    academic_year INTEGER,
    semester TEXT,
    period TEXT,
    url TEXT,
    good_teaching_score REAL,
    good_teaching_std REAL,
    clear_goals_and_standards_score REAL,
    clear_goals_and_standards_std REAL,
    appropriate_assessment_score REAL,
    appropriate_assessment_std REAL,
    appropriate_workload_score REAL,
    appropriate_workload_std REAL,
    important_for_education_score REAL,
    important_for_education_std REAL,
    overall_satisfaction_score REAL,
    overall_satisfaction_std REAL,
    UNIQUE(course_code, academic_year, semester, period),
    FOREIGN KEY (course_code) REFERENCES courses(course_code)
    )
    """)

    conn.commit()
    conn.close()


def get_programmes():
    """Fetch all LTH programmes from API and store in database."""
    url = "https://api.lth.lu.se/lot/courses/programmes"
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to get programmes: {response.status_code}")

    programmes = response.json()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for prog in programmes:
        cursor.execute(
            "INSERT OR REPLACE INTO programmes (programme_code, name_sv, name_en) VALUES (?, ?, ?)",
            (
                prog["programmeCode"],
                prog.get("programme_sv", ""),
                prog.get("programme_en", ""),
            ),
        )

    conn.commit()
    conn.close()

    codes = sorted(prog["programmeCode"] for prog in programmes)
    print(f"Found {len(codes)} programmes: {', '.join(codes)}")
    return codes


def get_current_academic_year_id(program_code: str):
    """Get the current academic year ID for a program."""
    url = f"https://api.lth.lu.se/lot/courses/academic-years?programmeCode={program_code}&includePreliminary=false"
    response = requests.get(url)
    data = response.json()
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to get current academic year id: {response.status_code}"
        )

    for item in data:
        if item.get("current") is True:
            return item["academicYearId"]

    raise RuntimeError(
        f"No current academic year id found for program code: {program_code}"
    )


def get_courses(program_code: str):
    """Fetch all courses for a program and store in database."""
    academic_year_id = get_current_academic_year_id(program_code)

    url = f"https://api.lth.lu.se/lot/courses?programmeCode={program_code}&academicYearId={academic_year_id}"
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to get courses: {response.status_code}")

    course_info = response.json()

    course_sql = """
    INSERT OR REPLACE INTO courses (course_code, name, credits, grading_scale, course_syllabus_url, course_evaluation_archive_url)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    offering_sql = """
    INSERT INTO course_offerings (course_code, start_period, end_period, start_year, end_year)
    VALUES (?, ?, ?, ?, ?)
    """

    program_course_sql = """
    INSERT OR IGNORE INTO program_courses (programme_code, course_code)
    VALUES (?, ?)
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for course in tqdm(
        course_info, desc=f"Getting course information for {program_code}"
    ):
        if course["type"] != "programme_course":
            continue

        course_code = course["courseCode"]

        # always record programme-course mapping
        cursor.execute(program_course_sql, (program_code, course_code))

        # skip full processing if course already exists (shared across programmes)
        cursor.execute(
            "SELECT course_code FROM courses WHERE course_code = ?",
            (course_code,),
        )
        if cursor.fetchone() is not None:
            continue

        try:
            year_info = requests.get(
                f"https://api.lth.lu.se/lot/courses/academic-years?courseCode={course_code}"
            ).json()
            if len(year_info) == 0:
                raise RuntimeError(
                    f"No start year info found for course code: {course_code}"
                )
            start_year = year_info[0]["academicYearId"]
            end_year = year_info[-1]["academicYearId"]

            # insert basic course information
            cursor.execute(
                course_sql,
                (
                    course_code,
                    course["name_en"],
                    course["credits"],
                    course["gradingScale"],
                    f"https://kurser.lth.se/lot/course-syllabus/{course['courseSyllabusPath_sv']}",
                    course["evaluationUrl_en"],
                ),
            )

            # delete old offerings for this course to avoid duplicates
            cursor.execute(
                "DELETE FROM course_offerings WHERE course_code = ?",
                (course_code,),
            )

            # insert all course offerings
            for time_plan in course["timePlans"]:
                start_sp = time_plan.get("startSpNr")
                end_sp = time_plan.get("endSpNr")
                if start_sp is None or end_sp is None:
                    print(f"  Warning: skipping timePlan for {course_code} — missing startSpNr or endSpNr")
                    continue
                cursor.execute(
                    offering_sql,
                    (
                        course_code,
                        start_sp,
                        end_sp,
                        start_year,
                        end_year,
                    ),
                )

            time.sleep(0.5)  # slow down a bit just to be polite
        except Exception as e:
            print(f"  Warning: skipping course {course_code} due to error: {e}")
            continue

    conn.commit()
    conn.close()


def get_course_evaluation_urls(course_code: str):
    """Generate evaluation URLs for a course with metadata.

    Converts academic year format (e.g., 24_25) and period numbers (1-4)
    to CEQ URL format with semesters (HT/VT) and periods (LP1/LP2).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # get all course offerings
    cursor.execute(
        "SELECT start_year, end_year, end_period FROM course_offerings WHERE course_code = ?",
        (course_code,),
    )
    offerings = cursor.fetchall()
    conn.close()

    if not offerings:
        print(f"Course {course_code} not found in database")
        return []

    evaluation_info = []

    # generate URLs for each offering
    for start_year, end_year, end_period in offerings:
        start_year_parts = start_year.split("_")
        end_year_parts = end_year.split("_")
        start_first_year = int(start_year_parts[0])
        end_first_year = int(end_year_parts[0])

        # generate URLs for all academic years from start to end
        for year_offset in range(end_first_year - start_first_year + 1):
            first_year = start_first_year + year_offset
            second_year = first_year + 1

            full_first_year = 2000 + first_year
            full_second_year = 2000 + second_year

            # convert period to semester and LP
            # periods 1,2 -> HT (autumn) LP1/LP2, use first year
            # periods 3,4 -> VT (spring) LP1/LP2, use second year
            if end_period in [1, 2]:
                semester = "HT"
                lp = f"LP{end_period}"
                year_for_url = full_first_year
            else:
                semester = "VT"
                lp = f"LP{end_period - 2}"
                year_for_url = full_second_year

            url = f"https://www.ceq.lth.se/rapporter/ceq/{year_for_url}_{semester}/{lp}/{course_code}_{year_for_url}_{semester}_{lp}_slutrapport_en.html"

            evaluation_info.append(
                {
                    "course_code": course_code,
                    "academic_year": year_for_url,
                    "semester": semester,
                    "period": lp,
                    "url": url,
                }
            )

    return evaluation_info


def fetch_and_store_evaluations(course_code: str):
    """Fetch and store all evaluations for a course.

    Skips evaluations that return 404 or have incomplete data.
    """
    evaluation_info = get_course_evaluation_urls(course_code)

    if not evaluation_info:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql = """
    INSERT OR REPLACE INTO course_evaluations (
        course_code, academic_year, semester, period, url,
        good_teaching_score, good_teaching_std,
        clear_goals_and_standards_score, clear_goals_and_standards_std,
        appropriate_assessment_score, appropriate_assessment_std,
        appropriate_workload_score, appropriate_workload_std,
        important_for_education_score, important_for_education_std,
        overall_satisfaction_score, overall_satisfaction_std
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for info in tqdm(evaluation_info, desc=f"Fetching evaluations for {course_code}"):
        result = parse_course_evaluation(info["url"])

        # skip if evaluation does not exist (404) or has no data
        if result is None or len(result) == 0:
            continue

        # extract scores and stds, skip if essential data is missing
        try:

            def get_score_std(data, key):
                """Extract score and std from data, return None if missing or invalid."""
                item = data.get(key, {})
                score_str = item.get("score", "")
                std_str = item.get("std", "")

                if not score_str or not std_str:
                    return None, None

                try:
                    return float(score_str), float(std_str)
                except ValueError:
                    return None, None

            # get all values
            gt_score, gt_std = get_score_std(result, "good_teaching")
            cg_score, cg_std = get_score_std(result, "clear_goals_and_standards")
            aa_score, aa_std = get_score_std(result, "appropriate_assessment")
            aw_score, aw_std = get_score_std(result, "appropriate_workload")
            ie_score, ie_std = get_score_std(
                result, "the_course_seems_important_for_my_education"
            )
            os_score, os_std = get_score_std(
                result, "overall_i_am_satisfied_with_this_course"
            )

            # check if all values are present
            all_values = [
                gt_score,
                gt_std,
                cg_score,
                cg_std,
                aa_score,
                aa_std,
                aw_score,
                aw_std,
                ie_score,
                ie_std,
                os_score,
                os_std,
            ]

            if any(v is None for v in all_values):
                continue

            cursor.execute(
                sql,
                (
                    info["course_code"],
                    info["academic_year"],
                    info["semester"],
                    info["period"],
                    info["url"],
                    gt_score,
                    gt_std,
                    cg_score,
                    cg_std,
                    aa_score,
                    aa_std,
                    aw_score,
                    aw_std,
                    ie_score,
                    ie_std,
                    os_score,
                    os_std,
                ),
            )
        except Exception as e:
            print(f"Error storing evaluation for {info['url']}: {e}")
            continue

        time.sleep(0.5)  # slow down a bit just to be polite

    conn.commit()
    conn.close()


def parse_course_evaluation(url: str):
    """Parse course evaluation HTML and extract CEQ scores.

    Returns:
        dict: Evaluation scores and standard deviations, or None if page not found.
    """
    response = requests.get(url)
    if response.status_code == 404:
        # evaluation report does not exist (maybe the semester is not over yet or the course is not offered in this semester)
        return None
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch {url}: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # CEQ evaluation categories
    keys = [
        "Good Teaching",
        "Clear Goals and Standards",
        "Appropriate Assessment",
        "Appropriate Workload",
        "The course seems important for my education",
        "Overall, I am satisfied with this course",
    ]
    results = {}

    # extract scores from table rows
    rows = soup.find_all("tr")
    for key in keys:
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 3 and cells[0].get_text(strip=True) == key:
                score = cells[1].get_text(strip=True)
                std = cells[2].get_text(strip=True)
                results[key.lower().replace(" ", "_").replace(",", "")] = {
                    "score": score,
                    "std": std,
                }
                break

    return results


def export_to_json(output_dir=None):
    """Export all course and evaluation data to JSON file.

    Args:
        output_dir: Output directory path, defaults to script_dir/output

    Returns:
        str: Path to the generated JSON file.
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR

    # create output directory if not exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # get all courses
    cursor.execute("""
        SELECT course_code, name, credits, grading_scale, 
               course_syllabus_url, course_evaluation_archive_url
        FROM courses
        ORDER BY course_code
    """)
    courses_data = cursor.fetchall()

    # get all programme-course mappings (only programmes that have courses)
    cursor.execute("""
        SELECT pc.programme_code, p.name_sv, p.name_en, pc.course_code
        FROM program_courses pc
        JOIN programmes p ON pc.programme_code = p.programme_code
        ORDER BY pc.programme_code, pc.course_code
    """)
    programme_rows = cursor.fetchall()

    programs = {}
    for code, name_sv, name_en, course_code in programme_rows:
        if code not in programs:
            programs[code] = {
                "name_sv": name_sv,
                "name_en": name_en,
                "course_codes": [],
            }
        programs[code]["course_codes"].append(course_code)

    result = {
        "courses": [],
        "programs": programs,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_courses": len(courses_data),
            "total_evaluations": 0,
        },
    }

    total_evaluations = 0

    for course_code, name, credits, grading_scale, syllabus_url, archive_url in tqdm(
        courses_data, desc="Exporting courses"
    ):
        # get course offerings
        cursor.execute(
            """
            SELECT start_period, end_period, start_year, end_year
            FROM course_offerings
            WHERE course_code = ?
        """,
            (course_code,),
        )
        offerings_data = cursor.fetchall()

        offerings = [
            {"start_period": sp, "end_period": ep, "start_year": sy, "end_year": ey}
            for sp, ep, sy, ey in offerings_data
        ]

        # get course evaluations
        cursor.execute(
            """
            SELECT academic_year, semester, period, url,
                   good_teaching_score, good_teaching_std,
                   clear_goals_and_standards_score, clear_goals_and_standards_std,
                   appropriate_assessment_score, appropriate_assessment_std,
                   appropriate_workload_score, appropriate_workload_std,
                   important_for_education_score, important_for_education_std,
                   overall_satisfaction_score, overall_satisfaction_std
            FROM course_evaluations
            WHERE course_code = ?
            ORDER BY academic_year DESC, semester, period
        """,
            (course_code,),
        )
        evaluations_data = cursor.fetchall()

        evaluations = []
        for eval_row in evaluations_data:
            (
                year,
                semester,
                period,
                url,
                gt_s,
                gt_std,
                cg_s,
                cg_std,
                aa_s,
                aa_std,
                aw_s,
                aw_std,
                ie_s,
                ie_std,
                os_s,
                os_std,
            ) = eval_row

            evaluations.append(
                {
                    "academic_year": year,
                    "semester": semester,
                    "period": period,
                    "url": url,
                    "scores": {
                        "good_teaching": {"score": gt_s, "std": gt_std},
                        "clear_goals_and_standards": {"score": cg_s, "std": cg_std},
                        "appropriate_assessment": {"score": aa_s, "std": aa_std},
                        "appropriate_workload": {"score": aw_s, "std": aw_std},
                        "important_for_education": {"score": ie_s, "std": ie_std},
                        "overall_satisfaction": {"score": os_s, "std": os_std},
                    },
                }
            )

        total_evaluations += len(evaluations)

        result["courses"].append(
            {
                "course_code": course_code,
                "name": name,
                "credits": credits,
                "grading_scale": grading_scale,
                "course_syllabus_url": syllabus_url,
                "course_evaluation_archive_url": archive_url,
                "offerings": offerings,
                "evaluations": evaluations,
            }
        )

    conn.close()

    result["metadata"]["total_evaluations"] = total_evaluations

    # write to JSON file
    output_file = os.path.join(output_dir, "courses_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(
        f"\nExported {len(courses_data)} courses with {total_evaluations} evaluations to {output_file}"
    )
    return output_file


def main(programme_codes=None):
    """Main function to scrape and export course data.

    Args:
        programme_codes: List of programme codes, or None to scrape all programmes.
    """
    print("=== Step 1: Initialize database ===")
    init_db()

    print("\n=== Step 2: Fetch programmes ===")
    all_programmes = get_programmes()

    if programme_codes is None:
        programme_codes = all_programmes
    else:
        programme_codes = [pc for pc in programme_codes if pc in all_programmes]
        if not programme_codes:
            raise RuntimeError(
                f"None of the specified programme codes found. "
                f"Available: {', '.join(all_programmes)}"
            )

    print(f"\n=== Step 3: Fetch courses for {len(programme_codes)} programme(s) ===")
    for i, pc in enumerate(programme_codes):
        print(f"\n[{i+1}/{len(programme_codes)}] Programme {pc}")
        try:
            get_courses(pc)
        except Exception as e:
            print(f"  Warning: skipping programme {pc} due to error: {e}")
            continue

    print("\n=== Step 4: Fetch evaluations for all courses ===")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT course_code FROM courses")
    course_codes = [row[0] for row in cursor.fetchall()]
    conn.close()

    for course_code in course_codes:
        print(f"\nFetching evaluations for {course_code}...")
        fetch_and_store_evaluations(course_code)

    print("\n=== Step 5: Export data to JSON ===")
    export_to_json()

    print("\n=== Done! ===")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # single programme mode: e.g. 'uv run scraper.py MMSR'
        main([sys.argv[1]])
    else:
        # full mode: scrape all programmes
        main()
