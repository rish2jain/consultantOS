#!/usr/bin/env python3
"""
Analyze representative views from E2E test screenshots
This script samples different view types rather than analyzing all 160+ screenshots
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
import re
from datetime import datetime

# Add parent directory to path to import ux_image_analyzer
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


def find_representative_screenshots(screenshots_dir: str, max_per_type: int = 3) -> list:
    """Find representative screenshots, sampling different view types"""
    screenshots_dir = Path(screenshots_dir)
    image_files = list(screenshots_dir.glob("*.png")) + list(screenshots_dir.glob("*.jpg"))
    
    if not image_files:
        return []
    
    # Group by view type
    by_type = defaultdict(list)
    for img_file in image_files:
        view_type = extract_view_type(img_file.name)
        by_type[view_type].append(img_file)
    
    # Sample from each type
    representative = []
    for view_type, files in by_type.items():
        # Sort by filename (which includes timestamp) and take most recent
        files_sorted = sorted(files, key=lambda x: x.name, reverse=True)
        sample = files_sorted[:max_per_type]
        representative.extend(sample)
        print(f"  {view_type}: {len(files)} total, sampling {len(sample)}")
    
    return representative


def main():
    screenshots_dir = "tests/e2e/screenshots"
    output_file = "tests/e2e/ux-analysis-representative.json"
    
    print("🔍 UX Image Analyzer - Representative Views Analysis")
    print("=" * 60)
    
    # Find representative screenshots
    print(f"\n📸 Finding representative screenshots from {screenshots_dir}...")
    representative = find_representative_screenshots(screenshots_dir, max_per_type=2)
    
    if not representative:
        print(f"❌ No screenshots found in {screenshots_dir}")
        return
    
    print(f"\n✅ Selected {len(representative)} representative screenshots from {len(list(Path(screenshots_dir).glob('*.png')))} total")
    print("\nSelected views:")
    for img in representative[:10]:  # Show first 10
        print(f"  • {img.name}")
    if len(representative) > 10:
        print(f"  ... and {len(representative) - 10} more")
    
    # Initialize analyzer
    print("\n🔧 Initializing analyzer...")
    analyzer = UXImageAnalyzer(use_cli=True, cli_backend="auto")
    
    # Analyze each screenshot
    print(f"\n📊 Analyzing {len(representative)} screenshots...")
    print("=" * 60)
    
    results = []
    for i, img_path in enumerate(representative, 1):
        print(f"\n[{i}/{len(representative)}] Analyzing {img_path.name}...")
        try:
            result = analyzer.analyze_image(str(img_path))
            results.append(result)
            print(f"  ✅ Score: {result.overall_score:.1f}/100")
            if result.strengths:
                print(f"  ✓ Strengths: {', '.join(result.strengths[:2])}")
            if result.weaknesses:
                print(f"  ✗ Issues: {', '.join(result.weaknesses[:2])}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
    
    if not results:
        print("\n❌ No results to save")
        return
    
    # Save results
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'total_screenshots_analyzed': len(results),
        'total_screenshots_available': len(list(Path(screenshots_dir).glob("*.png"))),
        'sampling_strategy': 'Representative views (2 per view type)',
        'results': [analyzer._result_to_dict(r) for r in results]
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print("📊 Analysis Summary")
    print("=" * 60)
    analyzer.print_summary(results)
    
    print(f"\n💾 Full results saved to: {output_file}")
    print(f"\n📈 Quick Stats:")
    avg_score = sum(r.overall_score for r in results) / len(results)
    min_score = min(r.overall_score for r in results)
    max_score = max(r.overall_score for r in results)
    print(f"  Average Score: {avg_score:.1f}/100")
    print(f"  Score Range: {min_score:.1f} - {max_score:.1f}")
    
    # Count common issues
    all_weaknesses = []
    for r in results:
        all_weaknesses.extend(r.weaknesses)
    
    from collections import Counter
    top_issues = Counter(all_weaknesses).most_common(5)
    if top_issues:
        print(f"\n🔴 Top Issues:")
        for issue, count in top_issues:
            print(f"  • {issue} ({count} views)")


if __name__ == '__main__':
    main()

