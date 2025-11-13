"""
UX Image Analyzer for Cursor Testing Toolkit

Analyzes UI screenshots for UX design quality, accessibility, and best practices.
Uses CLI tools (Codex, Claude, Gemini) for semantic analysis and OpenCV/Pillow for technical metrics.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json
from datetime import datetime

try:
    from PIL import Image, ImageStat
    import numpy as np
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️  Pillow not installed. Install with: pip install Pillow")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️  OpenCV not installed. Install with: pip install opencv-python")

# CLI tool availability (checked at runtime)
import subprocess
import shutil


@dataclass
class UXMetrics:
    """UX metrics extracted from image analysis"""
    # Technical metrics
    image_size: Tuple[int, int]
    aspect_ratio: float
    color_count: int
    brightness: float  # 0-255
    contrast: float  # Standard deviation of pixel values
    dominant_colors: List[Tuple[int, int, int]]  # RGB tuples
    
    # Layout metrics
    text_density: float  # Estimated text area / total area
    whitespace_ratio: float  # White/light pixels / total pixels
    visual_hierarchy_score: float  # 0-1, based on size variation
    
    # Accessibility metrics
    color_contrast_score: float  # 0-1, higher is better
    text_readability_score: float  # 0-1, estimated
    
    # Semantic analysis (from Gemini)
    semantic_analysis: Optional[Dict] = None
    ui_components_detected: Optional[List[str]] = None
    accessibility_issues: Optional[List[str]] = None
    design_recommendations: Optional[List[str]] = None


@dataclass
class AnalysisResult:
    """Complete analysis result for a screenshot"""
    image_path: str
    timestamp: str
    metrics: UXMetrics
    overall_score: float  # 0-100
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


class UXImageAnalyzer:
    """Analyzes UI screenshots for UX design quality"""
    
    def __init__(
        self,
        cli_backend: str = "auto"  # "auto", "gemini", "claude", "codex"
    ):
        """
        Initialize the analyzer

        Args:
            cli_backend: Which CLI to use: "auto" (detect), "gemini", "claude", "codex"
        """
        self.cli_backend = cli_backend

        # Detect available CLI tools
        self.codex_available = self._check_command("codex")
        self.gemini_available = self._check_command("gemini")
        self.claude_available = self._check_command("claude")

        # Print detected backends
        available = []
        if self.codex_available:
            available.append("codex")
        if self.claude_available:
            available.append("claude")
        if self.gemini_available:
            available.append("gemini")

        if available:
            print(f"ℹ️  CLI backends available: {', '.join(available)}")
        else:
            print("⚠️  No CLI backends found. Install one of: codex, claude, gemini")
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available in PATH"""
        return shutil.which(command) is not None
    
    def analyze_image(self, image_path: str) -> AnalysisResult:
        """
        Analyze a single screenshot for UX metrics
        
        Args:
            image_path: Path to the screenshot image
            
        Returns:
            AnalysisResult with comprehensive UX metrics
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load image
        if not PILLOW_AVAILABLE:
            raise ImportError("Pillow is required. Install with: pip install Pillow")
        
        img = Image.open(image_path)
        
        # Calculate technical metrics
        metrics = self._calculate_technical_metrics(img)
        
        # Calculate layout metrics
        layout_metrics = self._calculate_layout_metrics(img)
        metrics.update(layout_metrics)
        
        # Calculate accessibility metrics
        accessibility_metrics = self._calculate_accessibility_metrics(img)
        metrics.update(accessibility_metrics)
        
        # Semantic analysis with CLI or API (if available)
        try:
            semantic = self._semantic_analysis(img, image_path)
            if semantic:
                metrics.update(semantic)
        except Exception as e:
            print(f"⚠️  Semantic analysis failed: {e}")
        
        # Create metrics object
        ux_metrics = UXMetrics(**metrics)
        
        # Calculate overall score and generate recommendations
        score, strengths, weaknesses, recommendations = self._evaluate_ux(ux_metrics)
        
        return AnalysisResult(
            image_path=image_path,
            timestamp=datetime.now().isoformat(),
            metrics=ux_metrics,
            overall_score=score,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )
    
    def _calculate_technical_metrics(self, img: Image.Image) -> Dict:
        """Calculate basic technical image metrics"""
        width, height = img.size
        aspect_ratio = width / height if height > 0 else 0
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get pixel data
        pixels = np.array(img)
        
        # Calculate brightness (mean of all channels)
        brightness = float(np.mean(pixels))
        
        # Calculate contrast (standard deviation)
        contrast = float(np.std(pixels))
        
        # Count unique colors (sample for performance)
        sample_size = min(10000, width * height)
        sample_indices = np.random.choice(width * height, sample_size, replace=False)
        sample_pixels = pixels.reshape(-1, 3)[sample_indices]
        unique_colors = len(np.unique(sample_pixels, axis=0))
        
        # Get dominant colors using k-means (simplified)
        dominant_colors = self._get_dominant_colors(pixels, k=5)
        
        return {
            'image_size': (width, height),
            'aspect_ratio': aspect_ratio,
            'color_count': unique_colors,
            'brightness': brightness,
            'contrast': contrast,
            'dominant_colors': dominant_colors
        }
    
    def _get_dominant_colors(self, pixels: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant colors using simple clustering"""
        # Reshape to 2D array
        pixels_2d = pixels.reshape(-1, 3)
        
        # Sample for performance
        sample_size = min(5000, len(pixels_2d))
        sample = pixels_2d[np.random.choice(len(pixels_2d), sample_size, replace=False)]
        
        # Simple k-means approximation
        if OPENCV_AVAILABLE:
            try:
                sample_float = sample.astype(np.float32)
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
                _, labels, centers = cv2.kmeans(
                    sample_float, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
                )
                colors = [(int(c[0]), int(c[1]), int(c[2])) for c in centers]
                return colors
            except:
                pass
        
        # Fallback: simple histogram-based approach
        # Group similar colors
        colors = []
        for _ in range(k):
            if len(sample) == 0:
                break
            # Find most common color in remaining sample
            unique, counts = np.unique(sample, axis=0, return_counts=True)
            most_common_idx = np.argmax(counts)
            color = tuple(int(c) for c in unique[most_common_idx])
            colors.append(color)
            # Remove similar colors
            distances = np.sum((sample - unique[most_common_idx]) ** 2, axis=1)
            sample = sample[distances > 10000]  # Threshold for similarity
        
        return colors[:k]
    
    def _calculate_layout_metrics(self, img: Image.Image) -> Dict:
        """Calculate layout and visual hierarchy metrics"""
        width, height = img.size
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = np.array(img)
        
        # Estimate whitespace (very light pixels)
        light_threshold = 240
        light_pixels = np.sum(np.all(pixels >= light_threshold, axis=2))
        total_pixels = width * height
        whitespace_ratio = light_pixels / total_pixels if total_pixels > 0 else 0
        
        # Estimate text density (dark pixels in small regions)
        # This is a heuristic - actual text detection would require OCR
        dark_threshold = 50
        dark_pixels = np.sum(np.all(pixels <= dark_threshold, axis=2))
        text_density = dark_pixels / total_pixels if total_pixels > 0 else 0
        
        # Visual hierarchy (variance in brightness across regions)
        # Divide into grid and calculate variance
        grid_size = 10
        region_size_w = width // grid_size
        region_size_h = height // grid_size
        region_brightness = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                x1 = i * region_size_w
                y1 = j * region_size_h
                x2 = min((i + 1) * region_size_w, width)
                y2 = min((j + 1) * region_size_h, height)
                region = pixels[y1:y2, x1:x2]
                if len(region) > 0:
                    region_brightness.append(np.mean(region))
        
        visual_hierarchy_score = float(np.std(region_brightness)) / 255.0 if region_brightness else 0.0
        
        return {
            'text_density': text_density,
            'whitespace_ratio': whitespace_ratio,
            'visual_hierarchy_score': min(visual_hierarchy_score, 1.0)
        }
    
    def _calculate_accessibility_metrics(self, img: Image.Image) -> Dict:
        """Calculate accessibility-related metrics"""
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = np.array(img)
        
        # Estimate color contrast
        # This is simplified - real contrast checking requires text/background pairs
        brightness_values = np.mean(pixels, axis=2)
        brightness_std = np.std(brightness_values)
        
        # Higher std = better contrast (more variation)
        # Normalize to 0-1
        color_contrast_score = min(brightness_std / 128.0, 1.0)
        
        # Text readability (heuristic based on contrast and brightness)
        # Ideal: high contrast, medium brightness
        ideal_brightness = 128
        brightness = np.mean(brightness_values)
        brightness_score = 1.0 - abs(brightness - ideal_brightness) / 128.0
        text_readability_score = (color_contrast_score * 0.7 + brightness_score * 0.3)
        
        return {
            'color_contrast_score': color_contrast_score,
            'text_readability_score': text_readability_score
        }
    
    def _semantic_analysis(self, img: Image.Image, image_path: str) -> Dict:
        """Use CLI tools or API for semantic UI analysis"""
        prompt = """Analyze this UI screenshot and provide:
1. List of UI components detected (buttons, forms, navigation, etc.)
2. Accessibility issues (contrast, text size, missing labels, etc.)
3. Design recommendations for better UX

Format your response as JSON with these keys:
- "ui_components": array of component names
- "accessibility_issues": array of issues found
- "design_recommendations": array of recommendations

Be specific and actionable."""
        
        # Use CLI tools only (no API fallback)
        backend = self._select_backend()
        
        if not backend:
            return {}
        
        if backend == "gemini":
            return self._semantic_analysis_gemini_cli(image_path, prompt)
        elif backend == "claude":
            return self._semantic_analysis_claude_cli(image_path, prompt)
        elif backend == "codex":
            return self._semantic_analysis_codex(image_path, prompt)
        else:
            return {}
    
    def _select_backend(self) -> str:
        """Select the best available backend"""
        if self.cli_backend != "auto":
            # Use explicitly specified backend if available
            if self.cli_backend == "codex" and self.codex_available:
                return "codex"
            elif self.cli_backend == "claude" and self.claude_available:
                return "claude"
            elif self.cli_backend == "gemini" and self.gemini_available:
                return "gemini"
            else:
                print(f"⚠️  Requested backend '{self.cli_backend}' not available")
                return ""

        # Auto-detect: prefer gemini (recommended), then codex, then claude
        if self.gemini_available:
            return "gemini"
        elif self.codex_available:
            return "codex"
        elif self.claude_available:
            return "claude"
        else:
            print("⚠️  No CLI backends available for semantic analysis")
            return ""
    
    def _semantic_analysis_gemini_cli(self, image_path: str, prompt: str) -> Dict:
        """Use Gemini CLI for semantic analysis"""
        try:
            # Gemini CLI - pass image path for Gemini to load and analyze
            full_prompt = f"Analyze this UI screenshot image file: {image_path}\n\n{prompt}"

            # Use positional prompt (non-interactive)
            result = subprocess.run(
                ["gemini", full_prompt],
                capture_output=True,
                timeout=30,
                text=True
            )

            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            # Check for quota errors
            if "exhausted your capacity" in (stderr + stdout):
                print("⚠️  Gemini API quota exhausted - quota resets later")
                return {}

            # Filter out MCP configuration errors from output
            if stdout:
                lines = []
                for line in stdout.split('\n'):
                    # Skip error lines
                    if any(skip in line for skip in ['[ERROR]', 'Error when talking', 'An unexpected', 'Loaded cached']):
                        continue
                    lines.append(line)
                stdout = '\n'.join(lines).strip()

            if result.returncode != 0:
                if stderr:
                    print(f"⚠️  Gemini CLI error: {stderr[:200]}")
                return {}

            if not stdout:
                print("⚠️  Gemini returned empty response")
                return {}

            return self._parse_semantic_response(stdout)

        except FileNotFoundError:
            print("⚠️  Gemini CLI not found. Install with: pip install google-generativeai-cli")
            return {}
        except subprocess.TimeoutExpired:
            print("⚠️  Gemini CLI request timed out")
            return {}
        except Exception as e:
            print(f"⚠️  Gemini CLI analysis error: {e}")
            return {}
    
    def _semantic_analysis_claude_cli(self, image_path: str, prompt: str) -> Dict:
        """Use Claude CLI for semantic analysis (should be authenticated)"""
        try:
            # Claude is running this, so CLI should already be authenticated
            # Pass image path in prompt - Claude will load and analyze the image
            full_prompt = f"Analyze this UI screenshot image file: {image_path}\n\n{prompt}"

            result = subprocess.run(
                ["claude", full_prompt, "--print"],
                capture_output=True,
                timeout=30,
                text=True
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                if "API key" in error_msg or "authentication" in error_msg.lower():
                    print(f"⚠️  Claude CLI authentication error (run: claude auth)")
                else:
                    print(f"⚠️  Claude CLI error: {error_msg[:200]}")
                return {}

            text = result.stdout.strip()
            if not text:
                print("⚠️  Claude returned empty response")
                return {}

            return self._parse_semantic_response(text)

        except FileNotFoundError:
            print("⚠️  Claude CLI not found. Install from https://claude.ai/download")
            return {}
        except subprocess.TimeoutExpired:
            print("⚠️  Claude CLI request timed out")
            return {}
        except Exception as e:
            print(f"⚠️  Claude CLI analysis error: {e}")
            return {}
    
    def _semantic_analysis_codex(self, image_path: str, prompt: str) -> Dict:
        """Use OpenAI Codex CLI with pseudo-TTY for image analysis"""
        # Check platform first - PTY is Unix-only
        import sys
        if sys.platform == 'win32' or os.name == 'nt':
            print("⚠️  Codex CLI PTY mode not supported on Windows, using fallback")
            # Fallback to subprocess.run with timeout
            try:
                result = subprocess.run(
                    ["codex", prompt, "--image", image_path],
                    capture_output=True,
                    timeout=30,
                    text=True,
                    env={**os.environ, "FORCE_COLOR": "0"}
                )
                if result.returncode != 0:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    print(f"⚠️  Codex CLI error: {error_msg[:200]}")
                    return {}
                text = result.stdout.strip()
                if not text:
                    print("⚠️  Codex returned empty response")
                    return {}
                return self._parse_semantic_response(text)
            except FileNotFoundError:
                print("⚠️  Codex CLI not found. Install with: npm install -g @openai/codex")
                return {}
            except subprocess.TimeoutExpired:
                print("⚠️  Codex request timed out")
                return {}
            except Exception as e:
                print(f"⚠️  Codex analysis error: {e}")
                return {}
        
        # Unix platform - use PTY
        master = None
        slave = None
        process = None
        try:
            import pty
            import select
            import time
            
            # Create pseudo-terminal to bypass "stdout is not a terminal" error
            master, slave = pty.openpty()
            
            # Run codex with image path via pseudo-TTY
            process = subprocess.Popen(
                ["codex", prompt, "--image", image_path],
                stdin=slave,
                stdout=slave,
                stderr=slave,
                text=True,
                env={**os.environ, "FORCE_COLOR": "0"}
            )
            
            # Close slave in parent process immediately after spawning
            os.close(slave)
            slave = None  # Mark as closed to avoid double-close in finally
            
            # Read output from master with timeout
            output = []
            timeout = 30
            start_time = time.time()
            
            # Read output while process is running, with timeout
            while True:
                # Check if process finished
                if process.poll() is not None:
                    # Process finished, read remaining output
                    while True:
                        try:
                            data = os.read(master, 4096).decode('utf-8', errors='ignore')
                            if not data:
                                break
                            output.append(data)
                        except OSError:
                            break
                    break
                
                # Check for timeout using time-based check (more reliable than process.wait timeout)
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    print("⚠️  Codex request timed out")
                    process.kill()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        pass
                    break
                
                # Check if data available to read (non-blocking with short timeout)
                ready, _, _ = select.select([master], [], [], min(1.0, timeout - elapsed))
                if ready:
                    try:
                        data = os.read(master, 4096).decode('utf-8', errors='ignore')
                        if data:
                            output.append(data)
                    except OSError:
                        break
            
            text = ''.join(output).strip()
            
            if not text:
                print("⚠️  Codex returned empty response")
                return {}
            
            return self._parse_semantic_response(text)
            
        except ImportError:
            print("⚠️  pty module not available (non-Unix platform?)")
            return {}
        except FileNotFoundError:
            print("⚠️  Codex CLI not found. Install with: npm install -g @openai/codex")
            return {}
        except Exception as e:
            print(f"⚠️  Codex analysis error: {e}")
            return {}
        finally:
            # Ensure all resources are cleaned up
            if slave is not None:
                try:
                    os.close(slave)
                except OSError:
                    pass
            if master is not None:
                try:
                    os.close(master)
                except OSError:
                    pass
            if process is not None:
                try:
                    if process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                except Exception:
                    pass
    
    def _parse_semantic_response(self, text: str) -> Dict:
        """Parse semantic analysis response into structured format"""
        import re
        
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return {
                    'semantic_analysis': result,
                    'ui_components_detected': result.get('ui_components', []),
                    'accessibility_issues': result.get('accessibility_issues', []),
                    'design_recommendations': result.get('design_recommendations', [])
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback: try to extract structured info from text
        components = []
        issues = []
        recommendations = []
        
        # Simple pattern matching as fallback
        if 'button' in text.lower() or 'form' in text.lower():
            components.append("Interactive elements detected")
        if 'contrast' in text.lower():
            issues.append("Contrast issues mentioned")
        if 'recommend' in text.lower() or 'suggest' in text.lower():
            recommendations.append("See full analysis in raw response")
        
        return {
            'semantic_analysis': {'raw_response': text},
            'ui_components_detected': components if components else [],
            'accessibility_issues': issues if issues else [],
            'design_recommendations': recommendations if recommendations else []
        }
    
    def _evaluate_ux(self, metrics: UXMetrics) -> Tuple[float, List[str], List[str], List[str]]:
        """Evaluate overall UX quality and generate recommendations"""
        score = 0.0
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Score components (weighted)
        max_score = 100
        
        # Visual hierarchy (20 points)
        if metrics.visual_hierarchy_score > 0.5:
            score += 20
            strengths.append("Good visual hierarchy")
        else:
            score += metrics.visual_hierarchy_score * 20
            weaknesses.append("Weak visual hierarchy - elements lack clear size/importance variation")
            recommendations.append("Increase size contrast between primary and secondary elements")
        
        # Whitespace (15 points)
        if 0.3 <= metrics.whitespace_ratio <= 0.6:
            whitespace_contribution = 15
            strengths.append("Good whitespace balance")
        elif metrics.whitespace_ratio < 0.2:
            whitespace_contribution = max(0, min(15, metrics.whitespace_ratio * 75))
            weaknesses.append("Too little whitespace - layout feels cramped")
            recommendations.append("Increase padding and margins between elements")
        else:
            whitespace_contribution = max(0, min(15, 15 - (metrics.whitespace_ratio - 0.6) * 30))
            weaknesses.append("Too much whitespace - may feel empty")
            recommendations.append("Consider adding more content or reducing spacing")
        score += whitespace_contribution
        
        # Contrast (20 points)
        if metrics.color_contrast_score > 0.6:
            score += 20
            strengths.append("Good color contrast")
        else:
            score += metrics.color_contrast_score * 33.3
            weaknesses.append("Low color contrast - may affect readability")
            recommendations.append("Increase contrast between text and background colors")
        
        # Text readability (15 points)
        if metrics.text_readability_score > 0.7:
            score += 15
            strengths.append("Good text readability")
        else:
            score += metrics.text_readability_score * 21.4
            weaknesses.append("Text readability could be improved")
            recommendations.append("Adjust text color, size, or background for better readability")
        
        # Brightness (10 points)
        if 100 <= metrics.brightness <= 180:
            score += 10
            strengths.append("Appropriate brightness level")
        else:
            score += 5
            weaknesses.append("Brightness may be too high or too low")
            recommendations.append("Adjust overall brightness for better visual comfort")
        
        # Aspect ratio (10 points)
        if 1.3 <= metrics.aspect_ratio <= 2.0:
            score += 10
        else:
            score += 5
            recommendations.append("Consider standard screen aspect ratios (16:9, 16:10)")
        
        # Semantic analysis bonus (10 points)
        if metrics.semantic_analysis:
            score += 5
            if metrics.accessibility_issues and len(metrics.accessibility_issues) == 0:
                score += 5
                strengths.append("No major accessibility issues detected")
            elif metrics.accessibility_issues:
                score += max(0, 5 - len(metrics.accessibility_issues))
                weaknesses.extend(metrics.accessibility_issues[:3])  # Top 3 issues
                recommendations.extend(metrics.design_recommendations[:3])  # Top 3 recommendations
        
        # Add semantic recommendations if available
        if metrics.design_recommendations:
            recommendations.extend(metrics.design_recommendations[:5])
        
        return min(score, max_score), strengths, weaknesses, recommendations
    
    def analyze_directory(self, directory: str, output_file: Optional[str] = None) -> List[AnalysisResult]:
        """
        Analyze all images in a directory
        
        Args:
            directory: Directory containing screenshots
            output_file: Optional JSON file to save results
            
        Returns:
            List of AnalysisResult objects
        """
        directory = Path(directory)
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        
        results = []
        image_files = [f for f in directory.iterdir() 
                      if f.suffix.lower() in image_extensions]
        
        print(f"📸 Found {len(image_files)} images to analyze")
        
        for i, image_file in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] Analyzing {image_file.name}...")
            try:
                result = self.analyze_image(str(image_file))
                results.append(result)
                print(f"  ✅ Score: {result.overall_score:.1f}/100")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        if output_file:
            self._save_results(results, output_file)
        
        return results
    
    def _save_results(self, results: List[AnalysisResult], output_file: str):
        """Save analysis results to JSON file"""
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'total_images': len(results),
            'results': [self._result_to_dict(r) for r in results]
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to {output_file}")
    
    def _result_to_dict(self, result: AnalysisResult) -> Dict:
        """Convert AnalysisResult to dictionary for JSON serialization"""
        return {
            'image_path': result.image_path,
            'timestamp': result.timestamp,
            'overall_score': result.overall_score,
            'strengths': result.strengths,
            'weaknesses': result.weaknesses,
            'recommendations': result.recommendations,
            'metrics': {
                'image_size': result.metrics.image_size,
                'aspect_ratio': result.metrics.aspect_ratio,
                'brightness': result.metrics.brightness,
                'contrast': result.metrics.contrast,
                'whitespace_ratio': result.metrics.whitespace_ratio,
                'visual_hierarchy_score': result.metrics.visual_hierarchy_score,
                'color_contrast_score': result.metrics.color_contrast_score,
                'text_readability_score': result.metrics.text_readability_score,
                'ui_components_detected': result.metrics.ui_components_detected,
                'accessibility_issues': result.metrics.accessibility_issues,
                'design_recommendations': result.metrics.design_recommendations
            }
        }
    
    def print_summary(self, results: List[AnalysisResult]):
        """Print a summary of analysis results"""
        if not results:
            print("No results to summarize")
            return
        
        avg_score = sum(r.overall_score for r in results) / len(results)
        min_score = min(r.overall_score for r in results)
        max_score = max(r.overall_score for r in results)
        
        print("\n" + "="*60)
        print("📊 UX Analysis Summary")
        print("="*60)
        print(f"Total Images Analyzed: {len(results)}")
        print(f"Average Score: {avg_score:.1f}/100")
        print(f"Score Range: {min_score:.1f} - {max_score:.1f}")
        print("\nTop Issues:")
        
        # Count common weaknesses
        weakness_counts = {}
        for result in results:
            for weakness in result.weaknesses:
                weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
        
        for weakness, count in sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {weakness} ({count} images)")
        
        print("\nTop Recommendations:")
        recommendation_counts = {}
        for result in results:
            for rec in result.recommendations:
                recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        
        for rec, count in sorted(recommendation_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {rec} ({count} images)")


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze UI screenshots for UX quality')
    parser.add_argument('path', help='Path to image file or directory')
    parser.add_argument('--output', '-o', help='Output JSON file for results')
    parser.add_argument('--backend', choices=['auto', 'gemini', 'claude', 'codex'],
                       default='auto', help='CLI backend to use (default: auto-detect)')
    parser.add_argument('--summary', '-s', action='store_true', help='Print summary')

    args = parser.parse_args()

    analyzer = UXImageAnalyzer(cli_backend=args.backend)
    
    path = Path(args.path)
    
    if path.is_file():
        # Single image
        print(f"📸 Analyzing {path.name}...")
        result = analyzer.analyze_image(str(path))
        print(f"\n✅ Overall Score: {result.overall_score:.1f}/100")
        print(f"\nStrengths:")
        for s in result.strengths:
            print(f"  ✓ {s}")
        print(f"\nWeaknesses:")
        for w in result.weaknesses:
            print(f"  ✗ {w}")
        print(f"\nRecommendations:")
        for r in result.recommendations:
            print(f"  → {r}")
        
        if args.output:
            analyzer._save_results([result], args.output)
    
    elif path.is_dir():
        # Directory of images
        results = analyzer.analyze_directory(str(path), args.output)
        
        if args.summary:
            analyzer.print_summary(results)
    
    else:
        print(f"❌ Path not found: {path}")
        sys.exit(1)


if __name__ == '__main__':
    main()

