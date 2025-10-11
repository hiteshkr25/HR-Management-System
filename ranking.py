"""
Smart Ranking Algorithm for HR Management System
Weighted scoring: 50% skill match + 30% CGPA + 20% branch relevance
"""

def calculate_fit_score(student, job_request):
    """
    Calculate fit score (0-100) for a student based on job requirements
    
    Args:
        student: dict with keys: skills, cgpa, branch
        job_request: dict with keys: required_skills, min_cgpa, branch_pref
    
    Returns:
        tuple: (fit_score, skill_score) - fit score and skill match score
    """
    # 1. Skill Match Score (50% weight)
    skill_score = calculate_skill_match(
        student['skills'].lower(),
        job_request['required_skills'].lower()
    )
    
    # 2. CGPA Score (30% weight)
    gpa_score = calculate_gpa_score(
        student['cgpa'],
        job_request['min_cgpa']
    )
    
    # 3. Branch Relevance Score (20% weight)
    branch_score = calculate_branch_match(
        student['branch'],
        job_request['branch_pref']
    )
    
    # Calculate weighted total
    fit_score = (skill_score * 0.5) + (gpa_score * 0.3) + (branch_score * 0.2)
    
    return round(fit_score, 2), skill_score


def calculate_skill_match(student_skills, required_skills):
    """
    Calculate skill match score based on keyword overlap
    Returns score between 0-100
    """
    # Extract individual skills
    student_skill_set = set([s.strip() for s in student_skills.split(',')])
    required_skill_set = set([s.strip() for s in required_skills.split(',')])
    
    if not required_skill_set:
        return 100
    
    # Calculate exact matches
    exact_matches = student_skill_set.intersection(required_skill_set)
    exact_match_score = (len(exact_matches) / len(required_skill_set)) * 100
    
    # Calculate partial matches (substring matching)
    partial_match_count = 0
    for req_skill in required_skill_set:
        if req_skill not in exact_matches:
            for student_skill in student_skill_set:
                if req_skill in student_skill or student_skill in req_skill:
                    partial_match_count += 0.5
                    break
    
    partial_match_score = (partial_match_count / len(required_skill_set)) * 100
    
    # Combine exact and partial matches (exact matches weighted higher)
    total_score = min(100, exact_match_score + partial_match_score)
    
    return total_score


def calculate_gpa_score(student_gpa, min_gpa):
    """
    Calculate CGPA score (out of 10)
    Returns 0 if below minimum, scales from 0-100 based on how much above minimum
    """
    # Convert Decimal to float to avoid type mixing issues
    student_gpa = float(student_gpa)
    min_gpa = float(min_gpa)
    
    if student_gpa < min_gpa:
        return 0
    
    # If CGPA meets minimum, score based on excellence above minimum
    # Score = 50 (base for meeting minimum) + 50 * ((current - min) / (10.0 - min))
    if min_gpa >= 10.0:
        return 100
    
    base_score = 50
    excellence_score = ((student_gpa - min_gpa) / (10.0 - min_gpa)) * 50
    
    return min(100, base_score + excellence_score)


def calculate_branch_match(student_branch, preferred_branch):
    """
    Calculate branch relevance score
    Returns 100 for exact match, 50 for related branches, 0 for no match
    """
    if not preferred_branch or preferred_branch.strip() == '':
        return 100  # No preference means all branches are equally valid
    
    student_branch_lower = student_branch.lower().strip()
    preferred_branch_lower = preferred_branch.lower().strip()
    
    # Exact match
    if student_branch_lower == preferred_branch_lower:
        return 100
    
    # Related branches (CS, IT are related)
    related_groups = [
        ['computer science', 'information technology', 'software engineering'],
        ['electronics', 'electrical', 'communication'],
        ['mechanical', 'automobile', 'production'],
    ]
    
    for group in related_groups:
        if student_branch_lower in group and preferred_branch_lower in group:
            return 70
    
    # No match
    return 0


def rank_students(students, job_request):
    """
    Rank all students for a given job request
    
    Args:
        students: list of student dicts
        job_request: dict with job requirements
    
    Returns:
        list of tuples (student, fit_score, skill_score) sorted by fit_score descending
    """
    ranked = []
    
    for student in students:
        fit_score, skill_score = calculate_fit_score(student, job_request)
        ranked.append((student, fit_score, skill_score))
    
    # Sort by fit_score descending
    ranked.sort(key=lambda x: x[1], reverse=True)
    
    return ranked
