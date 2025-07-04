#!/usr/bin/env python3
"""
import os
Test Enhanced Redirection Analysis on Multiple Sessions
Compare analysis quality between sessions
"""

import asyncio
from enhanced_redirection_analyzer import ComprehensiveRedirectionAnalyzer

# Database configuration
DB_CONFIG = {
    'host': '192.168.10.90',
    'port': 5432,
    'dbname': 'knowledge_persistence',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD', '')
}

async def test_multiple_sessions():
    """Test enhanced analysis on multiple sessions"""
    print("=== MULTI-SESSION REDIRECTION ANALYSIS TEST ===")
    
    analyzer = ComprehensiveRedirectionAnalyzer(DB_CONFIG)
    
    # Test sessions
    sessions = [
        "0daffdc5-b8f5-4243-bc7a-c6e0fdf4995a",
        "4ae1b8e2-c4d7-496c-99c3-764d80db0e60"
    ]
    
    session_results = []
    
    for i, session_id in enumerate(sessions, 1):
        print(f"\n=== SESSION {i} ANALYSIS: {session_id} ===")
        
        analysis = await analyzer.analyze_session_redirections(session_id)
        session_results.append(analysis)
        
        if analysis.get('error'):
            print(f"ERROR: {analysis['error']}")
            continue
            
        print(f"Total redirections: {analysis['total_redirections']}")
        print(f"Redirection rate: {analysis['redirection_rate']:.1%}")
        print(f"Overall quality: {analysis['overall_assessment'].get('session_quality', 'unknown')}")
        
        if analysis['redirection_analyses']:
            for redir in analysis['redirection_analyses']:
                semantic = redir['semantic_analysis']
                print(f"\n  Redirection {redir['index']}:")
                print(f"    Content: {redir['content'][:80]}...")
                print(f"    Category: {semantic['primary_category']['primary']}")
                print(f"    Confidence: {semantic['primary_category']['confidence']:.2f}")
                print(f"    Severity: {semantic['severity_assessment']['severity_level']} ({semantic['severity_assessment']['severity_score']:.2f})")
                print(f"    Emotional tone: {semantic['emotional_tone']['dominant_tone']}")
                print(f"    Root causes: {semantic['root_cause_signals']}")
                print(f"    Resolution quality: {redir['resolution_effectiveness']['resolution_quality']}")
        
        print(f"\n  Actionable Insights:")
        for insight in analysis['actionable_insights']:
            print(f"    - [{insight['priority']}] {insight['insight']}")
    
    # Cross-session comparison
    print(f"\n=== CROSS-SESSION COMPARISON ===")
    
    if len(session_results) >= 2:
        valid_sessions = [s for s in session_results if not s.get('error')]
        
        if len(valid_sessions) >= 2:
            # Compare redirection rates
            rates = [s['redirection_rate'] for s in valid_sessions]
            avg_rate = sum(rates) / len(rates)
            print(f"Average redirection rate: {avg_rate:.1%}")
            
            # Compare categories
            all_categories = []
            for session in valid_sessions:
                for redir in session.get('redirection_analyses', []):
                    all_categories.append(redir['semantic_analysis']['primary_category']['primary'])
            
            if all_categories:
                category_counts = {cat: all_categories.count(cat) for cat in set(all_categories)}
                print(f"Most common category: {max(category_counts.items(), key=lambda x: x[1])}")
            
            # Compare severities
            all_severities = []
            for session in valid_sessions:
                for redir in session.get('redirection_analyses', []):
                    all_severities.append(redir['semantic_analysis']['severity_assessment']['severity_score'])
            
            if all_severities:
                avg_severity = sum(all_severities) / len(all_severities)
                print(f"Average severity score: {avg_severity:.2f}")
        
        print(f"\n=== METHODOLOGY COMPARISON ===")
        print("BEFORE (Simple counting):")
        print("  - Session 1: 1 redirection (33.3% rate)")
        print("  - Session 2: 1 redirection (33.3% rate)")
        print("  - Analysis: Both sessions have redirections, implement validation")
        
        print("\nAFTER (Enhanced semantic analysis):")
        for i, session in enumerate(valid_sessions, 1):
            if session['redirection_analyses']:
                redir = session['redirection_analyses'][0]
                semantic = redir['semantic_analysis']
                print(f"  - Session {i}: {semantic['primary_category']['primary']} "
                      f"({semantic['severity_assessment']['severity_level']}, "
                      f"confidence: {semantic['primary_category']['confidence']:.2f})")
                print(f"    Root cause: {semantic['root_cause_signals']}")
                print(f"    Resolution: {redir['resolution_effectiveness']['resolution_quality']}")

if __name__ == "__main__":
    asyncio.run(test_multiple_sessions())