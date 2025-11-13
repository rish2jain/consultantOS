#!/usr/bin/env python3
"""
Analyze one representative screenshot per view type
Processes views one at a time with full semantic analysis
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


def extract_view_type(filename: str) -> str:
    """Extract view type from filename"""
    # Pattern: scenarioX-Y-viewname-timestamp.png
    match = re.search(r'scenario\d+-\d+-(.+?)-20\d{2}', filename)
    if match:
        return match.group(1)
    
    # Fallback: use scenario number
    match = re.search(r'scenario(\d+)', filename)
    if match:
        return f"scenario_{match.group(1)}"
    
    return "unknown"


def find_one_per_view(screenshots_dir: str) -> list:
    """Find one representative screenshot per view type (most recent)"""
    screenshots_dir = Path(screenshots_dir)
    image_files = list(screenshots_dir.glob("*.png")) + list(screenshots_dir.glob("*.jpg"))
    
    if not image_files:
        return []
    
    # Group by view type
    by_type = defaultdict(list)
    for img_file in image_files:
        view_type = extract_view_type(img_file.name)
        by_type[view_type].append(img_file)
    
    # Take most recent from each type
    representative = []
    for view_type, files in sorted(by_type.items()):
        # Sort by filename (which includes timestamp) and take most recent
        files_sorted = sorted(files, key=lambda x: x.name, reverse=True)
        representative.append((view_type, files_sorted[0], len(files)))
    
    return representative


def main():
    screenshots_dir = "tests/e2e/screenshots"
    output_file = "tests/e2e/ux-analysis-one-per-view.json"
    
    print("🔍 UX Analysis - One Screenshot Per View Type")
    print("=" * 60)
    
    # Find one per view
    print(f"\n📸 Finding representative screenshots from {screenshots_dir}...")
    representative = find_one_per_view(screenshots_dir)
    
    if not representative:
        print(f"❌ No screenshots found in {screenshots_dir}")
        return
    
    print(f"\n✅ Selected {len(representative)} unique views")
    print("\nViews to analyze:")
    for view_type, img_file, total_count in representative:
        print(f"  • {view_type}: {img_file.name} (from {total_count} total)")
    
    # Initialize analyzer with CLI support - try Gemini first (most reliable)
    print("\n🔧 Initializing analyzer with CLI support...")
    # Try Gemini first, then fall back to others
    analyzer = UXImageAnalyzer(cli_backend="auto")
    
    # Analyze each view one at a time
    print(f"\n📊 Analyzing {len(representative)} views (one at a time)...")
    print("=" * 60)
    
    results = []
    for i, (view_type, img_path, total_count) in enumerate(representative, 1):
        print(f"\n[{i}/{len(representative)}] Analyzing: {view_type}")
        print(f"  File: {img_path.name}")
        print(f"  (Selected from {total_count} screenshots of this view)")
        print("-" * 60)
        
        try:
            result = analyzer.analyze_image(str(img_path))
            
            # Add view metadata
            result_dict = analyzer._result_to_dict(result)
            result_dict['view_type'] = view_type
            result_dict['total_screenshots_of_this_view'] = total_count
            results.append(result_dict)
            
            print(f"  ✅ Score: {result.overall_score:.1f}/100")
            if result.strengths:
                print(f"  ✓ Strengths:")
                for s in result.strengths[:3]:
                    print(f"    • {s}")
            if result.weaknesses:
                print(f"  ✗ Weaknesses:")
                for w in result.weaknesses[:3]:
                    print(f"    • {w}")
            if result.recommendations:
                print(f"  💡 Top Recommendations:")
                for r in result.recommendations[:2]:
                    print(f"    • {r}")
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")
            # Build error result dict matching successful schema
            error_result_dict = {
                'image_path': str(img_path),
                'timestamp': None,
                'overall_score': None,
                'strengths': [],
                'weaknesses': [],
                'recommendations': [],
                'error': str(e),
                'view_type': view_type,
                'total_screenshots_of_this_view': total_count,
                'metrics': {
                    'image_size': None,
                    'aspect_ratio': None,
                    'brightness': None,
                    'contrast': None,
                    'whitespace_ratio': None,
                    'visual_hierarchy_score': None,
                    'color_contrast_score': None,
                    'text_readability_score': None,
                    'ui_components_detected': None,
                    'accessibility_issues': None,
                    'design_recommendations': None
                }
            }
            results.append(error_result_dict)
            continue
    
    if not results:
        print("\n❌ No results to save")
        return
    
    # Calculate statistics
    successful_results = [r for r in results if 'overall_score' in r]
    if successful_results:
        scores = [r['overall_score'] for r in successful_results]
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        
        # Group by view type for stats
        by_type_stats = defaultdict(list)
        for r in successful_results:
            view_type = r.get('view_type', 'unknown')
            by_type_stats[view_type].append(r['overall_score'])
        
        # Find common issues
        all_weaknesses = []
        all_recommendations = []
        for r in successful_results:
            weaknesses = r.get('weaknesses', [])
            recommendations = r.get('recommendations', [])
            # Ensure they're strings, not dicts
            all_weaknesses.extend([w if isinstance(w, str) else str(w) for w in weaknesses])
            all_recommendations.extend([rec if isinstance(rec, str) else str(rec) for rec in recommendations])
        
        from collections import Counter
        top_issues = Counter(all_weaknesses).most_common(10)
        top_recommendations = Counter(all_recommendations).most_common(10)
    
    # Save results
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'analysis_mode': 'one_per_view_with_semantic',
        'total_views_analyzed': len(representative),
        'successful_analyses': len(successful_results),
        'failed_analyses': len(results) - len(successful_results),
        'results': results
    }
    
    if successful_results:
        output_data['summary'] = {
            'average_score': avg_score,
            'min_score': min_score,
            'max_score': max_score,
            'total_unique_views': len(by_type_stats)
        }
        output_data['top_issues'] = [{'issue': issue, 'count': count} for issue, count in top_issues]
        output_data['top_recommendations'] = [{'recommendation': rec, 'count': count} for rec, count in top_recommendations]
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 Final Summary")
    print("=" * 60)
    print(f"Total Views Analyzed: {len(representative)}")
    print(f"Successful: {len(successful_results)}")
    print(f"Failed: {len(results) - len(successful_results)}")
    
    if successful_results:
        print(f"\n📈 Score Statistics:")
        print(f"  Average Score: {avg_score:.1f}/100")
        print(f"  Score Range: {min_score:.1f} - {max_score:.1f}")
        
        if top_issues:
            print(f"\n🔴 Top Issues Across All Views:")
            for issue, count in top_issues[:5]:
                print(f"  • {issue} ({count} views)")
        
        if top_recommendations:
            print(f"\n💡 Top Recommendations:")
            for rec, count in top_recommendations[:5]:
                print(f"  • {rec} ({count} views)")
    
    print(f"\n💾 Full results saved to: {output_file}")


if __name__ == '__main__':
    main()

