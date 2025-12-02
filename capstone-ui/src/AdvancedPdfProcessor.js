import React, { useState } from "react";
import apiClient from "./apiClient";
import { useAuth } from "./context/AuthContext";

function AdvancedPdfProcessor({
  sharedFile,
  setSharedFile,
  sharedProcessingData,
  setSharedProcessingData,
  sharedLoadingAdvanced,
  setSharedLoadingAdvanced,
  sharedSummaries,
  setSharedSummaries,
  sharedLoadingSummary,
  setSharedLoadingSummary
}) {
  const { user } = useAuth();
  // Use shared state
  const file = sharedFile;
  const processingData = sharedProcessingData;
  const loading = sharedLoadingAdvanced;
  const summaries = sharedSummaries;
  const loadingSummary = sharedLoadingSummary;
  
  if (!user) {
    return (
      <div
        style={{
          padding: "40px",
          maxWidth: "800px",
          margin: "0 auto",
          textAlign: "center",
          backgroundColor: "#f8f9fa",
          borderRadius: "12px",
          border: "1px solid #e0e0e0",
        }}
      >
        <h3 style={{ color: "#495057" }}>Advanced Processor</h3>
        <p style={{ color: "#6c757d", marginTop: "10px" }}>
          Please log in to access the advanced PDF processing features.
        </p>
      </div>
    );
  }

  // Local state for UI
  const [activeTab, setActiveTab] = useState("overview");

  const handleFileChange = (e) => {
    setSharedFile(e.target.files[0]);
    setSharedProcessingData(null);
  };

  const handleAdvancedExtract = async () => {
    if (!file) return alert("Please select a PDF file first");
    
    setSharedLoadingAdvanced(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Step 1: Extract advanced features
      const response = await apiClient.post(
        "/advanced/advanced-extract",
        formData
      );
      console.log("Advanced extraction response:", response.data.data);
      console.log("Figures/Tables found:", response.data.data?.figures_tables);
      setSharedProcessingData(response.data.data);
      
      // Step 2: Automatically generate summaries
      if (response.data.data?.sections) {
        setSharedLoadingSummary(true);
        try {
          const summaryResponse = await apiClient.post(
            "/summarize/",
            response.data.data.sections
          );
          if (summaryResponse.data && summaryResponse.data.summaries) {
            setSharedSummaries(summaryResponse.data.summaries);
          }
        } catch (summaryError) {
          console.error("Summary generation error:", summaryError);
          // Don't show error to user - summaries are optional
        } finally {
          setSharedLoadingSummary(false);
        }
      }
    } catch (error) {
      console.error("Advanced extraction error:", error);
      alert("Error processing PDF. Please try again.");
    } finally {
      setSharedLoadingAdvanced(false);
    }
  };

  // Generate AI summaries
  const handleGenerateSummaries = async () => {
    if (!processingData?.sections) return alert("Please extract advanced features first");
    
    setSharedLoadingSummary(true);

    try {
      const res = await apiClient.post("/summarize/", processingData.sections);
      console.log("Summarization response:", res.data); 
      if (res.data && res.data.summaries) {
        setSharedSummaries(res.data.summaries);
      } else {
        console.error("Unexpected response format:", res.data);
        alert("Unexpected response format from backend");
      }
    } catch (err) {
      console.error("Summarization error:", err.response?.data || err.message);
      alert("Failed to summarize: " + JSON.stringify(err.response?.data || err.message));
    } finally {
      setSharedLoadingSummary(false);
    }
  };

  const renderOverview = () => {
    if (!processingData) return null;
    
    const { metadata, sections } = processingData;
    
    return (
      <div>
        <h3>Document Overview</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px", marginBottom: "20px" }}>
          <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "8px", backgroundColor: "#f9f9f9" }}>
            <h4 style={{ color: "#1e293b", margin: "0 0 10px 0" }}>Pages</h4>
            <p style={{ fontSize: "24px", margin: "0", color: "#2c3e50" }}>{metadata.total_pages}</p>
          </div>
          <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "8px", backgroundColor: "#e8f4fd" }}>
            <h4 style={{ color: "#1e293b", margin: "0 0 10px 0" }}>Citations</h4>
            <p style={{ fontSize: "24px", margin: "0", color: "#2980b9" }}>{metadata.total_citations}</p>
          </div>
          <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "8px", backgroundColor: "#e8f8f5" }}>
            <h4 style={{ color: "#1e293b", margin: "0 0 10px 0" }}>Figures</h4>
            <p style={{ fontSize: "24px", margin: "0", color: "#27ae60" }}>{metadata.total_figures}</p>
          </div>
          <div style={{ padding: "15px", border: "1px solid #ddd", borderRadius: "8px", backgroundColor: "#fef9e7" }}>
            <h4 style={{ color: "#1e293b", margin: "0 0 10px 0" }}>Tables</h4>
            <p style={{ fontSize: "24px", margin: "0", color: "#f39c12" }}>{metadata.total_tables}</p>
          </div>
        </div>

        <h3>Document Sections</h3>
        <div style={{ marginBottom: "20px" }}>
          <div style={{ marginBottom: "15px" }}>
            <h4>Abstract</h4>
            <div style={{ padding: "10px", backgroundColor: "#f8f9fa", borderRadius: "5px", borderLeft: "4px solid #007bff", color: "#1e293b" }}>
              {sections.abstract || "No abstract found"}
            </div>
            {sections.abstract && file && (
              <button
                onClick={() => {
                  const fileUrl = URL.createObjectURL(file);
                  window.open(fileUrl, '_blank');
                }}
                style={{
                  marginTop: "8px",
                  padding: "6px 12px",
                  backgroundColor: "var(--primary)",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                  fontSize: "14px"
                }}
              >
                📄 Read More
              </button>
            )}
          </div>
          <div style={{ marginBottom: "15px" }}>
            <h4>Introduction</h4>
            <div style={{ padding: "10px", backgroundColor: "#f8f9fa", borderRadius: "5px", borderLeft: "4px solid #28a745", color: "#1e293b" }}>
              {sections.introduction || "No introduction found"}
            </div>
            {sections.introduction && file && (
              <button
                onClick={() => {
                  const fileUrl = URL.createObjectURL(file);
                  window.open(fileUrl, '_blank');
                }}
                style={{
                  marginTop: "8px",
                  padding: "6px 12px",
                  backgroundColor: "var(--primary)",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                  fontSize: "14px"
                }}
              >
                📄 Read More
              </button>
            )}
          </div>
          <div style={{ marginBottom: "15px" }}>
            <h4>Main Body</h4>
            <div style={{ padding: "10px", backgroundColor: "#f8f9fa", borderRadius: "5px", borderLeft: "4px solid #ffc107", color: "#1e293b" }}>
              {sections.main_body ? sections.main_body.substring(0, 500) + "..." : "No main body found"}
            </div>
            {sections.main_body && file && (
              <button
                onClick={() => {
                  const fileUrl = URL.createObjectURL(file);
                  window.open(fileUrl, '_blank');
                }}
                style={{
                  marginTop: "8px",
                  padding: "6px 12px",
                  backgroundColor: "var(--primary)",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                  fontSize: "14px",
                  fontWeight: "500"
                }}
              >
                📄 Read More
              </button>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderCitations = () => {
    if (!processingData?.citations) return <p>No citations found</p>;
    
    return (
      <div>
        <h3>Citations ({processingData.citations.length})</h3>
        <div style={{ maxHeight: "400px", overflowY: "auto" }}>
          {processingData.citations.map((citation, index) => (
            <div key={index} style={{ 
              padding: "10px", 
              marginBottom: "10px", 
              border: "1px solid #ddd", 
              borderRadius: "5px",
              backgroundColor: "#f8f9fa",
              color: "#1e293b"
            }}>
              <div style={{ fontWeight: "bold", color: "#1e293b", marginBottom: "8px" }}>
                {citation.citation_type.toUpperCase()}
              </div>
              <div style={{ marginTop: "5px", color: "#1e293b" }}>
                <strong style={{ color: "#1e293b" }}>Text:</strong> {citation.text}
              </div>
              {citation.authors && citation.authors.length > 0 && (
                <div style={{ color: "#1e293b" }}><strong style={{ color: "#1e293b" }}>Authors:</strong> {citation.authors.join(", ")}</div>
              )}
              {citation.year && (
                <div style={{ color: "#1e293b" }}><strong style={{ color: "#1e293b" }}>Year:</strong> {citation.year}</div>
              )}
              {citation.citation_type === "numbered" && citation.reference_numbers?.length > 0 && (
                <div style={{ marginTop: "8px" }}>
                  <div style={{ fontWeight: 500, color: "#0d6efd" }}>
                    Referenced Sources:
                  </div>
                  <ul style={{ paddingLeft: "18px", marginTop: "4px", marginBottom: "0" }}>
                    {citation.reference_numbers.map((num, idx) => (
                      <li key={idx} style={{ marginBottom: "4px", color: "#1e293b" }}>
                        <strong style={{ color: "#1e293b" }}>[{num}]</strong>{" "}
                        {citation.resolved_references?.[idx] || (
                          <span style={{ color: "#1e293b" }}>
                            Reference {num} (details not captured)
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderFiguresTables = () => {
    if (!processingData?.figures_tables) return <p>No figures or tables found</p>;
    
    console.log("Rendering figures/tables:", processingData.figures_tables);
    console.log("Sample item:", processingData.figures_tables[0]);
    
    return (
      <div>
        <h3>Figures & Tables ({processingData.figures_tables.length})</h3>
        <div style={{ maxHeight: "600px", overflowY: "auto" }}>
          {processingData.figures_tables.map((item, index) => (
            <div key={index} style={{ 
              padding: "20px", 
              marginBottom: "20px", 
              border: "1px solid #ddd", 
              borderRadius: "8px",
              backgroundColor: item.content_type === "figure" ? "#e8f4fd" : "#fef9e7",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
            }}>
              <div style={{ 
                fontWeight: "bold", 
                color: item.content_type === "figure" ? "#2980b9" : "#f39c12",
                fontSize: "18px",
                marginBottom: "15px"
              }}>
                📊 {item.label} (Page {item.page_number})
              </div>
              
              {item.image_base64 && (
                <div style={{ 
                  marginBottom: "12px",
                  padding: "12px",
                  backgroundColor: "#fff",
                  borderRadius: "5px",
                  border: "1px solid #dee2e6",
                  textAlign: "center"
                }}>
                  <img 
                    src={`data:image/png;base64,${item.image_base64}`} 
                    alt={item.label}
                    style={{
                      maxWidth: "100%",
                      height: "auto",
                      borderRadius: "5px",
                      boxShadow: "0 2px 8px rgba(0,0,0,0.15)"
                    }}
                  />
                </div>
              )}
              
              {item.ai_explanation && (
                <div style={{ 
                  padding: "12px",
                  backgroundColor: "#fff",
                  borderRadius: "5px",
                  border: "1px solid #dee2e6"
                }}>
                  <div style={{ fontWeight: "600", marginBottom: "6px", color: "#28a745", display: "flex", alignItems: "center", gap: "6px" }}>
                    <span>🤖</span>
                    <span>AI Explanation:</span>
                  </div>
                  <div style={{ fontSize: "14px", color: "#495057", lineHeight: "1.6" }}>
                    {item.ai_explanation}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderKeywords = () => {
    if (!processingData?.keywords) return <p>No keywords found</p>;
    
    return (
      <div>
        <h3>Keywords ({processingData.keywords.length})</h3>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
          {processingData.keywords.map((keyword, index) => (
            <span key={index} style={{
              padding: "6px 12px",
              backgroundColor: "#e9ecef",
              borderRadius: "20px",
              fontSize: "14px",
              border: "1px solid #dee2e6",
              color: "#1e293b"
            }}>
              {keyword}
            </span>
          ))}
        </div>
      </div>
    );
  };

  const renderSummaries = () => {
    if (!summaries) {
      return (
        <div style={{ textAlign: "center", padding: "40px" }}>
          <div style={{ fontSize: "48px", color: "#6c757d", marginBottom: "20px" }}>🤖</div>
          <h3 style={{ color: "#495057", marginBottom: "15px" }}>AI Summaries</h3>
          <p style={{ color: "#6c757d", marginBottom: "20px" }}>
            AI summaries are automatically generated when you extract advanced features
          </p>
          {loadingSummary && (
            <div style={{ 
              padding: "15px", 
              backgroundColor: "#e8f4fd", 
              borderRadius: "8px",
              border: "1px solid #007bff",
              display: "inline-block"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ fontSize: "20px" }}>⏳</span>
                <span style={{ color: "#007bff", fontWeight: "500" }}>
                  Generating AI Summaries...
                </span>
              </div>
            </div>
          )}
        </div>
      );
    }
    
    return (
      <div>
        <h3>AI-Generated Summaries</h3>
        <div style={{ marginBottom: "20px" }}>
          <div style={{ marginBottom: "20px" }}>
            <h4>Abstract Summary</h4>
            <div style={{ 
              padding: "15px", 
              backgroundColor: "#e8f4fd", 
              borderRadius: "8px", 
              borderLeft: "4px solid #007bff",
              lineHeight: "1.6",
              color: "#1e293b"
            }}>
              {summaries.abstract}
            </div>
          </div>
          <div style={{ marginBottom: "20px" }}>
            <h4>Introduction Summary</h4>
            <div style={{ 
              padding: "15px", 
              backgroundColor: "#e8f8f5", 
              borderRadius: "8px", 
              borderLeft: "4px solid #28a745",
              lineHeight: "1.6",
              color: "#1e293b"
            }}>
              {summaries.introduction}
            </div>
          </div>
          <div style={{ marginBottom: "20px" }}>
            <h4>Main Body Summary</h4>
            <div style={{ 
              padding: "15px", 
              backgroundColor: "#fef9e7", 
              borderRadius: "8px", 
              borderLeft: "4px solid #ffc107",
              lineHeight: "1.6",
              color: "#1e293b"
            }}>
              {summaries.main_body}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      <h2>Advanced PDF Processor</h2>
      <p style={{ color: "rgba(226, 232, 255, 0.82)", marginBottom: "20px" }}>
        Upload a research paper PDF to extract citations, figures, tables, mathematical content, keywords, and generate AI summaries - all in one seamless process.
      </p>

      {/* File Upload Section */}
      <div style={{ 
        padding: "30px", 
        border: "2px dashed #6f42c1", 
        borderRadius: "15px", 
        backgroundColor: "#f8f9fa",
        marginBottom: "20px",
        textAlign: "center",
        transition: "all 0.3s ease"
      }}>
        {/* Upload Area */}
        <div style={{ marginBottom: "20px" }}>
          <div style={{ 
            fontSize: "48px", 
            color: "#6f42c1", 
            marginBottom: "15px" 
          }}>
            🔬
          </div>
          <h3 style={{ color: "#495057", marginBottom: "10px" }}>
            Upload Research Paper for Advanced Analysis
          </h3>
          <p style={{ color: "#6c757d", fontSize: "14px", marginBottom: "20px" }}>
            Extract citations, figures, tables, mathematical content, keywords, and generate AI summaries
          </p>
          
          {/* Hidden file input */}
          <input 
            type="file" 
            accept="application/pdf" 
            onChange={handleFileChange}
            id="file-upload-advanced"
            style={{ display: "none" }}
          />
          
          {/* Custom file input button */}
          <label 
            htmlFor="file-upload-advanced"
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
              marginBottom: "15px"
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = "#4f46e5"}
            onMouseOut={(e) => e.target.style.backgroundColor = "var(--primary)"}
          >
            📁 Choose PDF File
          </label>
          
          {/* File info display */}
          {file && (
            <div style={{ 
              marginTop: "15px", 
              padding: "10px 15px", 
              backgroundColor: "#f3e8ff", 
              borderRadius: "8px",
              border: "1px solid #6f42c1"
            }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "10px" }}>
                <span style={{ fontSize: "20px" }}>📄</span>
                <div>
                  <div style={{ fontWeight: "bold", color: "#6f42c1" }}>{file.name}</div>
                  <div style={{ fontSize: "12px", color: "#6c757d" }}>
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Action Button */}
        <div>
          <button 
            onClick={handleAdvancedExtract} 
            disabled={loading || !file}
            style={{
              padding: "15px 30px",
              backgroundColor: loading ? "#6c757d" : "var(--primary)",
              color: "white",
              border: "none",
              borderRadius: "10px",
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: "16px",
              fontWeight: "600",
              transition: "all 0.3s ease",
              boxShadow: loading ? "none" : "0 4px 12px rgba(99, 102, 241, 0.3)"
            }}
            onMouseOver={(e) => {
              if (!loading && file) {
                e.target.style.backgroundColor = "#4f46e5";
                e.target.style.transform = "translateY(-2px)";
              }
            }}
            onMouseOut={(e) => {
              if (!loading && file) {
                e.target.style.backgroundColor = "var(--primary)";
                e.target.style.transform = "translateY(0)";
              }
            }}
          >
            {loading ? (
              <>
                <span style={{ marginRight: "8px" }}>⏳</span>
                Processing Advanced Features & Summaries...
              </>
            ) : (
              <>
                <span style={{ marginRight: "8px" }}>🔬</span>
                Extract Advanced Features & Generate Summaries
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      {processingData && (
        <div>
          {/* Tab Navigation */}
          <div style={{ 
            borderBottom: "1px solid #ddd", 
            marginBottom: "20px",
            display: "flex",
            gap: "0"
          }}>
            {[
              { id: "overview", label: "Overview" },
              { id: "summaries", label: "AI Summaries" },
              { id: "citations", label: "Citations" },
              { id: "figures", label: "Figures & Tables" },
              { id: "keywords", label: "Keywords" }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: "10px 20px",
                  border: "none",
                  backgroundColor: activeTab === tab.id ? "var(--primary)" : "transparent",
                  color: activeTab === tab.id ? "white" : "var(--primary)",
                  cursor: "pointer",
                  borderTopLeftRadius: "5px",
                  borderTopRightRadius: "5px"
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div style={{ minHeight: "400px" }}>
            {activeTab === "overview" && renderOverview()}
            {activeTab === "summaries" && renderSummaries()}
            {activeTab === "citations" && renderCitations()}
            {activeTab === "figures" && renderFiguresTables()}
            {activeTab === "keywords" && renderKeywords()}
          </div>
        </div>
      )}
    </div>
  );
}

export default AdvancedPdfProcessor;
