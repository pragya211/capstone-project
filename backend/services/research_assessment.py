import os
import json
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
from dotenv import load_dotenv

load_dotenv()

@dataclass
class MissingContent:
    """Represents missing content or topics in a research paper"""
    category: str
    topic: str
    importance: str  # "Critical", "Important", "Beneficial"
    description: str
    suggestion: str
    related_sections: List[str]

@dataclass
class ResearchAssessment:
    """Complete assessment of a research paper"""
    paper_title: str
    research_field: str
    overall_completeness_score: float  # 0-100
    missing_content: List[MissingContent]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    methodology_analysis: Dict[str, Any]
    literature_review_analysis: Dict[str, Any]
    results_analysis: Dict[str, Any]
    discussion_analysis: Dict[str, Any]

class ResearchPaperAssessor:
    """AI-powered research paper assessment service"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is missing from .env file")
    
    def assess_research_paper(self, paper_content: Dict[str, Any]) -> ResearchAssessment:
        """
        Comprehensive assessment of a research paper
        """
        try:
            # Extract paper information
            title = paper_content.get('metadata', {}).get('title', 'Unknown Title')
            abstract = paper_content.get('sections', {}).get('abstract', '')
            introduction = paper_content.get('sections', {}).get('introduction', '')
            methodology = paper_content.get('sections', {}).get('methodology', '')
            results = paper_content.get('sections', {}).get('results', '')
            discussion = paper_content.get('sections', {}).get('discussion', '')
            conclusion = paper_content.get('sections', {}).get('conclusion', '')
            references = paper_content.get('citations', [])
            
            # Combine all text for analysis
            full_text = f"{abstract}\n\n{introduction}\n\n{methodology}\n\n{results}\n\n{discussion}\n\n{conclusion}"
            
            # Determine research field
            research_field = self._identify_research_field(full_text, title)
            
            # Perform comprehensive analysis
            missing_content = self._analyze_missing_content(full_text, research_field)
            strengths = self._identify_strengths(full_text)
            weaknesses = self._identify_weaknesses(full_text, missing_content)
            recommendations = self._generate_recommendations(missing_content, weaknesses)
            
            # Section-specific analyses
            methodology_analysis = self._analyze_methodology(methodology)
            literature_review_analysis = self._analyze_literature_review(introduction, references)
            results_analysis = self._analyze_results(results)
            discussion_analysis = self._analyze_discussion(discussion, results)
            
            # Calculate completeness score using both structural and quality metrics
            completeness_score = self._calculate_completeness_score(
                paper_content, missing_content, methodology_analysis, 
                literature_review_analysis, results_analysis, discussion_analysis
            )
            
            return ResearchAssessment(
                paper_title=title,
                research_field=research_field,
                overall_completeness_score=completeness_score,
                missing_content=missing_content,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
                methodology_analysis=methodology_analysis,
                literature_review_analysis=literature_review_analysis,
                results_analysis=results_analysis,
                discussion_analysis=discussion_analysis
            )
            
        except Exception as e:
            raise Exception(f"Assessment failed: {str(e)}")
    
    def _identify_research_field(self, text: str, title: str) -> str:
        """Identify the research field based on content"""
        prompt = f"""
        Analyze the following research paper title and content to identify the primary research field.
        
        CRITICAL: Return ONLY the field name as plain text, NOT in JSON format.
        Examples: "Computer Science", "Medicine", "Psychology", "Physics", "Engineering", "Biology"
        
        Title: {title}
        Content: {text[:2000]}...
        
        Return only the field name:
        """
        
        try:
            response = self._call_openai(prompt, max_tokens=50)
            cleaned_response = self._clean_research_field_response(response.strip())
            
            # If cleaning didn't work or returned empty, try keyword-based detection
            if not cleaned_response or cleaned_response == "Unknown" or len(cleaned_response) < 3:
                cleaned_response = self._identify_field_by_keywords(text, title)
            
            return cleaned_response
        except Exception as e:
            print(f"Research field identification failed: {e}")
            return self._identify_field_by_keywords(text, title)
    
    def _clean_research_field_response(self, response: str) -> str:
        """Clean the research field response to remove JSON formatting"""
        # Remove JSON formatting if present
        response = response.strip()
        
        # Remove common JSON patterns
        if response.startswith('{') and response.endswith('}'):
            try:
                import json
                data = json.loads(response)
                if 'field' in data:
                    return data['field']
                elif 'research_field' in data:
                    return data['research_field']
            except:
                pass
        
        # Remove quotes if present
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        
        # Remove "field:" prefix if present
        if ':' in response:
            response = response.split(':', 1)[1].strip()
        
        # Clean up common variations
        field_mapping = {
            'cs': 'Computer Science',
            'computer science': 'Computer Science',
            'ai': 'Artificial Intelligence',
            'artificial intelligence': 'Artificial Intelligence',
            'ml': 'Machine Learning',
            'machine learning': 'Machine Learning',
            'nlp': 'Natural Language Processing',
            'natural language processing': 'Natural Language Processing'
        }
        
        response_lower = response.lower().strip()
        if response_lower in field_mapping:
            return field_mapping[response_lower]
        
        # Capitalize properly if it's all lowercase
        if response.islower():
            return response.title()
        
        return response
    
    def _identify_field_by_keywords(self, text: str, title: str) -> str:
        """Identify research field using keyword analysis as fallback"""
        combined_text = f"{title} {text}".lower()
        
        # Define keyword mappings for different fields
        field_keywords = {
            'Computer Science': [
                'algorithm', 'programming', 'software', 'computer', 'computing', 'data structure',
                'machine learning', 'artificial intelligence', 'neural network', 'deep learning',
                'natural language processing', 'computer vision', 'database', 'system',
                'network', 'security', 'cybersecurity', 'blockchain', 'cryptography'
            ],
            'Artificial Intelligence': [
                'artificial intelligence', 'ai', 'machine learning', 'neural network', 'deep learning',
                'reinforcement learning', 'supervised learning', 'unsupervised learning',
                'computer vision', 'natural language processing', 'nlp', 'automation',
                'intelligent system', 'cognitive', 'reasoning', 'knowledge representation'
            ],
            'Machine Learning': [
                'machine learning', 'ml', 'neural network', 'deep learning', 'model', 'training',
                'classification', 'regression', 'clustering', 'feature extraction', 'optimization',
                'gradient descent', 'backpropagation', 'tensorflow', 'pytorch', 'scikit-learn'
            ],
            'Mathematics': [
                'mathematical', 'equation', 'theorem', 'proof', 'algebra', 'calculus',
                'statistics', 'probability', 'optimization', 'linear algebra', 'geometry',
                'analysis', 'topology', 'number theory', 'discrete mathematics'
            ],
            'Physics': [
                'physics', 'quantum', 'mechanics', 'thermodynamics', 'electromagnetic',
                'particle', 'energy', 'force', 'motion', 'wave', 'relativity', 'quantum mechanics'
            ],
            'Biology': [
                'biology', 'biological', 'cell', 'dna', 'protein', 'genetics', 'evolution',
                'organism', 'molecular biology', 'biochemistry', 'ecology', 'microbiology'
            ],
            'Medicine': [
                'medical', 'medicine', 'clinical', 'patient', 'treatment', 'diagnosis',
                'therapy', 'healthcare', 'disease', 'symptom', 'pharmaceutical', 'drug'
            ],
            'Engineering': [
                'engineering', 'mechanical', 'electrical', 'civil', 'chemical', 'design',
                'manufacturing', 'construction', 'materials', 'structure', 'system design'
            ]
        }
        
        # Count keyword matches for each field
        field_scores = {}
        for field, keywords in field_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            field_scores[field] = score
        
        # Return the field with the highest score, or Computer Science as default
        if field_scores:
            best_field = max(field_scores, key=field_scores.get)
            if field_scores[best_field] > 0:
                return best_field
        
        return "Computer Science"  # Default fallback
    
    def _analyze_missing_content(self, text: str, research_field: str) -> List[MissingContent]:
        """Analyze what content is missing from the research paper"""
        prompt = f"""
        As an expert research paper reviewer in {research_field}, analyze the following research paper content and identify missing elements that should typically be included in a comprehensive research paper in this field.
        
        Paper content: {text[:4000]}...
        
        CRITICAL INSTRUCTIONS:
        1. You MUST respond with ONLY valid JSON
        2. Do NOT include any explanatory text before or after the JSON
        3. Do NOT use markdown code blocks (```json)
        4. The JSON must be properly formatted with correct quotes and brackets
        5. If no missing content is found, return an empty array: {{"missing_content": []}}
        
        For each missing element, identify:
        - Category: One of "Methodology", "Literature Review", "Results", "Discussion", "Ethics", "Limitations", "Future Work", "Conclusion"
        - Topic: Specific element that's missing
        - Importance: "Critical", "Important", or "Beneficial"
        - Description: What should be included
        - Suggestion: How to address the gap
        - Related sections: Which paper sections this affects
        
        RESPOND WITH ONLY THIS JSON FORMAT (NO OTHER TEXT):
        {{
            "missing_content": [
                {{
                    "category": "Methodology",
                    "topic": "Statistical Analysis",
                    "importance": "Critical",
                    "description": "Missing detailed statistical analysis methods",
                    "suggestion": "Add section on statistical tests used",
                    "related_sections": ["Methodology", "Results"]
                }},
                {{
                    "category": "Literature Review",
                    "topic": "Recent Work",
                    "importance": "Important",
                    "description": "Limited coverage of recent related work",
                    "suggestion": "Include more citations from 2022-2024",
                    "related_sections": ["Introduction", "Related Work"]
                }}
            ]
        }}
        """
        
        try:
            response = self._call_openai(prompt, max_tokens=2000)
            
            # Clean the response to extract only JSON
            response = response.strip()
            
            # Remove any markdown code blocks if present
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            
            response = response.strip()
            
            # Try to parse the JSON
            data = json.loads(response)
            
            missing_content = []
            for item in data.get("missing_content", []):
                missing_content.append(MissingContent(
                    category=item.get("category", "Unknown"),
                    topic=item.get("topic", "Unknown"),
                    importance=item.get("importance", "Important"),
                    description=item.get("description", "No description provided"),
                    suggestion=item.get("suggestion", "No suggestion provided"),
                    related_sections=item.get("related_sections", ["General"])
                ))
            
            return missing_content
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"JSON parsing error: {e}")
            print(f"Response received: {response[:500]}...")
            
            # Try to extract information from the response even if it's not perfect JSON
            try:
                # Fallback: try to extract information from text response
                return self._parse_text_response(response, text, research_field)
            except:
                # Final fallback if everything fails
                return [
                    MissingContent(
                        category="Analysis Error",
                        topic="Unable to parse AI response",
                        importance="Important",
                        description="The AI analysis could not be properly parsed. This might be due to API issues or response format problems.",
                        suggestion="Please try again or review the paper manually for completeness",
                        related_sections=["All sections"]
                    )
                ]
    
    def _parse_text_response(self, response: str, text: str, research_field: str) -> List[MissingContent]:
        """Fallback method to parse text response when JSON parsing fails"""
        try:
            # Try to extract basic information from the text response
            missing_content = []
            
            # Look for common patterns in the response
            lines = response.split('\n')
            current_item = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Try to identify key information
                if 'category' in line.lower() or 'section' in line.lower():
                    if current_item:
                        missing_content.append(self._create_missing_content_item(current_item))
                    current_item = {}
                    current_item['category'] = self._extract_category_from_line(line)
                
                elif 'importance' in line.lower() or 'critical' in line.lower() or 'important' in line.lower():
                    current_item['importance'] = self._extract_importance_from_line(line)
                
                elif 'description' in line.lower() or 'missing' in line.lower():
                    current_item['description'] = line
                
                elif 'suggestion' in line.lower() or 'recommend' in line.lower():
                    current_item['suggestion'] = line
            
            # Add the last item if exists
            if current_item:
                missing_content.append(self._create_missing_content_item(current_item))
            
            # If we couldn't extract anything meaningful, create a generic response
            if not missing_content:
                missing_content = [
                    MissingContent(
                        category="General Analysis",
                        topic="Paper Review",
                        importance="Important",
                        description="AI analysis completed but response format was unexpected",
                        suggestion="Please review the paper for standard research paper components",
                        related_sections=["All sections"]
                    )
                ]
            
            return missing_content
            
        except Exception as e:
            print(f"Text parsing fallback also failed: {e}")
            raise
    
    def _extract_category_from_line(self, line: str) -> str:
        """Extract category from a line of text"""
        line_lower = line.lower()
        if 'methodology' in line_lower:
            return "Methodology"
        elif 'literature' in line_lower:
            return "Literature Review"
        elif 'result' in line_lower:
            return "Results"
        elif 'discussion' in line_lower:
            return "Discussion"
        elif 'limitation' in line_lower:
            return "Limitations"
        elif 'ethical' in line_lower:
            return "Ethics"
        else:
            return "General"
    
    def _extract_importance_from_line(self, line: str) -> str:
        """Extract importance level from a line of text"""
        line_lower = line.lower()
        if 'critical' in line_lower:
            return "Critical"
        elif 'important' in line_lower:
            return "Important"
        else:
            return "Beneficial"
    
    def _create_missing_content_item(self, item_data: dict) -> MissingContent:
        """Create a MissingContent object from parsed data"""
        return MissingContent(
            category=item_data.get('category', 'General'),
            topic=item_data.get('topic', 'Analysis Point'),
            importance=item_data.get('importance', 'Important'),
            description=item_data.get('description', 'No description available'),
            suggestion=item_data.get('suggestion', 'Please review this section'),
            related_sections=item_data.get('related_sections', ['General'])
        )
    
    def _calculate_completeness_score(self, paper_content: Dict[str, Any], missing_content: List[MissingContent], 
                                    methodology_analysis: Dict[str, Any] = None, 
                                    literature_review_analysis: Dict[str, Any] = None,
                                    results_analysis: Dict[str, Any] = None,
                                    discussion_analysis: Dict[str, Any] = None) -> float:
        """Calculate overall completeness score (0-100) combining structural and quality metrics"""
        
        # Get deterministic section analysis
        sections = paper_content.get('sections', {})
        citations = paper_content.get('citations', [])
        
        # Calculate raw scores
        structural_section_raw = self._calculate_section_scores(sections)
        citation_raw = self._calculate_citation_score(len(citations))
        missing_content_raw = self._calculate_missing_content_score(missing_content)
        section_quality_raw = self._calculate_section_quality_score(
            methodology_analysis, literature_review_analysis, 
            results_analysis, discussion_analysis
        )
        
        # Calculate percentage within each bracket
        structural_percentage = self._calculate_section_percentage(sections)
        citation_percentage = self._calculate_citation_percentage(len(citations))
        missing_content_percentage = self._calculate_missing_content_percentage(missing_content)
        section_quality_percentage = self._calculate_section_quality_percentage(
            methodology_analysis, literature_review_analysis, 
            results_analysis, discussion_analysis
        )
        
        # Combine weighted scores for final score
        final_score = (
            structural_section_raw * 0.25 +    # 25% - Structural completeness
            section_quality_raw * 0.25 +       # 25% - Content quality
            citation_raw * 0.15 +              # 15% - Citation adequacy
            missing_content_raw * 0.35         # 35% - Missing content analysis
        )
        
        # Ensure score doesn't go below 20 (even very incomplete papers get some credit)
        final_score = max(20.0, min(100.0, final_score))
        
        # Calculate weighted contribution percentages (out of assigned weights)
        structural_weighted_contribution = (structural_percentage / 100.0) * 25.0  # 25% weight
        quality_weighted_contribution = (section_quality_percentage / 100.0) * 25.0  # 25% weight
        citation_weighted_contribution = (citation_percentage / 100.0) * 15.0  # 15% weight
        missing_content_weighted_contribution = (missing_content_percentage / 100.0) * 35.0  # 35% weight
        
        # Store detailed scoring for transparency with weighted percentage breakdown
        self._last_score_breakdown = {
            'raw_scores': {
                'structural_section_score': structural_section_raw,
                'section_quality_score': section_quality_raw,
                'citation_score': citation_raw,
                'missing_content_score': missing_content_raw,
            },
            'weighted_score_breakdown': {
                'structural_completeness': {
                    'score_out_of_weight': f"{structural_weighted_contribution:.1f}/25.0",
                    'percentage_of_weight': f"{(structural_weighted_contribution/25.0)*100:.1f}%",
                    'bracket': 'Structural Sections (25% weight)',
                    'description': f'Scored {structural_weighted_contribution:.1f} out of 25.0 points ({(structural_weighted_contribution/25.0)*100:.1f}% of assigned weight)'
                },
                'content_quality': {
                    'score_out_of_weight': f"{quality_weighted_contribution:.1f}/25.0",
                    'percentage_of_weight': f"{(quality_weighted_contribution/25.0)*100:.1f}%",
                    'bracket': 'Content Quality (25% weight)',
                    'description': f'Scored {quality_weighted_contribution:.1f} out of 25.0 points ({(quality_weighted_contribution/25.0)*100:.1f}% of assigned weight)'
                },
                'citation_adequacy': {
                    'score_out_of_weight': f"{citation_weighted_contribution:.1f}/15.0",
                    'percentage_of_weight': f"{(citation_weighted_contribution/15.0)*100:.1f}%",
                    'bracket': 'Citation Adequacy (15% weight)',
                    'description': f'Scored {citation_weighted_contribution:.1f} out of 15.0 points ({(citation_weighted_contribution/15.0)*100:.1f}% of assigned weight)'
                },
                'missing_content_analysis': {
                    'score_out_of_weight': f"{missing_content_weighted_contribution:.1f}/35.0",
                    'percentage_of_weight': f"{(missing_content_weighted_contribution/35.0)*100:.1f}%",
                    'bracket': 'Completeness Analysis (35% weight)',
                    'description': f'Scored {missing_content_weighted_contribution:.1f} out of 35.0 points ({(missing_content_weighted_contribution/35.0)*100:.1f}% of assigned weight)'
                }
            },
            'percentage_breakdown': {
                'structural_completeness': {
                    'percentage': structural_percentage,
                    'bracket': 'Structural Sections (25% weight)',
                    'description': f'Scored {structural_percentage:.1f}% of possible structural completeness'
                },
                'content_quality': {
                    'percentage': section_quality_percentage,
                    'bracket': 'Content Quality (25% weight)',
                    'description': f'Scored {section_quality_percentage:.1f}% of possible content quality'
                },
                'citation_adequacy': {
                    'percentage': citation_percentage,
                    'bracket': 'Citation Adequacy (15% weight)',
                    'description': f'Scored {citation_percentage:.1f}% of possible citation adequacy'
                },
                'missing_content_analysis': {
                    'percentage': missing_content_percentage,
                    'bracket': 'Completeness Analysis (35% weight)',
                    'description': f'Scored {missing_content_percentage:.1f}% of possible completeness'
                }
            },
            'final_score': final_score,
            'weights': {
                'structural_completeness': 0.25,
                'content_quality': 0.25,
                'citation_adequacy': 0.15,
                'missing_content_analysis': 0.35
            }
        }
        
        return final_score
    
    def _calculate_section_scores(self, sections: Dict[str, str]) -> float:
        """Calculate section completeness score (0-100) - deterministic"""
        essential_sections = ['abstract', 'introduction', 'methodology', 'results', 'discussion', 'conclusion']
        total_sections = len(essential_sections)
        present_sections = 0
        
        for section in essential_sections:
            content = sections.get(section, '').strip()
            if content and len(content) > 50:  # Must have substantial content
                present_sections += 1
        
        # Base score for section presence
        section_presence_score = (present_sections / total_sections) * 60  # Max 60 points
        
        # Additional points for content quality (length-based heuristics)
        content_quality_score = 0
        for section in essential_sections:
            content = sections.get(section, '').strip()
            if content:
                # Award points based on content length (heuristic for quality)
                length = len(content)
                if length > 500:  # Substantial content
                    content_quality_score += 6
                elif length > 200:  # Adequate content
                    content_quality_score += 4
                elif length > 100:  # Minimal content
                    content_quality_score += 2
        
        return min(100.0, section_presence_score + content_quality_score)
    
    def _calculate_section_quality_score(self, methodology_analysis: Dict[str, Any] = None,
                                        literature_review_analysis: Dict[str, Any] = None,
                                        results_analysis: Dict[str, Any] = None,
                                        discussion_analysis: Dict[str, Any] = None) -> float:
        """Calculate average quality score from AI section analyses"""
        quality_scores = []
        
        # Collect scores from each section analysis
        if methodology_analysis and 'score' in methodology_analysis:
            quality_scores.append(methodology_analysis['score'])
        
        if literature_review_analysis and 'score' in literature_review_analysis:
            quality_scores.append(literature_review_analysis['score'])
        
        if results_analysis and 'score' in results_analysis:
            quality_scores.append(results_analysis['score'])
        
        if discussion_analysis and 'score' in discussion_analysis:
            quality_scores.append(discussion_analysis['score'])
        
        # If no quality scores available, return neutral score
        if not quality_scores:
            return 50.0
        
        # Calculate average of available scores
        return sum(quality_scores) / len(quality_scores)
    
    def _calculate_citation_score(self, citation_count: int) -> float:
        """Calculate citation adequacy score (0-100) - deterministic"""
        if citation_count >= 30:
            return 100.0  # Excellent
        elif citation_count >= 20:
            return 90.0   # Very good
        elif citation_count >= 15:
            return 80.0   # Good
        elif citation_count >= 10:
            return 70.0   # Adequate
        elif citation_count >= 5:
            return 50.0   # Below average
        elif citation_count >= 1:
            return 30.0   # Poor
        else:
            return 10.0   # Very poor
    
    def _calculate_missing_content_score(self, missing_content: List[MissingContent]) -> float:
        """Calculate missing content score (0-100) - with deterministic fallback"""
        if not missing_content:
            return 100.0  # No missing content
        
        # Count missing content by importance level
        critical_count = len([c for c in missing_content if c.importance == "Critical"])
        important_count = len([c for c in missing_content if c.importance == "Important"])
        beneficial_count = len([c for c in missing_content if c.importance == "Beneficial"])
        
        # Deterministic scoring with diminishing returns
        critical_deduction = 0
        if critical_count >= 1:
            critical_deduction += 15  # First critical item
        if critical_count >= 2:
            critical_deduction += 12  # Second critical item
        if critical_count >= 3:
            critical_deduction += 10  # Third critical item
        if critical_count >= 4:
            critical_deduction += (critical_count - 3) * 8  # Additional items
        
        important_deduction = 0
        if important_count >= 1:
            important_deduction += 10  # First important item
        if important_count >= 2:
            important_deduction += 8   # Second important item
        if important_count >= 3:
            important_deduction += (important_count - 2) * 6  # Additional items
        
        beneficial_deduction = min(beneficial_count * 3, 15)  # Capped at 15 points
        
        total_deduction = critical_deduction + important_deduction + beneficial_deduction
        return max(0.0, 100.0 - total_deduction)
    
    def _calculate_section_percentage(self, sections: Dict[str, str]) -> float:
        """Calculate percentage of structural completeness achieved"""
        essential_sections = ['abstract', 'introduction', 'methodology', 'results', 'discussion', 'conclusion']
        total_sections = len(essential_sections)
        present_sections = 0
        content_quality_points = 0
        
        for section in essential_sections:
            content = sections.get(section, '').strip()
            if content and len(content) > 50:
                present_sections += 1
                # Calculate content quality percentage within this section
                length = len(content)
                if length > 500:
                    content_quality_points += 1.0  # Full quality
                elif length > 200:
                    content_quality_points += 0.7  # 70% quality
                elif length > 100:
                    content_quality_points += 0.4  # 40% quality
                else:
                    content_quality_points += 0.2  # 20% quality
        
        # Section presence percentage (60% of total)
        section_presence_pct = (present_sections / total_sections) * 60
        
        # Content quality percentage (40% of total)
        max_quality_points = total_sections * 1.0  # If all sections had perfect quality
        content_quality_pct = (content_quality_points / max_quality_points) * 40 if max_quality_points > 0 else 0
        
        return section_presence_pct + content_quality_pct
    
    def _calculate_citation_percentage(self, citation_count: int) -> float:
        """Calculate percentage of citation adequacy achieved"""
        # Define citation brackets and their percentage values
        if citation_count >= 30:
            return 100.0  # Excellent - 100% of citation adequacy
        elif citation_count >= 20:
            # Linear interpolation between 90-100%
            return 90.0 + ((citation_count - 20) / 10) * 10
        elif citation_count >= 15:
            # Linear interpolation between 80-90%
            return 80.0 + ((citation_count - 15) / 5) * 10
        elif citation_count >= 10:
            # Linear interpolation between 70-80%
            return 70.0 + ((citation_count - 10) / 5) * 10
        elif citation_count >= 5:
            # Linear interpolation between 50-70%
            return 50.0 + ((citation_count - 5) / 5) * 20
        elif citation_count >= 1:
            # Linear interpolation between 30-50%
            return 30.0 + ((citation_count - 1) / 4) * 20
        else:
            return 10.0  # Very poor - 10% of citation adequacy
    
    def _calculate_missing_content_percentage(self, missing_content: List[MissingContent]) -> float:
        """Calculate percentage of completeness (inverse of missing content)"""
        if not missing_content:
            return 100.0  # Perfect completeness
        
        # Calculate total penalty points
        critical_count = len([c for c in missing_content if c.importance == "Critical"])
        important_count = len([c for c in missing_content if c.importance == "Important"])
        beneficial_count = len([c for c in missing_content if c.importance == "Beneficial"])
        
        # Calculate penalty points (same logic as _calculate_missing_content_score)
        critical_deduction = 0
        if critical_count >= 1:
            critical_deduction += 15
        if critical_count >= 2:
            critical_deduction += 12
        if critical_count >= 3:
            critical_deduction += 10
        if critical_count >= 4:
            critical_deduction += (critical_count - 3) * 8
        
        important_deduction = 0
        if important_count >= 1:
            important_deduction += 10
        if important_count >= 2:
            important_deduction += 8
        if important_count >= 3:
            important_deduction += (important_count - 2) * 6
        
        beneficial_deduction = min(beneficial_count * 3, 15)
        
        total_deduction = critical_deduction + important_deduction + beneficial_deduction
        completeness_percentage = max(0.0, 100.0 - total_deduction)
        
        return completeness_percentage
    
    def _calculate_section_quality_percentage(self, methodology_analysis: Dict[str, Any] = None,
                                            literature_review_analysis: Dict[str, Any] = None,
                                            results_analysis: Dict[str, Any] = None,
                                            discussion_analysis: Dict[str, Any] = None) -> float:
        """Calculate percentage of content quality achieved"""
        quality_scores = []
        
        # Collect scores from each section analysis
        if methodology_analysis and 'score' in methodology_analysis:
            quality_scores.append(methodology_analysis['score'])
        
        if literature_review_analysis and 'score' in literature_review_analysis:
            quality_scores.append(literature_review_analysis['score'])
        
        if results_analysis and 'score' in results_analysis:
            quality_scores.append(results_analysis['score'])
        
        if discussion_analysis and 'score' in discussion_analysis:
            quality_scores.append(discussion_analysis['score'])
        
        # If no quality scores available, return neutral percentage
        if not quality_scores:
            return 50.0  # 50% of possible content quality
        
        # Calculate average percentage of content quality
        return sum(quality_scores) / len(quality_scores)
    
    def get_last_score_breakdown(self) -> Dict[str, Any]:
        """Get the detailed breakdown of the last calculated score"""
        return getattr(self, '_last_score_breakdown', {
            'raw_scores': {
                'structural_section_score': 0,
                'section_quality_score': 0,
                'citation_score': 0,
                'missing_content_score': 0,
            },
            'weighted_score_breakdown': {
                'structural_completeness': {'score_out_of_weight': '0.0/25.0', 'percentage_of_weight': '0.0%', 'bracket': 'Structural Sections', 'description': 'No analysis performed'},
                'content_quality': {'score_out_of_weight': '0.0/25.0', 'percentage_of_weight': '0.0%', 'bracket': 'Content Quality', 'description': 'No analysis performed'},
                'citation_adequacy': {'score_out_of_weight': '0.0/15.0', 'percentage_of_weight': '0.0%', 'bracket': 'Citation Adequacy', 'description': 'No analysis performed'},
                'missing_content_analysis': {'score_out_of_weight': '0.0/35.0', 'percentage_of_weight': '0.0%', 'bracket': 'Completeness Analysis', 'description': 'No analysis performed'}
            },
            'percentage_breakdown': {
                'structural_completeness': {'percentage': 0, 'bracket': 'Structural Sections', 'description': 'No analysis performed'},
                'content_quality': {'percentage': 0, 'bracket': 'Content Quality', 'description': 'No analysis performed'},
                'citation_adequacy': {'percentage': 0, 'bracket': 'Citation Adequacy', 'description': 'No analysis performed'},
                'missing_content_analysis': {'percentage': 0, 'bracket': 'Completeness Analysis', 'description': 'No analysis performed'}
            },
            'final_score': 0,
            'weights': {}
        })
    
    def _identify_strengths(self, text: str) -> List[str]:
        """Identify strengths of the research paper"""
        try:
            prompt = f"""
            Analyze the following research paper content and identify its main strengths.
            List 3-5 key strengths as bullet points starting with "-".
            
            Paper content: {text[:3000]}...
            
            Format your response as:
            - Strength 1
            - Strength 2
            - Strength 3
            """
            
            response = self._call_openai(prompt, max_tokens=300)
            # Parse bullet points from response
            strengths = [line.strip('- ').strip() for line in response.split('\n') if line.strip().startswith('-')]
            
            # If no bullet points found, try to extract from numbered list or paragraphs
            if not strengths:
                lines = response.split('\n')
                strengths = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10][:5]
            
            return strengths[:5] if strengths else ["Analysis completed - strengths identified"]
            
        except Exception as e:
            print(f"Error identifying strengths: {e}")
            return ["Unable to identify strengths due to analysis error"]
    
    def _identify_weaknesses(self, text: str, missing_content: List[MissingContent]) -> List[str]:
        """Identify weaknesses in the research paper"""
        try:
            prompt = f"""
            Analyze the following research paper content and identify its main weaknesses.
            Focus on methodological issues, gaps in analysis, or presentation problems.
            List 3-5 key weaknesses as bullet points starting with "-".
            
            Paper content: {text[:3000]}...
            
            Format your response as:
            - Weakness 1
            - Weakness 2
            - Weakness 3
            """
            
            response = self._call_openai(prompt, max_tokens=300)
            # Parse bullet points from response
            weaknesses = [line.strip('- ').strip() for line in response.split('\n') if line.strip().startswith('-')]
            
            # If no bullet points found, try to extract from numbered list or paragraphs
            if not weaknesses:
                lines = response.split('\n')
                weaknesses = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10][:5]
            
            return weaknesses[:5] if weaknesses else ["Analysis completed - weaknesses identified"]
            
        except Exception as e:
            print(f"Error identifying weaknesses: {e}")
            return ["Unable to identify weaknesses due to analysis error"]
    
    def _generate_recommendations(self, missing_content: List[MissingContent], weaknesses: List[str]) -> List[str]:
        """Generate actionable recommendations for improvement"""
        recommendations = []
        
        # Recommendations based on missing content
        for content in missing_content:
            if content.importance == "Critical":
                recommendations.append(f"CRITICAL: {content.suggestion}")
            elif content.importance == "Important":
                recommendations.append(f"IMPORTANT: {content.suggestion}")
        
        # Recommendations based on weaknesses
        for weakness in weaknesses[:3]:  # Top 3 weaknesses
            recommendations.append(f"Address weakness: {weakness}")
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    def _analyze_methodology(self, methodology_text: str) -> Dict[str, Any]:
        """Analyze methodology section"""
        if not methodology_text.strip():
            return {"score": 0, "issues": ["Methodology section is missing"], "suggestions": ["Add comprehensive methodology section"]}
        
        prompt = f"""
        Analyze the methodology section of this research paper.
        
        Methodology: {methodology_text[:2000]}...
        
        CRITICAL: Respond with ONLY valid JSON. No explanatory text.
        
        Return in this exact JSON format:
        {{
            "score": 75,
            "issues": ["Issue 1", "Issue 2"],
            "suggestions": ["Suggestion 1", "Suggestion 2"]
        }}
        """
        
        try:
            response = self._call_openai(prompt, max_tokens=500)
            
            # Clean the response to extract only JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
        except Exception as e:
            print(f"Methodology analysis JSON parsing error: {e}")
            return {"score": 50, "issues": ["Unable to analyze methodology"], "suggestions": ["Review methodology section manually"]}
    
    def _analyze_literature_review(self, introduction_text: str, references: List[Any]) -> Dict[str, Any]:
        """Analyze literature review quality"""
        prompt = f"""
        Analyze the literature review in this research paper's introduction.
        Number of references found: {len(references)}
        
        Introduction: {introduction_text[:2000]}...
        
        CRITICAL: Respond with ONLY valid JSON. No explanatory text.
        
        Return in this exact JSON format:
        {{
            "score": 80,
            "coverage_adequacy": "Good coverage of relevant literature",
            "critical_analysis": "Provides critical analysis of existing work",
            "research_gap_identification": "Clearly identifies research gaps",
            "suggestions": ["Suggestion 1", "Suggestion 2"]
        }}
        """
        
        try:
            response = self._call_openai(prompt, max_tokens=500)
            
            # Clean the response to extract only JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
        except Exception as e:
            print(f"Literature review analysis JSON parsing error: {e}")
            return {"score": 50, "coverage_adequacy": "Unknown", "critical_analysis": "Unknown", "research_gap_identification": "Unknown", "suggestions": ["Review literature review manually"]}
    
    def _analyze_results(self, results_text: str) -> Dict[str, Any]:
        """Analyze results section"""
        if not results_text.strip():
            return {"score": 0, "issues": ["Results section is missing"], "suggestions": ["Add comprehensive results section"]}
        
        prompt = f"""
        Analyze the results section of this research paper.
        
        Results: {results_text[:2000]}...
        
        CRITICAL: Respond with ONLY valid JSON. No explanatory text.
        
        Return in this exact JSON format:
        {{
            "score": 85,
            "presentation_clarity": "Results are clearly presented",
            "statistical_analysis": "Adequate statistical analysis",
            "visual_elements": "Good use of figures and tables",
            "suggestions": ["Suggestion 1", "Suggestion 2"]
        }}
        """
        
        try:
            response = self._call_openai(prompt, max_tokens=500)
            
            # Clean the response to extract only JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
        except Exception as e:
            print(f"Results analysis JSON parsing error: {e}")
            return {"score": 50, "presentation_clarity": "Unknown", "statistical_analysis": "Unknown", "visual_elements": "Unknown", "suggestions": ["Review results section manually"]}
    
    def _analyze_discussion(self, discussion_text: str, results_text: str) -> Dict[str, Any]:
        """Analyze discussion section"""
        if not discussion_text.strip():
            return {"score": 0, "issues": ["Discussion section is missing"], "suggestions": ["Add comprehensive discussion section"]}
        
        prompt = f"""
        Analyze the discussion section of this research paper.
        
        Discussion: {discussion_text[:2000]}...
        Results context: {results_text[:1000]}...
        
        CRITICAL: Respond with ONLY valid JSON. No explanatory text.
        
        Return in this exact JSON format:
        {{
            "score": 70,
            "result_interpretation": "Good interpretation of results",
            "literature_comparison": "Compares well with existing literature",
            "limitations": "Acknowledges study limitations",
            "future_work": "Suggests future research directions",
            "suggestions": ["Suggestion 1", "Suggestion 2"]
        }}
        """
        
        try:
            response = self._call_openai(prompt, max_tokens=500)
            
            # Clean the response to extract only JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
        except Exception as e:
            print(f"Discussion analysis JSON parsing error: {e}")
            return {"score": 50, "result_interpretation": "Unknown", "literature_comparison": "Unknown", "limitations": "Unknown", "future_work": "Unknown", "suggestions": ["Review discussion section manually"]}
    
    def _call_openai(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call OpenAI API with error handling"""
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are an expert research paper reviewer and academic editor with extensive experience in various research fields. When asked to provide JSON responses, you MUST respond with ONLY valid JSON. Do not include any explanatory text, markdown formatting, or code blocks. The JSON must be properly formatted and parseable."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.0,
                    "max_tokens": max_tokens
                },
                timeout=60  # 60 second timeout
            )
            
            if response.status_code != 200:
                error_detail = response.text
                if "quota" in error_detail.lower() or "billing" in error_detail.lower():
                    raise Exception(f"OpenAI API billing/quota issue: {error_detail}")
                elif "rate limit" in error_detail.lower():
                    raise Exception(f"OpenAI API rate limit exceeded: {error_detail}")
                else:
                    raise Exception(f"OpenAI API Error: {response.status_code} - {error_detail}")
            
            response.raise_for_status()
            data = response.json()
            
            if "choices" not in data or len(data["choices"]) == 0:
                raise Exception("No response choices returned from OpenAI API")
            
            content = data["choices"][0]["message"]["content"]
            if not content:
                raise Exception("Empty response content from OpenAI API")
            
            return content
            
        except requests.exceptions.Timeout:
            raise Exception("OpenAI API request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error connecting to OpenAI API: {str(e)}")
        except KeyError as e:
            raise Exception(f"Unexpected response format from OpenAI API: {str(e)}")
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
