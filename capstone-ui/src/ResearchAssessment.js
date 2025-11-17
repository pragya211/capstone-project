import React, { useState } from 'react';
import apiClient from './apiClient';
import { useAuth } from './context/AuthContext';

const ResearchAssessment = ({ 
  sharedFile, 
  setSharedFile, 
  sharedAssessmentData, 
  setSharedAssessmentData,
  sharedLoadingAssessment, 
  setSharedLoadingAssessment 
}) => {
  const [assessmentType, setAssessmentType] = useState('comprehensive');
  const [assessmentResults, setAssessmentResults] = useState(null);
  const [error, setError] = useState(null);
  const { user } = useAuth();

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSharedFile(file);
      setAssessmentResults(null);
      setError(null);
    }
  };

  const performAssessment = async (type = 'comprehensive') => {
    if (!sharedFile) {
      setError('Please select a PDF file first');
      return;
    }

    setSharedLoadingAssessment(true);
    setError(null);
    setAssessmentResults(null);

    try {
      const formData = new FormData();
      formData.append('file', sharedFile);

      let endpoint;
      switch (type) {
        case 'quick':
          endpoint = '/assess/quick-missing-analysis';
          break;
        case 'comprehensive':
        default:
          endpoint = '/assess/assess-paper';
          break;
      }

      const { data } = await apiClient.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setAssessmentResults(data);
      setSharedAssessmentData(data);
    } catch (err) {
      console.error('Assessment error:', err);
      setError(`Assessment failed: ${err.message}`);
    } finally {
      setSharedLoadingAssessment(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#28a745'; // Green
    if (score >= 60) return '#ffc107'; // Yellow
    return '#dc3545'; // Red
  };

  const getImportanceColor = (importance) => {
    if (!importance || typeof importance !== 'string') {
      return '#6c757d'; // Default color for undefined/null importance
    }
    switch (importance.toLowerCase()) {
      case 'critical': return '#dc3545';
      case 'important': return '#ffc107';
      case 'beneficial': return '#17a2b8';
      default: return '#6c757d';
    }
  };

  const renderAssessmentResults = () => {
    if (!assessmentResults) return null;

    // Handle different response formats
    let assessment;
    if (assessmentResults.assessment) {
      // Comprehensive assessment format
      assessment = assessmentResults.assessment;
    } else if (assessmentResults.paper_title) {
      // Quick analysis format - convert to standard format
      console.log('Quick analysis response:', assessmentResults); // Debug log
      console.log('Quick analysis score_breakdown:', assessmentResults.score_breakdown); // Debug log
      assessment = {
        paper_title: assessmentResults.paper_title,
        research_field: assessmentResults.research_field,
        overall_completeness_score: assessmentResults.completeness_score,
        missing_content: assessmentResults.critical_missing_content || [],
        strengths: [],
        weaknesses: [],
        recommendations: [],
        methodology_analysis: {},
        literature_review_analysis: {},
        results_analysis: {},
        discussion_analysis: {},
        assessment_summary: assessmentResults.assessment_summary || {
          total_missing_items: assessmentResults.total_critical_issues || 0,
          critical_missing: assessmentResults.total_critical_issues || 0,
          important_missing: 0,
          beneficial_missing: 0
        },
        score_breakdown: assessmentResults.score_breakdown ? {
          ...assessmentResults.score_breakdown,
          weighted_score_breakdown: assessmentResults.score_breakdown.weighted_score_breakdown || {
            structural_completeness: { score_out_of_weight: '0.0/25.0', percentage_of_weight: '0.0%' },
            content_quality: { score_out_of_weight: '0.0/25.0', percentage_of_weight: '0.0%' },
            citation_adequacy: { score_out_of_weight: '0.0/15.0', percentage_of_weight: '0.0%' },
            missing_content_analysis: { score_out_of_weight: '0.0/35.0', percentage_of_weight: '0.0%' }
          }
        } : {
          weighted_score_breakdown: {
            structural_completeness: { score_out_of_weight: '0.0/25.0', percentage_of_weight: '0.0%' },
            content_quality: { score_out_of_weight: '0.0/25.0', percentage_of_weight: '0.0%' },
            citation_adequacy: { score_out_of_weight: '0.0/15.0', percentage_of_weight: '0.0%' },
            missing_content_analysis: { score_out_of_weight: '0.0/35.0', percentage_of_weight: '0.0%' }
          }
        }
      };
    } else {
      return null;
    }

    return (
      <div style={{ marginTop: '20px' }}>
        {/* Header */}
        <div style={{ 
          backgroundColor: '#f8f9fa', 
          padding: '20px', 
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #dee2e6'
        }}>
          <h2 style={{ color: '#495057', margin: '0 0 10px 0' }}>
            📄 {assessment.paper_title || 'Research Paper Assessment'}
          </h2>
          <p style={{ margin: '0', color: '#6c757d' }}>
            <strong>Research Field:</strong> {assessment.research_field || 'Unknown'}
          </p>
          {!assessmentResults.assessment && (
            <div style={{ 
              marginTop: '10px', 
              padding: '8px 12px', 
              backgroundColor: '#fff3cd', 
              border: '1px solid #ffeaa7',
              borderRadius: '4px',
              fontSize: '14px',
              color: '#856404'
            }}>
              ⚡ <strong>Quick Analysis:</strong> This is a fast analysis focusing only on critical missing content. For a complete assessment with all details, use "Comprehensive Assessment".
            </div>
          )}
          <div style={{ 
            marginTop: '15px',
            display: 'flex',
            alignItems: 'center',
            gap: '20px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontWeight: 'bold', color: '#495057' }}>Completeness Score:</span>
              <div style={{
                backgroundColor: getScoreColor(assessment.overall_completeness_score),
                color: 'white',
                padding: '5px 15px',
                borderRadius: '20px',
                fontWeight: 'bold',
                fontSize: '18px'
              }}>
                {assessment.overall_completeness_score?.toFixed(1) || '0'}/100
              </div>
            </div>
            {assessment.assessment_summary && (
              <div style={{ display: 'flex', gap: '15px', fontSize: '14px' }}>
                <span style={{ color: '#dc3545' }}>
                  🚨 Critical: {assessment.assessment_summary.critical_missing}
                </span>
                {!assessmentResults.assessment && (
                  <span style={{ color: '#6c757d', fontSize: '12px' }}>
                    (Quick analysis - showing only critical issues)
                  </span>
                )}
                {assessmentResults.assessment && (
                  <>
                    <span style={{ color: '#ffc107' }}>
                      ⚠️ Important: {assessment.assessment_summary.important_missing}
                    </span>
                    <span style={{ color: '#17a2b8' }}>
                      💡 Beneficial: {assessment.assessment_summary.beneficial_missing}
                    </span>
                  </>
                )}
              </div>
            )}
          </div>
          
          {/* Score Breakdown */}
          {assessment.score_breakdown && (
            <div style={{ 
              marginTop: '20px', 
              padding: '15px', 
              backgroundColor: '#ffffff', 
              borderRadius: '8px',
              border: '1px solid #dee2e6'
            }}>
              <h4 style={{ margin: '0 0 15px 0', color: '#495057' }}>📊 Score Breakdown</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
                    {assessment.score_breakdown.weighted_score_breakdown?.structural_completeness?.score_out_of_weight?.split('/')[0] || 
                     ((assessment.score_breakdown.structural_section_score || 0) * 0.25).toFixed(1)}
                  </div>
                  <div style={{ fontSize: '12px', color: '#6c757d' }}>Structural Completeness</div>
                  <div style={{ fontSize: '10px', color: '#6c757d' }}>(25%)</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
                    {assessment.score_breakdown.weighted_score_breakdown?.content_quality?.score_out_of_weight?.split('/')[0] || 
                     ((assessment.score_breakdown.section_quality_score || 0) * 0.25).toFixed(1)}
                  </div>
                  <div style={{ fontSize: '12px', color: '#6c757d' }}>Content Quality</div>
                  <div style={{ fontSize: '10px', color: '#6c757d' }}>(25%)</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ffc107' }}>
                    {assessment.score_breakdown.weighted_score_breakdown?.citation_adequacy?.score_out_of_weight?.split('/')[0] || 
                     ((assessment.score_breakdown.citation_score || 0) * 0.15).toFixed(1)}
                  </div>
                  <div style={{ fontSize: '12px', color: '#6c757d' }}>Citation Adequacy</div>
                  <div style={{ fontSize: '10px', color: '#6c757d' }}>(15%)</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
                    {assessment.score_breakdown.weighted_score_breakdown?.missing_content_analysis?.score_out_of_weight?.split('/')[0] || 
                     ((assessment.score_breakdown.missing_content_score || 0) * 0.35).toFixed(1)}
                  </div>
                  <div style={{ fontSize: '12px', color: '#6c757d' }}>Missing Content</div>
                  <div style={{ fontSize: '10px', color: '#6c757d' }}>(35%)</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Missing Content */}
        {assessment.missing_content && assessment.missing_content.length > 0 && (
          <div style={{ marginBottom: '30px' }}>
            <h3 style={{ color: 'var(--color-text)', borderBottom: '2px solid #007bff', paddingBottom: '10px' }}>
              {!assessmentResults.assessment ? '🚨 Critical Missing Content' : '🔍 Missing Content Analysis'}
            </h3>
            {!assessmentResults.assessment && (
              <div style={{ 
                marginBottom: '15px', 
                padding: '10px', 
                backgroundColor: '#f8d7da', 
                border: '1px solid #f5c6cb',
                borderRadius: '4px',
                fontSize: '14px',
                color: '#721c24'
              }}>
                ⚠️ <strong>Quick Analysis Results:</strong> Showing only critical issues that need immediate attention. 
                {assessmentResults.total_critical_issues > 0 
                  ? ` Found ${assessmentResults.total_critical_issues} critical issue${assessmentResults.total_critical_issues > 1 ? 's' : ''}.`
                  : ' No critical issues found.'
                }
              </div>
            )}
            <div style={{ display: 'grid', gap: '15px' }}>
              {assessment.missing_content.map((item, index) => (
                <div key={index} style={{
                  border: '1px solid #dee2e6',
                  borderRadius: '8px',
                  padding: '15px',
                  backgroundColor: '#ffffff'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                    <div>
                      <h4 style={{ margin: '0 0 5px 0', color: '#212529' }}>
                        {item.topic}
                      </h4>
                      <span style={{
                        backgroundColor: getImportanceColor(item.importance),
                        color: 'white',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        {item.importance || 'Critical'}
                      </span>
                      <span style={{
                        marginLeft: '10px',
                        color: '#6c757d',
                        fontSize: '14px'
                      }}>
                        {item.category}
                      </span>
                    </div>
                  </div>
                  <p style={{ margin: '10px 0', color: '#212529' }}>
                    <strong>Description:</strong> {item.description}
                  </p>
                  <div style={{
                    backgroundColor: '#e9ecef',
                    padding: '10px',
                    borderRadius: '5px',
                    borderLeft: '4px solid #007bff',
                    color: '#212529'
                  }}>
                    <strong style={{ color: '#212529' }}>💡 Suggestion:</strong> <span style={{ color: '#212529' }}>{item.suggestion}</span>
                  </div>
                  {item.related_sections && item.related_sections.length > 0 && (
                    <div style={{ marginTop: '10px', fontSize: '14px', color: '#6c757d' }}>
                      <strong>Related sections:</strong> {item.related_sections.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Strengths and Weaknesses - Only show for comprehensive assessment */}
        {assessmentResults.assessment && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '30px' }}>
            {/* Strengths */}
            {assessment.strengths && assessment.strengths.length > 0 && (
            <div>
              <h3 style={{ color: '#28a745', borderBottom: '2px solid #28a745', paddingBottom: '10px' }}>
                ✅ Strengths
              </h3>
              <ul style={{ paddingLeft: '20px' }}>
                {assessment.strengths.map((strength, index) => {
                  // Remove bullet points, double quotes, and numbering patterns
                  // Pattern: "• - Strength 1": "actual text" or • - Strength 1: "actual text"
                  let cleanedStrength = strength;
                  
                  // Try to match the pattern and extract just the content
                  // Match: "• - Strength X": "content" or any variation
                  const patternMatch = cleanedStrength.match(/["']?\s*[•\u2022\-\s]+\s*["']?\s*Strength\s+\d+\s*["']?\s*:\s*["']?\s*(.+)/i);
                  if (patternMatch && patternMatch[1]) {
                    cleanedStrength = patternMatch[1];
                  } else {
                    // Fallback: remove patterns step by step
                    cleanedStrength = cleanedStrength
                      .replace(/^["']?\s*[•\u2022\-\s]+\s*["']?\s*Strength\s+\d+\s*["']?\s*:\s*["']?\s*/gi, '')
                      .replace(/^["']?\s*[•\u2022\-\s]+\s*["']?/g, '')
                      .replace(/^["']?\s*Strength\s+\d+\s*["']?\s*:\s*["']?\s*/gi, '')
                      .replace(/^\d+\.\s*/, '') // Remove "1. " at start
                      .replace(/^\d+\)\s*/, '') // Remove "1) " at start
                      .replace(/^\(\d+\)\s*/, ''); // Remove "(1) " at start
                  }
                  
                  // Remove any remaining numbering patterns anywhere in the text
                  cleanedStrength = cleanedStrength
                    .replace(/\s*Strength\s+\d+\s*:\s*/gi, '') // Remove "Strength X:" anywhere
                    .replace(/^\d+\.\s*/, '') // Remove "1. " at start
                    .replace(/^\d+\)\s*/, '') // Remove "1) " at start
                    .replace(/^\(\d+\)\s*/, '') // Remove "(1) " at start
                    .replace(/^["']+/, '') // Remove surrounding quotes at start
                    .replace(/["']+$/, '') // Remove surrounding quotes at end
                    .trim();
                  
                  return (
                    <li key={index} style={{ marginBottom: '8px', color: 'var(--color-text)' }}>
                      {cleanedStrength}
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          {/* Weaknesses */}
          {assessment.weaknesses && assessment.weaknesses.length > 0 && (
            <div>
              <h3 style={{ color: '#dc3545', borderBottom: '2px solid #dc3545', paddingBottom: '10px' }}>
                ❌ Weaknesses
              </h3>
              <ul style={{ paddingLeft: '20px' }}>
                {assessment.weaknesses.map((weakness, index) => (
                  <li key={index} style={{ marginBottom: '8px', color: 'var(--color-text)' }}>
                    {weakness}
                  </li>
                ))}
              </ul>
            </div>
          )}
          </div>
        )}

        {/* Recommendations - Only show for comprehensive assessment */}
        {assessmentResults.assessment && assessment.recommendations && assessment.recommendations.length > 0 && (
          <div style={{ marginBottom: '30px' }}>
            <h3 style={{ color: '#007bff', borderBottom: '2px solid #007bff', paddingBottom: '10px' }}>
              💡 Recommendations
            </h3>
            <ul style={{ paddingLeft: '20px', listStyleType: 'none' }}>
              {assessment.recommendations.map((recommendation, index) => (
                <li key={index} style={{ 
                  marginBottom: '10px', 
                  color: '#495057',
                  padding: '10px',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '5px',
                  borderLeft: '4px solid #007bff'
                }}>
                  {recommendation}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Detailed Analysis - Only show for comprehensive assessment */}
        {assessmentResults.assessment && (
          <div style={{ marginBottom: '30px' }}>
            <h3 style={{ color: 'var(--color-text)', borderBottom: '2px solid #6c757d', paddingBottom: '10px' }}>
              📊 Detailed Section Analysis
            </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            {/* Methodology Analysis */}
            {assessment.methodology_analysis && (
              <div style={{
                border: '1px solid #dee2e6',
                borderRadius: '8px',
                padding: '15px',
                backgroundColor: '#ffffff'
              }}>
                <h4 style={{ color: '#007bff', margin: '0 0 10px 0' }}>🔬 Methodology</h4>
                <p style={{ margin: '0', color: '#495057' }}>
                  Score: <strong>{assessment.methodology_analysis.score ?? 'N/A'}/100</strong>
                </p>
                {assessment.methodology_analysis.suggestions && (
                  <div style={{ marginTop: '10px' }}>
                    <strong style={{ color: '#212529' }}>Suggestions:</strong>
                    <ul style={{ margin: '5px 0 0 20px', fontSize: '14px' }}>
                      {assessment.methodology_analysis.suggestions.slice(0, 2).map((suggestion, index) => (
                        <li key={index} style={{ color: '#212529' }}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Literature Review Analysis */}
            {assessment.literature_review_analysis && (
              <div style={{
                border: '1px solid #dee2e6',
                borderRadius: '8px',
                padding: '15px',
                backgroundColor: '#ffffff'
              }}>
                <h4 style={{ color: '#007bff', margin: '0 0 10px 0' }}>📚 Literature Review</h4>
                <p style={{ margin: '0', color: '#495057' }}>
                  Score: <strong>{assessment.literature_review_analysis.score ?? 'N/A'}/100</strong>
                </p>
                {assessment.literature_review_analysis.suggestions && (
                  <div style={{ marginTop: '10px' }}>
                    <strong style={{ color: '#212529' }}>Suggestions:</strong>
                    <ul style={{ margin: '5px 0 0 20px', fontSize: '14px' }}>
                      {assessment.literature_review_analysis.suggestions.slice(0, 2).map((suggestion, index) => (
                        <li key={index} style={{ color: '#212529' }}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Results Analysis */}
            {assessment.results_analysis && (
              <div style={{
                border: '1px solid #dee2e6',
                borderRadius: '8px',
                padding: '15px',
                backgroundColor: '#ffffff'
              }}>
                <h4 style={{ color: '#007bff', margin: '0 0 10px 0' }}>📈 Results</h4>
                <p style={{ margin: '0', color: '#495057' }}>
                  Score: <strong>{assessment.results_analysis.score ?? 'N/A'}/100</strong>
                </p>
                {assessment.results_analysis.suggestions && (
                  <div style={{ marginTop: '10px' }}>
                    <strong style={{ color: '#212529' }}>Suggestions:</strong>
                    <ul style={{ margin: '5px 0 0 20px', fontSize: '14px' }}>
                      {assessment.results_analysis.suggestions.slice(0, 2).map((suggestion, index) => (
                        <li key={index} style={{ color: '#212529' }}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Discussion Analysis */}
            {assessment.discussion_analysis && (
              <div style={{
                border: '1px solid #dee2e6',
                borderRadius: '8px',
                padding: '15px',
                backgroundColor: '#ffffff'
              }}>
                <h4 style={{ color: '#007bff', margin: '0 0 10px 0' }}>💭 Discussion</h4>
                <p style={{ margin: '0', color: '#495057' }}>
                  Score: <strong>{assessment.discussion_analysis.score ?? 'N/A'}/100</strong>
                </p>
                {assessment.discussion_analysis.suggestions && (
                  <div style={{ marginTop: '10px' }}>
                    <strong style={{ color: '#212529' }}>Suggestions:</strong>
                    <ul style={{ margin: '5px 0 0 20px', fontSize: '14px' }}>
                      {assessment.discussion_analysis.suggestions.slice(0, 2).map((suggestion, index) => (
                        <li key={index} style={{ color: '#212529' }}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        )}
      </div>
    );
  };

  if (!user) {
    return (
      <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
        <div style={{
          backgroundColor: '#f8f9fa',
          borderRadius: '12px',
          border: '1px solid #dee2e6',
          padding: '30px',
          textAlign: 'center'
        }}>
          <h2 style={{ color: '#495057', marginBottom: '15px' }}>
            🔐 Research Assessment Requires Sign In
          </h2>
          <p style={{ color: '#6c757d', fontSize: '16px', lineHeight: 1.5 }}>
            Please log in to upload papers and run research assessments.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      <h2 style={{ color: "#f8fafc" }}>AI Research Paper Assessment</h2>
      <p style={{ color: "rgba(226, 232, 255, 0.82)", marginBottom: "20px" }}>
        Upload a research paper to spot gaps and surface improvement ideas.
      </p>

      <div
        style={{
          display: "grid",
          gap: "20px",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          marginBottom: "24px",
        }}
      >
        <div
          style={{
            padding: "30px",
            border: "2px dashed #6f42c1",
            borderRadius: "15px",
            backgroundColor: "#f8f9fa",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "46px", marginBottom: "12px" }}>🗂️</div>
          <h3 style={{ color: "#495057", marginBottom: "10px" }}>Upload Research Paper</h3>
          <p style={{ color: "#6c757d", fontSize: "14px", marginBottom: "18px" }}>
            Drag and drop your PDF here, or click to browse.
          </p>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            id="file-upload-assessment"
            style={{ display: "none" }}
          />
          <label
            htmlFor="file-upload-assessment"
            style={{
              display: "inline-block",
              padding: "12px 24px",
              backgroundColor: "var(--primary)",
              color: "white",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "16px",
              fontWeight: "500",
              transition: "all 0.3s ease",
              border: "none",
              marginBottom: "12px"
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = "#4f46e5"}
            onMouseOut={(e) => e.target.style.backgroundColor = "var(--primary)"}
          >
            📁 Choose PDF File
          </label>
          {sharedFile && (
            <p style={{ color: "#28a745", fontWeight: 600, margin: 0 }}>
              ✅ Selected: {sharedFile.name}
            </p>
          )}
        </div>

        <div
          style={{
            padding: "30px",
            borderRadius: "15px",
            backgroundColor: "#fff",
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.06)",
            border: "1px solid #e9ecef",
          }}
        >
          <h3 style={{ color: "#495057", marginBottom: "12px" }}>Assessment Settings</h3>
          <label
            style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: 600,
              color: "#495057",
            }}
          >
            Choose assessment mode
          </label>
          <select
            value={assessmentType}
            onChange={(e) => setAssessmentType(e.target.value)}
            style={{
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid #ced4da",
              fontSize: "15px",
              width: "100%",
              marginBottom: "16px",
            }}
          >
            <option value="comprehensive">Comprehensive Assessment</option>
            <option value="quick">Quick Analysis</option>
          </select>

          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            <button
              onClick={() => performAssessment(assessmentType)}
              disabled={!sharedFile || sharedLoadingAssessment}
              style={{
                flex: "1 1 180px",
                padding: "14px 18px",
                borderRadius: "10px",
                border: "none",
                backgroundColor: sharedLoadingAssessment ? "#6c757d" : "var(--primary)",
                color: "#fff",
                fontWeight: 600,
                cursor: !sharedFile || sharedLoadingAssessment ? "not-allowed" : "pointer",
                opacity: sharedFile && !sharedLoadingAssessment ? 1 : 0.6,
              }}
            >
              {sharedLoadingAssessment ? "🔄 Analyzing..." : "🚀 Start Assessment"}
            </button>
            <button
              onClick={() => {
                setAssessmentResults(null);
                setError(null);
                setSharedAssessmentData(null);
              }}
              disabled={!assessmentResults}
              style={{
                flex: "1 1 160px",
                padding: "14px 18px",
                borderRadius: "10px",
                border: "none",
                backgroundColor: assessmentResults ? "var(--primary)" : "#6c757d",
                color: "#fff",
                fontWeight: 600,
                cursor: assessmentResults ? "pointer" : "not-allowed",
                opacity: assessmentResults ? 1 : 0.6,
              }}
            >
              🗑️ Clear Results
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div
          style={{
            backgroundColor: "#f8d7da",
            color: "#721c24",
            padding: "15px",
            borderRadius: "8px",
            marginBottom: "20px",
            border: "1px solid #f5c6cb",
          }}
        >
          <strong>❌ Error:</strong> {error}
        </div>
      )}

      {sharedLoadingAssessment && (
        <div style={{ textAlign: "center", padding: "40px" }}>
          <div
            style={{
              display: "inline-block",
              width: "40px",
              height: "40px",
              border: "4px solid #f3f3f3",
              borderTop: "4px solid #6f42c1",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
            }}
          ></div>
          <p style={{ marginTop: "20px", color: "#6c757d", fontSize: "18px" }}>
            🤖 AI is analyzing your research paper...
          </p>
          <p style={{ color: "#6c757d", fontSize: "14px" }}>
            This may take 30-60 seconds depending on paper length.
          </p>
        </div>
      )}

      {assessmentResults && !sharedLoadingAssessment && renderAssessmentResults()}

      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default ResearchAssessment;

