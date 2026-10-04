import React, { useState, useEffect } from 'react';
import AppHeader from './components/AppHeader';
import UploadZone from './components/UploadZone';
import DocumentHeader from './components/DocumentHeader';
import MetricsRow from './components/MetricsRow';
import OverviewTab from './components/OverviewTab';
import AnalysisTab from './components/AnalysisTab';
import KeywordsTab from './components/KeywordsTab';
import ChatTab from './components/ChatTab';
import ReportTab from './components/ReportTab';
import ApiKeyModal from './components/ApiKeyModal';

export default function App() {
  const [systemConfig, setSystemConfig] = useState({
    is_api_configured: false,
    model_name: 'gemini-2.5-flash',
  });
  const [activeTab, setActiveTab] = useState('overview');
  const [docData, setDocData] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);
  const [isSendingChat, setIsSendingChat] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Fetch initial system configuration
  const fetchConfig = async () => {
    try {
      const res = await fetch('/api/config');
      if (res.ok) {
        const data = await res.json();
        setSystemConfig(data);
      }
    } catch (err) {
      console.error('Failed to load system config:', err);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  // Handle PDF upload
  const handleFileUpload = async (file) => {
    setIsUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        const errMsg = data.detail?.message || data.detail || 'Upload failed.';
        throw new Error(errMsg);
      }

      setDocData({
        doc_id: data.doc_id,
        filename: data.filename,
        page_count: data.page_count,
        total_words: data.total_words,
        stats: data.stats,
        analysis: null,
        chat_history: [],
      });
      setActiveTab('overview');
    } catch (err) {
      setUploadError(err.message || 'Error processing PDF document.');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle AI Analysis
  const handleTriggerAnalysis = async () => {
    if (!docData?.doc_id) return;

    setIsAnalyzing(true);
    setAnalysisError(null);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: docData.doc_id }),
      });

      const data = await response.json();

      if (!response.ok) {
        const errMsg = data.detail || 'Analysis failed.';
        throw new Error(errMsg);
      }

      setDocData((prev) => ({
        ...prev,
        analysis: data.analysis,
      }));
    } catch (err) {
      setAnalysisError(err.message || 'Failed to analyze paper.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle Q&A Message
  const handleSendMessage = async (question) => {
    if (!docData?.doc_id || !question.trim()) return;

    // Optimistically update conversation
    const updatedHistory = [...(docData.chat_history || []), { role: 'user', content: question }];
    setDocData((prev) => ({ ...prev, chat_history: updatedHistory }));
    setIsSendingChat(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: docData.doc_id, question }),
      });

      const data = await response.json();

      if (!response.ok) {
        const errMsg = data.detail || 'Failed to generate answer.';
        throw new Error(errMsg);
      }

      setDocData((prev) => ({
        ...prev,
        chat_history: data.chat_history,
      }));
    } catch (err) {
      setDocData((prev) => ({
        ...prev,
        chat_history: [
          ...updatedHistory,
          { role: 'assistant', content: `⚠️ Error: ${err.message || 'Failed to get answer.'}` },
        ],
      }));
    } finally {
      setIsSendingChat(false);
    }
  };

  // Clear Chat
  const handleClearChat = async () => {
    if (!docData?.doc_id) return;
    try {
      await fetch('/api/chat/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: docData.doc_id }),
      });
      setDocData((prev) => ({ ...prev, chat_history: [] }));
    } catch (err) {
      console.error('Failed to clear chat:', err);
    }
  };

  // Reset Document (Return to Welcome/Upload Screen)
  const handleResetDoc = async () => {
    try {
      await fetch('/api/reset', { method: 'POST' });
    } catch (err) {
      console.error('Failed to reset:', err);
    }
    setDocData(null);
    setUploadError(null);
    setAnalysisError(null);
    setActiveTab('overview');
  };

  // Update API Key from Modal
  const handleSaveApiKey = async (newKey) => {
    try {
      const response = await fetch('/api/config/api-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: newKey }),
      });
      const data = await response.json();
      if (data.is_configured) {
        setSystemConfig((prev) => ({ ...prev, is_api_configured: true }));
      }
      return data;
    } catch (err) {
      return { success: false, message: err.message || 'Failed to save key.' };
    }
  };

  return (
    <div className="app-shell">
      {/* Top Navigation */}
      <AppHeader
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        docData={docData}
        onResetDoc={handleResetDoc}
        isApiConfigured={systemConfig.is_api_configured}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Main Content Area */}
      <main className="main-content">
        {!docData ? (
          /* Welcome & Upload Screen */
          <UploadZone
            onFileUpload={handleFileUpload}
            isUploading={isUploading}
            uploadError={uploadError}
          />
        ) : (
          /* Document Workspace */
          <div>
            <DocumentHeader
              filename={docData.filename}
              analysis={docData.analysis}
              isAnalyzing={isAnalyzing}
              onAnalyze={handleTriggerAnalysis}
              isApiConfigured={systemConfig.is_api_configured}
              onOpenSettings={() => setIsSettingsOpen(true)}
              analysisError={analysisError}
            />

            <MetricsRow
              pageCount={docData.page_count}
              stats={docData.stats}
              totalWords={docData.total_words}
            />

            {/* Active Workspace View */}
            <div style={{ marginTop: '2rem' }}>
              {activeTab === 'overview' && (
                <OverviewTab
                  analysis={docData.analysis}
                  onTriggerAnalysis={handleTriggerAnalysis}
                  isAnalyzing={isAnalyzing}
                  isApiConfigured={systemConfig.is_api_configured}
                  setActiveTab={setActiveTab}
                />
              )}

              {activeTab === 'analysis' && (
                <AnalysisTab
                  analysis={docData.analysis}
                  onTriggerAnalysis={handleTriggerAnalysis}
                  isAnalyzing={isAnalyzing}
                />
              )}

              {activeTab === 'keywords' && (
                <KeywordsTab
                  analysis={docData.analysis}
                  onTriggerAnalysis={handleTriggerAnalysis}
                  isAnalyzing={isAnalyzing}
                />
              )}

              {activeTab === 'chat' && (
                <ChatTab
                  chatHistory={docData.chat_history || []}
                  onSendMessage={handleSendMessage}
                  onClearChat={handleClearChat}
                  isSending={isSendingChat}
                  isApiConfigured={systemConfig.is_api_configured}
                  onOpenSettings={() => setIsSettingsOpen(true)}
                />
              )}

              {activeTab === 'report' && (
                <ReportTab
                  docId={docData.doc_id}
                  analysis={docData.analysis}
                  filename={docData.filename}
                  onTriggerAnalysis={handleTriggerAnalysis}
                  isAnalyzing={isAnalyzing}
                />
              )}
            </div>
          </div>
        )}
      </main>

      {/* API Key Modal */}
      <ApiKeyModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        isConfigured={systemConfig.is_api_configured}
        onSaveKey={handleSaveApiKey}
      />
    </div>
  );
}
