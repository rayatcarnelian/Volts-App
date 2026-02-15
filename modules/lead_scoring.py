"""
VOLTS Lead Scoring Engine
==========================
Enterprise-grade lead scoring system modeled after HubSpot, Apollo.io, and Salesforce Einstein.

Features:
- Dual-score architecture (Fit + Engagement)
- Score decay for stale leads
- Configurable weights
- Detailed score breakdown
"""

import json
import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from modules.database import get_connection

# =============================================================================
# SCORING CONFIGURATION (Customizable Weights)
# =============================================================================

@dataclass
class ScoringConfig:
    """
    Configurable scoring weights - adjust these to match your business priorities.
    Inspired by HubSpot's customizable scoring rules.
    """
    
    # --- FIT SCORE WEIGHTS (Max ~50 pts) ---
    # Data Completeness
    weight_has_phone: int = 15
    weight_has_email: int = 10
    weight_has_name: int = 5
    weight_has_profile_url: int = 5
    weight_has_bio: int = 5
    
    # Source Quality (Higher = Better source)
    source_weights: Dict[str, int] = field(default_factory=lambda: {
        "Instagram": 10,
        "LinkedIn X-Ray": 10,
        "LinkedIn Sniper": 10,
        "PropertyGuru": 8,
        "iProperty": 8,
        "Google Maps": 6,
        "Telegram": 5,
        "Facebook": 5,
        "X Hunter": 4,
        "Manual": 2,
    })
    
    # --- ENGAGEMENT SCORE WEIGHTS (Max ~50 pts) ---
    # Status Progression
    status_weights: Dict[str, int] = field(default_factory=lambda: {
        "Client": 25,
        "Qualified": 20,
        "Contacted": 15,
        "Warm": 12,
        "New": 5,
        "Blacklisted": -50,  # Negative for bad leads
    })
    
    # Recency Bonus
    weight_recent_7_days: int = 15
    weight_recent_14_days: int = 8
    weight_recent_30_days: int = 3
    
    # Engagement Signals
    weight_has_notes: int = 5
    
    # --- SCORE DECAY (Recency Penalty) ---
    decay_7_days: int = 5
    decay_14_days: int = 10
    decay_30_days: int = 20
    
    # --- THRESHOLDS ---
    threshold_hot: int = 70
    threshold_warm: int = 40
    # Below warm = cold


# =============================================================================
# SCORE BREAKDOWN
# =============================================================================

@dataclass
class ScoreBreakdown:
    """
    Detailed breakdown of how a score was calculated.
    Inspired by Salesforce Einstein's "Top Positives/Negatives" display.
    """
    fit_score: int = 0
    engagement_score: int = 0
    recency_penalty: int = 0
    total_score: int = 0
    
    # Detailed factors
    fit_factors: List[Dict[str, Any]] = field(default_factory=list)
    engagement_factors: List[Dict[str, Any]] = field(default_factory=list)
    decay_factors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Classification
    grade: str = "COLD"  # HOT, WARM, COLD
    emoji: str = "❄️"
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> "ScoreBreakdown":
        if not json_str:
            return cls()
        try:
            data = json.loads(json_str)
            return cls(**data)
        except:
            return cls()


# =============================================================================
# LEAD SCORER
# =============================================================================

class LeadScorer:
    """
    Main scoring engine.
    Combines HubSpot's dual-score, Apollo's weighting, and Einstein's auto-refresh.
    """
    
    def __init__(self, config: Optional[ScoringConfig] = None):
        self.config = config or ScoringConfig()
    
    def calculate_fit_score(self, lead: Dict) -> tuple:
        """
        Calculate FIT score - "Is this lead right for us?"
        Based on data completeness and source quality.
        """
        score = 0
        factors = []
        
        # Data Completeness
        if lead.get('phone') or lead.get('primary_phone'):
            score += self.config.weight_has_phone
            factors.append({"factor": "Has Phone", "points": self.config.weight_has_phone, "positive": True})
        
        if lead.get('email') or lead.get('primary_email'):
            score += self.config.weight_has_email
            factors.append({"factor": "Has Email", "points": self.config.weight_has_email, "positive": True})
        
        if lead.get('name'):
            score += self.config.weight_has_name
            factors.append({"factor": "Has Name", "points": self.config.weight_has_name, "positive": True})
        
        if lead.get('profile_url'):
            score += self.config.weight_has_profile_url
            factors.append({"factor": "Has Profile URL", "points": self.config.weight_has_profile_url, "positive": True})
        
        if lead.get('bio') or lead.get('notes'):
            score += self.config.weight_has_bio
            factors.append({"factor": "Has Bio/Notes", "points": self.config.weight_has_bio, "positive": True})
        
        # Source Quality
        source = lead.get('source', 'Manual')
        source_points = self.config.source_weights.get(source, 2)
        score += source_points
        factors.append({"factor": f"Source: {source}", "points": source_points, "positive": True})
        
        return score, factors
    
    def calculate_engagement_score(self, lead: Dict) -> tuple:
        """
        Calculate ENGAGEMENT score - "How interested are they?"
        Based on status progression and activity.
        """
        score = 0
        factors = []
        
        # Status Progression
        status = lead.get('status') or lead.get('master_status', 'New')
        status_points = self.config.status_weights.get(status, 5)
        score += status_points
        factors.append({"factor": f"Status: {status}", "points": status_points, "positive": status_points > 0})
        
        # Recency Bonus (when was lead added?)
        created_at = lead.get('created_at') or lead.get('added_date')
        if created_at:
            try:
                if isinstance(created_at, str):
                    created_date = datetime.datetime.strptime(created_at[:10], "%Y-%m-%d").date()
                else:
                    created_date = created_at
                
                days_since_added = (datetime.date.today() - created_date).days
                
                if days_since_added <= 7:
                    score += self.config.weight_recent_7_days
                    factors.append({"factor": "Added in last 7 days", "points": self.config.weight_recent_7_days, "positive": True})
                elif days_since_added <= 14:
                    score += self.config.weight_recent_14_days
                    factors.append({"factor": "Added in last 14 days", "points": self.config.weight_recent_14_days, "positive": True})
                elif days_since_added <= 30:
                    score += self.config.weight_recent_30_days
                    factors.append({"factor": "Added in last 30 days", "points": self.config.weight_recent_30_days, "positive": True})
            except:
                pass
        
        # Has Notes (indicates engagement)
        if lead.get('notes'):
            notes = str(lead.get('notes', '')).strip()
            if notes and notes.lower() not in ['none', 'null', '']:
                score += self.config.weight_has_notes
                factors.append({"factor": "Has Notes", "points": self.config.weight_has_notes, "positive": True})
        
        return score, factors
    
    def calculate_recency_penalty(self, lead: Dict) -> tuple:
        """
        Calculate SCORE DECAY - penalty for leads going cold.
        Inspired by HubSpot's score decay feature.
        """
        penalty = 0
        factors = []
        
        # Use last_touched_at if available, else created_at
        last_touch = lead.get('last_touched_at') or lead.get('created_at') or lead.get('added_date')
        
        if last_touch:
            try:
                if isinstance(last_touch, str):
                    last_date = datetime.datetime.strptime(last_touch[:10], "%Y-%m-%d").date()
                else:
                    last_date = last_touch
                
                days_since_touch = (datetime.date.today() - last_date).days
                
                if days_since_touch >= 30:
                    penalty = self.config.decay_30_days
                    factors.append({"factor": "No contact 30+ days", "points": -penalty, "positive": False})
                elif days_since_touch >= 14:
                    penalty = self.config.decay_14_days
                    factors.append({"factor": "No contact 14+ days", "points": -penalty, "positive": False})
                elif days_since_touch >= 7:
                    penalty = self.config.decay_7_days
                    factors.append({"factor": "No contact 7+ days", "points": -penalty, "positive": False})
            except:
                pass
        
        return penalty, factors
    
    def score_lead(self, lead: Dict) -> ScoreBreakdown:
        """
        Calculate complete score for a single lead.
        Returns detailed breakdown.
        """
        # Calculate components
        fit_score, fit_factors = self.calculate_fit_score(lead)
        engagement_score, engagement_factors = self.calculate_engagement_score(lead)
        recency_penalty, decay_factors = self.calculate_recency_penalty(lead)
        
        # Total score (capped at 0 minimum)
        total_score = max(0, fit_score + engagement_score - recency_penalty)
        
        # Determine grade
        if total_score >= self.config.threshold_hot:
            grade = "🔥 HOT"
            emoji = "🔥"
        elif total_score >= self.config.threshold_warm:
            grade = "⚡ WARM"
            emoji = "⚡"
        else:
            grade = "❄️ COLD"
            emoji = "❄️"
        
        return ScoreBreakdown(
            fit_score=fit_score,
            engagement_score=engagement_score,
            recency_penalty=recency_penalty,
            total_score=total_score,
            fit_factors=fit_factors,
            engagement_factors=engagement_factors,
            decay_factors=decay_factors,
            grade=grade,
            emoji=emoji
        )
    
    def score_and_save(self, lead_id: int, lead: Dict) -> ScoreBreakdown:
        """
        Score a lead and persist to database.
        """
        breakdown = self.score_lead(lead)
        
        conn = get_connection()
        c = conn.cursor()
        
        c.execute("""
            UPDATE leads 
            SET total_score = ?,
                fit_score = ?,
                engagement_score = ?,
                recency_penalty = ?,
                last_scored_at = ?,
                score_factors = ?
            WHERE id = ?
        """, (
            breakdown.total_score,
            breakdown.fit_score,
            breakdown.engagement_score,
            breakdown.recency_penalty,
            datetime.datetime.now(),
            breakdown.to_json(),
            lead_id
        ))
        
        conn.commit()
        conn.close()
        
        return breakdown
    
    def rescore_all_leads(self) -> Dict[str, int]:
        """
        Rescore all leads in the database.
        Returns summary stats.
        """
        conn = get_connection()
        c = conn.cursor()
        
        # Get all leads
        c.execute("""
            SELECT 
                l.id, l.name, l.primary_email as email, l.primary_phone as phone,
                l.master_status as status, l.created_at, l.notes, l.last_touched_at,
                COALESCE(li.profile_url, i.profile_url, pa.profile_url) as profile_url,
                COALESCE(li.headline, i.bio_text, pa.specialty_area) as bio,
                CASE 
                    WHEN li.id IS NOT NULL THEN 'LinkedIn X-Ray'
                    WHEN i.id IS NOT NULL THEN 'Instagram'
                    WHEN pa.id IS NOT NULL THEN pa.source_portal
                    ELSE 'Manual' 
                END as source
            FROM leads l
            LEFT JOIN linkedin_profiles li ON l.id = li.lead_id
            LEFT JOIN instagram_profiles i ON l.id = i.lead_id
            LEFT JOIN property_agents pa ON l.id = pa.lead_id
        """)
        
        leads = c.fetchall()
        conn.close()
        
        stats = {"hot": 0, "warm": 0, "cold": 0, "total": 0}
        
        for lead_row in leads:
            lead = dict(lead_row)
            breakdown = self.score_and_save(lead['id'], lead)
            
            stats["total"] += 1
            if "HOT" in breakdown.grade:
                stats["hot"] += 1
            elif "WARM" in breakdown.grade:
                stats["warm"] += 1
            else:
                stats["cold"] += 1
        
        return stats


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_lead_score_breakdown(lead_id: int) -> Optional[ScoreBreakdown]:
    """
    Retrieve the score breakdown for a specific lead.
    """
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT score_factors FROM leads WHERE id = ?", (lead_id,))
    row = c.fetchone()
    conn.close()
    
    if row and row['score_factors']:
        return ScoreBreakdown.from_json(row['score_factors'])
    return None


def get_top_leads(limit: int = 10) -> list:
    """
    Get top-scoring leads for leaderboard.
    """
    conn = get_connection()
    
    query = f"""
        SELECT 
            l.id, l.name, l.primary_email as email, l.primary_phone as phone,
            l.master_status as status, l.total_score, l.fit_score, 
            l.engagement_score, l.recency_penalty, l.score_factors,
            CASE 
                WHEN li.id IS NOT NULL THEN 'LinkedIn X-Ray'
                WHEN i.id IS NOT NULL THEN 'Instagram'
                WHEN pa.id IS NOT NULL THEN pa.source_portal
                ELSE 'Manual' 
            END as source
        FROM leads l
        LEFT JOIN linkedin_profiles li ON l.id = li.lead_id
        LEFT JOIN instagram_profiles i ON l.id = i.lead_id
        LEFT JOIN property_agents pa ON l.id = pa.lead_id
        ORDER BY l.total_score DESC
        LIMIT {limit}
    """
    
    import pandas as pd
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


def get_score_distribution() -> Dict[str, int]:
    """
    Get distribution of scores for analytics.
    """
    conn = get_connection()
    c = conn.cursor()
    
    config = ScoringConfig()
    
    c.execute(f"""
        SELECT 
            SUM(CASE WHEN total_score >= {config.threshold_hot} THEN 1 ELSE 0 END) as hot,
            SUM(CASE WHEN total_score >= {config.threshold_warm} AND total_score < {config.threshold_hot} THEN 1 ELSE 0 END) as warm,
            SUM(CASE WHEN total_score < {config.threshold_warm} THEN 1 ELSE 0 END) as cold,
            COUNT(*) as total
        FROM leads
    """)
    
    row = c.fetchone()
    conn.close()
    
    return {
        "hot": row['hot'] or 0,
        "warm": row['warm'] or 0,
        "cold": row['cold'] or 0,
        "total": row['total'] or 0
    }


def touch_lead(lead_id: int):
    """
    Mark a lead as touched (resets decay timer).
    """
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""
        UPDATE leads 
        SET last_touched_at = ?
        WHERE id = ?
    """, (datetime.datetime.now(), lead_id))
    
    conn.commit()
    conn.close()
