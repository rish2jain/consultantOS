#!/usr/bin/env python3
"""
Fast UX analysis - Technical metrics only (no CLI/API calls)
Analyzes all screenshots quickly using only technical metrics
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
import re
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.ux_image_analyzer import UXImageAnalyzer


def extract_view_info(filename: str) -> dict:
    """Extract view information from filename"""
    # Pattern: scenarioX-Y-viewname-timestamp.png
    match = re.search(r'scenario(\d+)-(\d+)-(.+?)-20\d{2}', filename)
    if match:
        return {
            'scenario': match.group(1),
            'step': match.group(2),
            'view': match.group(3),
            'type': match.group(3)
        }
    
    # Fallback patterns
    match = re.search(r'scenario(\d+)', filename)
    if match:
        return {
            'scenario': match.group(1),
            'step': 'unknown',
            'view': 'unknown',
            'type': f"scenario_{match.group(1)}"
        }
    
    return {'scenario': 'unknown', 'step': 'unknown', 'view': 'unknown', 'type': 'unknown'}


def main():
    screenshots_dir = "tests/e2e/screenshots"
    output_file = "tests/e2e/ux-analysis-fast.json"
    
    print("🔍 Fast UX Analysis - Technical Metrics Only")
    print("=" * 60)
    
    # Find all screenshots
    screenshots_path = Path(screenshots_dir)
    image_files = list(screenshots_path.glob("*.png")) + list(screenshots_path.glob("*.jpg"))
    
    if not image_files:
        print(f"❌ No screenshots found in {screenshots_dir}")
        return
    
    print(f"\n📸 Found {len(image_files)} screenshots")
    
    # Group by view type
    by_type = defaultdict(list)
    for img_file in image_files:
        info = extract_view_info(img_file.name)
        by_type[info['type']].append((img_file, info))
    
    print(f"📊 Found {len(by_type)} unique view types")
    
    # Initialize analyzer (no CLI, no API - fast mode)
    print("\n🔧 Initializing analyzer (fast mode - technical metrics only)...")
    analyzer = UXImageAnalyzer(use_cli=False)  # Skip CLI/API for speed
    
    # Analyze screenshots
    print(f"\n📊 Analyzing {len(image_files)} screenshots...")
    print("=" * 60)
    
    results = []
    errors = []
    
    for i, img_path in enumerate(image_files, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(image_files)} ({i*100//len(image_files)}%)")
        
        try:
            result = analyzer.analyze_image(str(img_path))
            view_info = extract_view_info(img_path.name)
            result_dict = analyzer._result_to_dict(result)
            result_dict['view_info'] = view_info
            results.append(result_dict)
        except Exception as e:
            errors.append({'file': str(img_path), 'error': str(e)})
            continue
    
    if not results:
        print("\n❌ No results to save")
        if errors:
            print(f"Errors: {len(errors)}")
        return
    
    # Calculate statistics
    scores = [r['overall_score'] for r in results]
    avg_score = sum(scores) / len(scores)
    min_score = min(scores)
    max_score = max(scores)
    
    # Group by view type
    by_view_type = defaultdict(list)
    for r in results:
        view_type = r.get('view_info', {}).get('type', 'unknown')
        by_view_type[view_type].append(r)
    
    # Calculate per-type averages
    type_stats = {}
    for view_type, type_results in by_view_type.items():
        type_scores = [r['overall_score'] for r in type_results]
        type_stats[view_type] = {
            'count': len(type_results),
            'avg_score': sum(type_scores) / len(type_scores),
            'min_score': min(type_scores),
            'max_score': max(type_scores)
        }
    
    # Find common issues
    all_weaknesses = []
    all_recommendations = []
    for r in results:
        all_weaknesses.extend(r.get('weaknesses', []))
        all_recommendations.extend(r.get('recommendations', []))
    
    from collections import Counter
    top_issues = Counter(all_weaknesses).most_common(10)
    top_recommendations = Counter(all_recommendations).most_common(10)
    
    # Save results
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'analysis_mode': 'fast_technical_only',
        'total_screenshots_analyzed': len(results),
        'total_screenshots_found': len(image_files),
        'errors': len(errors),
        'summary': {
            'average_score': avg_score,
            'min_score': min_score,
            'max_score': max_score,
            'total_views': len(by_view_type)
        },
        'by_view_type': type_stats,
        'top_issues': [{'issue': issue, 'count': count} for issue, count in top_issues],
        'top_recommendations': [{'recommendation': rec, 'count': count} for rec, count in top_recommendations],
        'results': results[:50]  # Save first 50 detailed results to keep file size manageable
    }
    
    if errors:
        output_data['error_details'] = errors[:20]  # First 20 errors
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Analysis Summary")
    print("=" * 60)
    print(f"Total Screenshots Analyzed: {len(results)}")
    print(f"Errors: {len(errors)}")
    print(f"\n📈 Overall Statistics:")
    print(f"  Average Score: {avg_score:.1f}/100")
    print(f"  Score Range: {min_score:.1f} - {max_score:.1f}")
    print(f"  Unique View Types: {len(by_view_type)}")
    
    print(f"\n📋 Top View Types by Count:")
    sorted_types = sorted(type_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    for view_type, stats in sorted_types[:10]:
        print(f"  • {view_type}: {stats['count']} views, avg {stats['avg_score']:.1f}/100")
    
    if top_issues:
        print(f"\n🔴 Top Issues (across all views):")
        for issue, count in top_issues[:5]:
            print(f"  • {issue} ({count} views)")
    
    if top_recommendations:
        print(f"\n💡 Top Recommendations:")
        for rec, count in top_recommendations[:5]:
            print(f"  • {rec} ({count} views)")
    
    print(f"\n💾 Full results saved to: {output_file}")
    print(f"\n💡 Tip: Run with --backend gemini/claude/codex for semantic analysis on specific views")


if __name__ == '__main__':
    main()

