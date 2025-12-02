import React, { useState } from "react";
import apiClient from "./apiClient";

function PdfUploader({
  sharedFile,
  setSharedFile,
  sharedSections,
  setSharedSections,
  sharedSummaries,
  setSharedSummaries,
  sharedEnhancedData,
  setSharedEnhancedData,
  sharedLoadingExtract,
  setSharedLoadingExtract,
  sharedLoadingSummary,
  setSharedLoadingSummary
}) {
  // Use shared state
  const file = sharedFile;
  const sections = sharedSections;
  const summaries = sharedSummaries;
  const enhancedData = sharedEnhancedData;
  const loadingExtract = sharedLoadingExtract;
  const loadingSummary = sharedLoadingSummary;
  
  // Local state for UI
  const [useEnhancedExtraction, setUseEnhancedExtraction] = useState(true);

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    setSharedFile(selectedFile);
    setSharedSections(null);
    setSharedSummaries(null);
    setSharedEnhancedData(null);
    
    // Auto-extract sections when file is selected
    if (selectedFile) {
      await handleAutoExtract(selectedFile);
    }
  };

  // Auto-extract sections when file is uploaded
  const handleAutoExtract = async (fileToProcess) => {
    setSharedLoadingExtract(true);

    const formData = new FormData();
    formData.append("file", fileToProcess);

    try {
      let endpoint = "/extract/upload";
      
      if (useEnhancedExtraction) {
        endpoint = "/enhanced/enhanced-extract";
      }
      
      const res = await apiClient.post(endpoint, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      console.log("Auto-extraction response:", res.data);
      
      if (useEnhancedExtraction && res.data.enhanced_data) {
        setSharedSections(res.data.sections);
        setSharedEnhancedData(res.data.enhanced_data);
      } else {
        setSharedSections(res.data.sections);
        setSharedEnhancedData(null);
      }
    } catch (err) {
      console.error("Auto-extraction error:", err);
      alert("Failed to extract sections from PDF");
    } finally {
      setSharedLoadingExtract(false);
    }
  };

  // Summarize sections
  const handleSummarize = async () => {
    if (!sections) return alert("Extract sections first");
    setSharedLoadingSummary(true);

    try {
      const res = await apiClient.post("/summarize/", sections);
      console.log("Summarization response:", res.data); 
      if (res.data && res.data.summaries) {
        setSharedSummaries(res.data.summaries);
      } else {
        console.error("Unexpected response format:", res.data);
        alert("Unexpected response format from backend");
      }
    } catch (err) {
      console.error("Summarization error:", err.response?.data || err.message);
      alert("Failed to summarize"+ JSON.stringify(err.response?.data || err.message));
    } finally {
      setSharedLoadingSummary(false);
    }
  };


  const renderSummaries = () => {
    if (!summaries) return <p>No summaries available. Please extract sections and summarize first.</p>;
    
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
      <h2>AI Research Paper Summarizer</h2>
      <p style={{ color: "var(--color-text-subtle)", marginBottom: "20px" }}>
        Upload a research paper PDF and get instant AI-powered summaries. 
        Sections are automatically extracted - just upload and summarize!
      </p>

      {/* File Upload Section */}
      <div style={{ 
        padding: "30px", 
        border: "2px dashed #007bff", 
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
            color: "#007bff", 
            marginBottom: "15px" 
          }}>
            📄
          </div>
          <h3 style={{ color: "#495057", marginBottom: "10px" }}>
            Upload Research Paper PDF
          </h3>
          <p style={{ color: "#6c757d", fontSize: "14px", marginBottom: "20px" }}>
            Drag and drop your PDF file here, or click to browse. Sections will be automatically extracted.
          </p>
          
          {/* Hidden file input */}
          <input 
            type="file" 
            accept="application/pdf" 
            onChange={handleFileChange}
            id="file-upload-basic"
            style={{ display: "none" }}
          />
          
          {/* Custom file input button */}
          <label 
            htmlFor="file-upload-basic"
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
              backgroundColor: "#e8f4fd", 
              borderRadius: "8px",
              border: "1px solid #007bff"
            }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "10px" }}>
                <span style={{ fontSize: "20px" }}>📄</span>
                <div>
                  <div style={{ fontWeight: "bold", color: "#007bff" }}>{file.name}</div>
                  <div style={{ fontSize: "12px", color: "#6c757d" }}>
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Status Display */}
        {loadingExtract && (
          <div style={{ 
            marginTop: "20px", 
            padding: "15px", 
            backgroundColor: "#e8f4fd", 
            borderRadius: "8px",
            border: "1px solid #007bff"
          }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "10px" }}>
              <span style={{ fontSize: "20px" }}>⏳</span>
              <span style={{ color: "#007bff", fontWeight: "500" }}>
                Extracting sections from PDF...
              </span>
            </div>
          </div>
        )}
        

        {/* Summarize Button */}
        {sections && (
          <div style={{ marginTop: "20px", textAlign: "center" }}>
            <button 
              onClick={handleSummarize} 
              disabled={loadingSummary}
              style={{
                padding: "15px 30px",
                backgroundColor: loadingSummary ? "#6c757d" : "var(--primary)",
                color: "white",
                border: "none",
                borderRadius: "10px",
                cursor: loadingSummary ? "not-allowed" : "pointer",
                fontSize: "16px",
                fontWeight: "600",
                transition: "all 0.3s ease",
                boxShadow: loadingSummary ? "none" : "0 4px 12px rgba(99, 102, 241, 0.3)"
              }}
              onMouseOver={(e) => {
                if (!loadingSummary) {
                  e.target.style.backgroundColor = "#4f46e5";
                  e.target.style.transform = "translateY(-2px)";
                }
              }}
              onMouseOut={(e) => {
                if (!loadingSummary) {
                  e.target.style.backgroundColor = "var(--primary)";
                  e.target.style.transform = "translateY(0)";
                }
              }}
            >
              {loadingSummary ? (
                <>
                  <span style={{ marginRight: "8px" }}>⏳</span>
                  Generating AI Summaries...
                </>
              ) : (
                <>
                  <span style={{ marginRight: "8px" }}>🤖</span>
                  Generate AI Summaries
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Results Section */}
      {sections && (
        <div>
          {/* AI Summaries Section */}
          <div style={{ minHeight: "400px" }}>
            {renderSummaries()}
          </div>
        </div>
      )}
    </div>
  );
}

export default PdfUploader;
