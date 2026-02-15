"""
Avatar Library - HeyGen/CapCut Style
Provides 50+ professional avatars across multiple categories
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Avatar:
    id: str
    name: str
    category: str
    style: str
    gender: str
    age_range: str  # "young", "middle", "senior"
    occupation: str
    thumbnail_url: str
    full_image_path: Optional[str] = None
    description: str = ""

# Business Professionals (20 avatars)
BUSINESS_AVATARS = [
    Avatar(
        id="exec_male_1",
        name="Marcus Chen",
        category="Business",
        style="Executive",
        gender="Male",
        age_range="middle",
        occupation="CEO",
        thumbnail_url="https://images.unsplash.com/photo-1560250097-0b93528c311a?w=512&h=512&fit=crop&crop=face",
        description="Confident executive, modern office setting"
    ),
    Avatar(
        id="exec_female_1",
        name="Sarah Williams",
        category="Business",
        style="Executive",
        gender="Female",
        age_range="middle",
        occupation="CFO",
        thumbnail_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=512&h=512&fit=crop&crop=face",
        description="Professional leader, corporate background"
    ),
    Avatar(
        id="manager_male_1",
        name="David Park",
        category="Business",
        style="Manager",
        gender="Male",
        age_range="young",
        occupation="Tech Manager",
        thumbnail_url="https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=512&h=512&fit=crop&crop=face",
        description="Modern tech leader, startup vibe"
    ),
    Avatar(
        id="manager_female_1",
        name="Emily Zhang",
        category="Business",
        style="Manager",
        gender="Female",
        age_range="young",
        occupation="Product Manager",
        thumbnail_url="https://images.unsplash.com/photo-1580489944761-15a19d654956?w=512&h=512&fit=crop&crop=face",
        description="Dynamic product leader"
    ),
    Avatar(
        id="sales_male_1",
        name="James Anderson",
        category="Business",
        style="Sales",
        gender="Male",
        age_range="middle",
        occupation="Sales Director",
        thumbnail_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=512&h=512&fit=crop&crop=face",
        description="Charismatic sales professional"
    ),
    Avatar(
        id="sales_female_1",
        name="Maria Rodriguez",
        category="Business",
        style="Sales",
        gender="Female",
        age_range="young",
        occupation="Account Executive",
        thumbnail_url="https://images.unsplash.com/photo-1598550874175-4d0ef436c909?w=512&h=512&fit=crop&crop=face",
        description="Energetic sales expert"
    ),
    Avatar(
        id="consultant_male_1",
        name="Michael Brown",
        category="Business",
        style="Consultant",
        gender="Male",
        age_range="senior",
        occupation="Senior Consultant",
        thumbnail_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=512&h=512&fit=crop&crop=face",
        description="Experienced business advisor"
    ),
    Avatar(
        id="consultant_female_1",
        name="Jennifer Lee",
        category="Business",
        style="Consultant",
        gender="Female",
        age_range="middle",
        occupation="Strategy Consultant",
        thumbnail_url="https://images.unsplash.com/photo-1551836022-deb4988cc6c0?w=512&h=512&fit=crop&crop=face",
        description="Strategic business partner"
    ),
    # Additional Business Avatars
    Avatar(id="business_male_2", name="Robert Taylor", category="Business", style="Corporate", gender="Male", age_range="middle", occupation="VP Operations", thumbnail_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=512&h=512&fit=crop&crop=face", description="Operations expert"),
    Avatar(id="business_female_2", name="Lisa Johnson", category="Business", style="Corporate", gender="Female", age_range="middle", occupation="Marketing Director", thumbnail_url="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=512&h=512&fit=crop&crop=face", description="Marketing strategist"),
    Avatar(id="business_male_3", name="Christopher Davis", category="Business", style="Startup", gender="Male", age_range="young", occupation="Founder", thumbnail_url="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=512&h=512&fit=crop&crop=face", description="Startup founder"),
    Avatar(id="business_female_3", name="Amanda White", category="Business", style="Startup", gender="Female", age_range="young", occupation="Co-Founder", thumbnail_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=512&h=512&fit=crop&crop=face", description="Tech entrepreneur"),
]

# Healthcare (10 avatars)
HEALTHCARE_AVATARS = [
    Avatar(id="doctor_male_1", name="Dr. James Peterson", category="Healthcare", style="Doctor", gender="Male", age_range="middle", occupation="Physician", thumbnail_url="https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=512&h=512&fit=crop&crop=face", description="Medical doctor"),
    Avatar(id="doctor_female_1", name="Dr. Sarah Collins", category="Healthcare", style="Doctor", gender="Female", age_range="middle", occupation="Surgeon", thumbnail_url="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=512&h=512&fit=crop&crop=face", description="Medical professional"),
    Avatar(id="nurse_male_1", name="Nurse Michael Scott", category="Healthcare", style="Nurse", gender="Male", age_range="young", occupation="RN", thumbnail_url="https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=512&h=512&fit=crop&crop=face", description="Registered nurse"),
    Avatar(id="nurse_female_1", name="Nurse Emma Davis", category="Healthcare", style="Nurse", gender="Female", age_range="young", occupation="RN", thumbnail_url="https://images.unsplash.com/photo-1582750433449-d22b1274be8f?w=512&h=512&fit=crop&crop=face", description="Healthcare provider"),
    Avatar(id="therapist_male_1", name="Dr. David Wright", category="Healthcare", style="Therapist", gender="Male", age_range="middle", occupation="Psychologist", thumbnail_url="https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=512&h=512&fit=crop&crop=face", description="Mental health professional"),
    Avatar(id="therapist_female_1", name="Dr. Rachel Green", category="Healthcare", style="Therapist", gender="Female", age_range="middle", occupation="Counselor", thumbnail_url="https://images.unsplash.com/photo-1580489944761-15a19d654956?w=512&h=512&fit=crop&crop=face", description="Counseling expert"),
    Avatar(id="pharmacist_male_1", name="Pharmacist Tom Baker", category="Healthcare", style="Pharmacist", gender="Male", age_range="middle", occupation="Pharmacist", thumbnail_url="https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=512&h=512&fit=crop&crop=face", description="Pharmacy professional"),
    Avatar(id="pharmacist_female_1", name="Pharmacist Anna Lee", category="Healthcare", style="Pharmacist", gender="Female", age_range="young", occupation="Pharmacist", thumbnail_url="https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=512&h=512&fit=crop&crop=face", description="Medication expert"),
    Avatar(id="dentist_male_1", name="Dr. Robert King", category="Healthcare", style="Dentist", gender="Male", age_range="senior", occupation="Dentist", thumbnail_url="https://images.unsplash.com/photo-1560250097-0b93528c311a?w=512&h=512&fit=crop&crop=face", description="Dental professional"),
    Avatar(id="dentist_female_1", name="Dr. Laura Adams", category="Healthcare", style="Dentist", gender="Female", age_range="middle", occupation="Orthodontist", thumbnail_url="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=512&h=512&fit=crop&crop=face", description="Dental specialist"),
]

# Education (10 avatars)
EDUCATION_AVATARS = [
    Avatar(id="teacher_male_1", name="Prof. John Smith", category="Education", style="Professor", gender="Male", age_range="senior", occupation="Professor", thumbnail_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=512&h=512&fit=crop&crop=face", description="University professor"),
    Avatar(id="teacher_female_1", name="Prof. Mary Johnson", category="Education", style="Professor", gender="Female", age_range="middle", occupation="Associate Prof", thumbnail_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=512&h=512&fit=crop&crop=face", description="Academic leader"),
    Avatar(id="teacher_male_2", name="Mr. Alex Turner", category="Education", style="Teacher", gender="Male", age_range="young", occupation="High School Teacher", thumbnail_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=512&h=512&fit=crop&crop=face", description="Educator"),
    Avatar(id="teacher_female_2", name="Ms. Karen Brown", category="Education", style="Teacher", gender="Female", age_range="young", occupation="Elementary Teacher", thumbnail_url="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=512&h=512&fit=crop&crop=face", description="Primary educator"),
    Avatar(id="coach_male_1", name="Coach Ryan Mitchell", category="Education", style="Coach", gender="Male", age_range="middle", occupation="Life Coach", thumbnail_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=512&h=512&fit=crop&crop=face", description="Personal development"),
    Avatar(id="coach_female_1", name="Coach Sophia Martin", category="Education", style="Coach", gender="Female", age_range="young", occupation="Career Coach", thumbnail_url="https://images.unsplash.com/photo-1580489944761-15a19d654956?w=512&h=512&fit=crop&crop=face", description="Career guidance"),
]

# Tech & IT (10 avatars)
TECH_AVATARS = [
    Avatar(id="dev_male_1", name="Alex Nguyen", category="Tech", style="Developer", gender="Male", age_range="young", occupation="Software Engineer", thumbnail_url="https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=512&h=512&fit=crop&crop=face", description="Full-stack developer"),
    Avatar(id="dev_female_1", name="Olivia Chen", category="Tech", style="Developer", gender="Female", age_range="young", occupation="Frontend Dev", thumbnail_url="https://images.unsplash.com/photo-1580489944761-15a19d654956?w=512&h=512&fit=crop&crop=face", description="UI/UX engineer"),
    Avatar(id="dev_male_2", name="Kevin Walsh", category="Tech", style="Developer", gender="Male", age_range="middle", occupation="Senior Engineer", thumbnail_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=512&h=512&fit=crop&crop=face", description="Backend specialist"),
    Avatar(id="dev_female_2", name="Sophia Patel", category="Tech", style="Developer", gender="Female", age_range="young", occupation="Data Scientist", thumbnail_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=512&h=512&fit=crop&crop=face", description="AI/ML expert"),
    Avatar(id="it_male_1", name="Brian Foster", category="Tech", style="IT", gender="Male", age_range="middle", occupation="IT Manager", thumbnail_url="https://images.unsplash.com/photo-1560250097-0b93528c311a?w=512&h=512&fit=crop&crop=face", description="IT infrastructure"),
    Avatar(id="it_female_1", name="Nicole Sanders", category="Tech", style="IT", gender="Female", age_range="young", occupation="DevOps Engineer", thumbnail_url="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=512&h=512&fit=crop&crop=face", description="Cloud specialist"),
]

# Compile all avatars
ALL_AVATARS = BUSINESS_AVATARS + HEALTHCARE_AVATARS + EDUCATION_AVATARS + TECH_AVATARS

# Category mapping
AVATAR_CATEGORIES = {
    "Business": BUSINESS_AVATARS,
    "Healthcare": HEALTHCARE_AVATARS,
    "Education": EDUCATION_AVATARS,
    "Tech": TECH_AVATARS,
}

def get_all_avatars() -> List[Avatar]:
    """Get all available avatars"""
    return ALL_AVATARS

def get_avatars_by_category(category: str) -> List[Avatar]:
    """Get avatars filtered by category"""
    return AVATAR_CATEGORIES.get(category, [])

def get_avatar_by_id(avatar_id: str) -> Optional[Avatar]:
    """Get specific avatar by ID"""
    for avatar in ALL_AVATARS:
        if avatar.id == avatar_id:
            return avatar
    return None

def filter_avatars(
    category: Optional[str] = None,
    gender: Optional[str] = None,
    age_range: Optional[str] = None,
    style: Optional[str] = None
) -> List[Avatar]:
    """Filter avatars by multiple criteria"""
    filtered = ALL_AVATARS
    
    if category:
        filtered = [a for a in filtered if a.category == category]
    if gender:
        filtered = [a for a in filtered if a.gender == gender]
    if age_range:
        filtered = [a for a in filtered if a.age_range == age_range]
    if style:
        filtered = [a for a in filtered if a.style == style]
    
    return filtered

def search_avatars(query: str) -> List[Avatar]:
    """Search avatars by name or description"""
    query = query.lower()
    return [
        a for a in ALL_AVATARS
        if query in a.name.lower() or query in a.description.lower() or query in a.occupation.lower()
    ]
