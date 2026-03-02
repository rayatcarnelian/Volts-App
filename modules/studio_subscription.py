"""
STUDIO SUBSCRIPTION MANAGER (THE BANK)
Handles user credits, tiers, and usage tracking for the SaaS model.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any

# ============================================================================
# TIER DEFINITIONS
# ============================================================================

TIERS = {
    "FREE": {
        "name": "Starter",
        "price": 0,
        "limits": {
            "images_per_day": 5,
            "videos_per_month": 0,
            "max_resolution": 1024,
            "commercial_license": False
        }
    },
    "PRO": {
        "name": "Creator Pro",
        "price": 29,
        "limits": {
            "images_per_month": 500,
            "videos_per_month": 20,
            "max_resolution": 2048,
            "commercial_license": True
        }
    },
    "AGENCY": {
        "name": "Agency Elite",
        "price": 99,
        "limits": {
            "images_per_month": 9999, # Effectively unlimited
            "videos_per_month": 100,
            "max_resolution": 4096,
            "commercial_license": True
        }
    }
}

class SubscriptionManager:
    """
    Manages user subscriptions and credit usage.
    For MVP, uses a simple JSON file 'user_credits.json'.
    In production, this would be a SQL database.
    """
    
    DB_FILE = "user_credits.json"
    
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self._load_db()
        
    def _load_db(self):
        """Load or create the credit database."""
        if os.path.exists(self.DB_FILE):
            try:
                with open(self.DB_FILE, 'r') as f:
                    self.db = json.load(f)
            except:
                self.db = {}
        else:
            self.db = {}
            
        # Initialize user if not exists
        if self.user_id not in self.db:
            self._reset_user(self.user_id)
            
    def _save_db(self):
        """Save the credit database."""
        with open(self.DB_FILE, 'w') as f:
            json.dump(self.db, f, indent=4)
            
    def _reset_user(self, user_id: str, tier: str = "FREE"):
        """Initialize a new user or reset their cycle."""
        self.db[user_id] = {
            "tier": tier,
            "cycle_start": time.time(),
            "usage": {
                "images": 0,
                "videos": 0,
                "images_today": 0,
                "last_active": time.time()
            }
        }
        self._save_db()

    def _check_cycle(self):
        """Reset counters if new billing cycle (30 days) or new day."""
        user = self.db[self.user_id]
        now = time.time()
        
        # Daily Reset (for Free Tier)
        last_active = datetime.fromtimestamp(user["usage"]["last_active"])
        current_time = datetime.fromtimestamp(now)
        
        if last_active.day != current_time.day:
            user["usage"]["images_today"] = 0
            
        # Monthly Reset
        cycle_start = user["cycle_start"]
        days_passed = (now - cycle_start) / (24 * 3600)
        
        if days_passed >= 30:
            user["cycle_start"] = now
            user["usage"]["images"] = 0
            user["usage"]["videos"] = 0
            
        user["usage"]["last_active"] = now
        self._save_db()

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get current user status and limits."""
        self._check_cycle()
        user = self.db[self.user_id]
        tier_name = user["tier"]
        tier_limits = TIERS[tier_name]["limits"]
        
        return {
            "tier": tier_name,
            "limits": tier_limits,
            "usage": user["usage"]
        }

    def can_generate_image(self) -> bool:
        """Check if user has image credits."""
        self._check_cycle()
        user = self.db[self.user_id]
        tier = user["tier"]
        limits = TIERS[tier]["limits"]
        
        if tier == "FREE":
            # Free tier limited by daily usage
            if user["usage"]["images_today"] >= limits["images_per_day"]:
                return False
        else:
            # Paid tiers limited by monthly usage
            if user["usage"]["images"] >= limits["images_per_month"]:
                return False
                
        return True

    def can_generate_video(self) -> bool:
        """Check if user has video credits."""
        self._check_cycle()
        user = self.db[self.user_id]
        tier = user["tier"]
        limits = TIERS[tier]["limits"]
        
        # Hard check: Free tier has 0 videos
        if limits["videos_per_month"] == 0:
            return False
            
        if user["usage"]["videos"] >= limits["videos_per_month"]:
            return False
            
        return True

    def deduct_image(self):
        """Deduct 1 image credit."""
        self._check_cycle()
        user = self.db[self.user_id]
        user["usage"]["images"] += 1
        user["usage"]["images_today"] += 1
        self._save_db()

    def deduct_video(self):
        """Deduct 1 video credit."""
        self._check_cycle()
        user = self.db[self.user_id]
        user["usage"]["videos"] += 1
        self._save_db()

    def upgrade_tier(self, new_tier: str):
        """Upgrade user to a new tier."""
        if new_tier in TIERS:
            self.db[self.user_id]["tier"] = new_tier
            # Reset cycle on upgrade to give full fresh credits
            self.db[self.user_id]["cycle_start"] = time.time()
            self.db[self.user_id]["usage"]["images"] = 0
            self.db[self.user_id]["usage"]["videos"] = 0
            self._save_db()
