#!/usr/bin/env python3
"""
Live Prediction Assistant for KnowledgePersistence-AI
Real-time predictive recommendations based on current activity
"""

import json
import psycopg
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LivePredictionAssistant:
    """Real-time predictive knowledge assistant"""
    
    def __init__(self):
        self.db_connection = "postgresql://postgres:SecureKnowledgePassword2025@localhost:5432/knowledge_persistence"
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict[str, Any]:
        """Load discovered patterns"""
        try:
            with open('/home/greg/KnowledgePersistence-AI/enhanced_pattern_analysis.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"patterns": []}
    
    def get_immediate_recommendations(self, current_activity: str = "") -> Dict[str, Any]:
        """Get immediate actionable recommendations"""
        conn = psycopg.connect(self.db_connection)
        
        # Get very recent activity (last 4 hours)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=4)
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT knowledge_type, category, title, importance_score, created_at
                FROM knowledge_items 
                WHERE created_at >= %s
                ORDER BY created_at DESC
                LIMIT 20
            """, (cutoff_time,))
            
            recent_items = [
                {
                    'knowledge_type': row[0],
                    'category': row[1], 
                    'title': row[2],
                    'importance_score': row[3],
                    'created_at': row[4]
                }
                for row in cur.fetchall()
            ]
        
        recommendations = []
        
        # Check for breakthrough opportunity (experiential → technical_discovery)
        recent_experiential = [item for item in recent_items if item['knowledge_type'] == 'experiential']
        if recent_experiential:
            latest_exp = recent_experiential[0]
            time_since = (datetime.now(timezone.utc) - latest_exp['created_at']).total_seconds() / 60  # minutes
            
            if time_since <= 10:  # Within 10 minutes = optimal breakthrough window
                recommendations.append({
                    'type': 'BREAKTHROUGH ALERT',
                    'urgency': 'IMMEDIATE',
                    'action': 'Create technical_discovery knowledge item NOW',
                    'reason': f'Experiential knowledge "{latest_exp["title"]}" created {time_since:.1f} minutes ago',
                    'expected_outcome': '+21.6 importance boost, breakthrough potential',
                    'confidence': '98%'
                })
        
        # Check for learning cycle optimization
        if recent_items:
            latest_type = recent_items[0]['knowledge_type']
            
            # High-efficiency transitions from pattern analysis
            high_efficiency_next = {
                'experiential': ('technical_discovery', 393.05, 'breakthrough'),
                'procedural': ('experiential', 236.53, 'knowledge building'), 
                'contextual': ('experiential', 127.35, 'experience synthesis')
            }
            
            if latest_type in high_efficiency_next:
                next_type, efficiency, purpose = high_efficiency_next[latest_type]
                recommendations.append({
                    'type': 'LEARNING OPTIMIZATION',
                    'urgency': 'HIGH',
                    'action': f'Create {next_type} knowledge for optimal learning',
                    'reason': f'Recent {latest_type} knowledge optimally leads to {next_type}',
                    'expected_outcome': f'Learning efficiency: {efficiency:.0f} ({purpose})',
                    'confidence': f'{efficiency/400*100:.0f}%'
                })
        
        # Check innovation conditions
        type_counts = {}
        for item in recent_items:
            type_counts[item['knowledge_type']] = type_counts.get(item['knowledge_type'], 0) + 1
        
        # Innovation pattern: multiple types + high experiential activity
        if type_counts.get('experiential', 0) >= 3 and len(type_counts) >= 2:
            recommendations.append({
                'type': 'INNOVATION OPPORTUNITY',
                'urgency': 'HIGH', 
                'action': 'Focus on breakthrough discovery - conditions optimal',
                'reason': f'High experiential activity ({type_counts["experiential"]} items) + diverse knowledge types',
                'expected_outcome': 'Major breakthrough potential detected',
                'confidence': '85%'
            })
        
        # Context-specific recommendations
        if current_activity:
            activity_lower = current_activity.lower()
            context_suggestions = []
            
            if 'pattern' in activity_lower or 'recognition' in activity_lower:
                context_suggestions.append({
                    'type': 'CONTEXT OPTIMIZATION',
                    'urgency': 'MEDIUM',
                    'action': 'Document pattern discovery methodology',
                    'reason': 'Pattern recognition work benefits from procedural documentation',
                    'expected_outcome': 'Improved pattern recognition reproducibility',
                    'confidence': '75%'
                })
            
            if 'mcp' in activity_lower or 'server' in activity_lower:
                context_suggestions.append({
                    'type': 'CONTEXT OPTIMIZATION',
                    'urgency': 'MEDIUM',
                    'action': 'Create technical_discovery for MCP integration insights',
                    'reason': 'MCP work often yields technical breakthroughs',
                    'expected_outcome': 'Capture architectural insights for future use',
                    'confidence': '80%'
                })
            
            recommendations.extend(context_suggestions)
        
        # Sort by urgency
        urgency_order = {'IMMEDIATE': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        recommendations.sort(key=lambda x: urgency_order.get(x['urgency'], 3))
        
        return {
            'timestamp': datetime.now().isoformat(),
            'current_activity': current_activity,
            'recent_knowledge_count': len(recent_items),
            'recent_types': list(type_counts.keys()),
            'total_recommendations': len(recommendations),
            'recommendations': recommendations[:5]  # Top 5
        }
    
    def monitor_breakthrough_window(self) -> Dict[str, Any]:
        """Monitor for optimal breakthrough timing"""
        conn = psycopg.connect(self.db_connection)
        
        # Look for experiential knowledge in last hour
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT title, created_at, importance_score
                FROM knowledge_items 
                WHERE knowledge_type = 'experiential' AND created_at >= %s
                ORDER BY created_at DESC
            """, (cutoff_time,))
            
            experiential_items = cur.fetchall()
        
        breakthrough_windows = []
        for item in experiential_items:
            minutes_since = (datetime.now(timezone.utc) - item[1]).total_seconds() / 60
            optimal_window = 3.3  # ~0.055 hours from pattern analysis
            
            if minutes_since <= optimal_window * 2:  # Within 2x optimal window
                urgency = 1.0 - (minutes_since / (optimal_window * 2))
                breakthrough_windows.append({
                    'trigger_title': item[0],
                    'minutes_since_creation': minutes_since,
                    'optimal_window_minutes': optimal_window,
                    'urgency_score': urgency,
                    'status': 'OPTIMAL' if minutes_since <= optimal_window else 'GOOD'
                })
        
        return {
            'breakthrough_opportunities': breakthrough_windows,
            'immediate_action_needed': any(w['status'] == 'OPTIMAL' for w in breakthrough_windows)
        }

def interactive_assistant():
    """Interactive prediction assistant"""
    assistant = LivePredictionAssistant()
    
    print("🤖 Live Prediction Assistant Active")
    print("=" * 50)
    
    while True:
        try:
            print("\nWhat are you working on? (or 'breakthrough' to check timing, 'quit' to exit)")
            user_input = input("> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'breakthrough':
                # Check breakthrough timing
                timing = assistant.monitor_breakthrough_window()
                if timing['immediate_action_needed']:
                    print("\n🚨 BREAKTHROUGH WINDOW DETECTED!")
                    for opp in timing['breakthrough_opportunities']:
                        if opp['status'] == 'OPTIMAL':
                            print(f"   📍 '{opp['trigger_title']}' created {opp['minutes_since_creation']:.1f} min ago")
                            print(f"   ⏰ CREATE TECHNICAL_DISCOVERY NOW for maximum impact!")
                else:
                    print("\n📊 No immediate breakthrough opportunities detected")
                    if timing['breakthrough_opportunities']:
                        print("   Recent experiential knowledge:")
                        for opp in timing['breakthrough_opportunities']:
                            print(f"   - '{opp['trigger_title']}' ({opp['minutes_since_creation']:.1f} min ago)")
            else:
                # Get recommendations for current activity
                recs = assistant.get_immediate_recommendations(user_input)
                
                print(f"\n📋 RECOMMENDATIONS ({recs['total_recommendations']} total):")
                print(f"Recent activity: {recs['recent_knowledge_count']} items, types: {', '.join(recs['recent_types'])}")
                
                for i, rec in enumerate(recs['recommendations'], 1):
                    print(f"\n{i}. {rec['type']} ({rec['urgency']} PRIORITY)")
                    print(f"   🎯 Action: {rec['action']}")
                    print(f"   💡 Reason: {rec['reason']}")
                    print(f"   📈 Expected: {rec['expected_outcome']}")
                    print(f"   🎲 Confidence: {rec['confidence']}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n👋 Live Prediction Assistant session ended")

if __name__ == "__main__":
    interactive_assistant()