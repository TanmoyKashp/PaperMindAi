import React, { useState, useEffect } from 'react';
import AppHeader from './components/layout/AppHeader';
import UploadZone from './components/upload/UploadZone';
import DocumentHeader from './components/analysis/DocumentHeader';
import MetricsRow from './components/analysis/MetricsRow';
import OverviewTab from './components/analysis/OverviewTab';
import AnalysisTab from './components/analysis/AnalysisTab';
import KeywordsTab from './components/analysis/KeywordsTab';
import ChatTab from './components/chat/ChatTab';
import ReportTab from './components/report/ReportTab';
import ApiKeyModal from './components/common/ApiKeyModal';

import {
  fetchSystemConfig,
  uploadPdfDocument,
  analyzeResearchPaper,
  sendChatMessage,
  clearChatHistory,
  resetWorkspaceSession,
  updateApiKey,
} from './services/api';

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

  // Load system configuration
  useEffect(() => {
    let isMounted = true;
    fetchSystemConfig()
      .then((data) => {
        if (isMounted && data) {
          setSystemConfig(data);
        }
      })
      .catch((err) => {
        console.warn('System config load notice:', err.message);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // Handle PDF upload
  const handleFileUpload = async (file) => {
    setIsUploading(true);
    setUploadError(null);

    try {
      const data = await uploadPdfDocument(file);
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
      setUploadError(err.message || 'Error parsing PDF document.');
    } finally {
      setIsUploading(false);
    }
  };

  // Trigger Gemini analysis
  const handleTriggerAnalysis = async () => {
    if (!docData?.doc_id) return;

    setIsAnalyzing(true);
    setAnalysisError(null);

    try {
      const data = await analyzeResearchPaper(docData.doc_id);
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

  // Send message in grounded Q&A
  const handleSendMessage = async (question) => {
    if (!docData?.doc_id || !question.trim()) return;

    const previousHistory = docData.chat_history || [];
    const optimisticHistory = [...previousHistory, { role: 'user', content: question }];
    
    setDocData((prev) => ({ ...prev, chat_history: optimisticHistory }));
    setIsSendingChat(true);

    try {
      const data = await sendChatMessage(docData.doc_id, question);
      setDocData((prev) => ({
        ...prev,
        chat_history: data.chat_history,
      }));
    } catch (err) {
      setDocData((prev) => ({
        ...prev,
        chat_history: [
          ...optimisticHistory,
          {
            role: 'assistant',
            content: `**Error:** ${err.message || 'Failed to generate answer. Please verify your Gemini API key or connection.'}`,
          },
        ],
      }));
    } finally {
      setIsSendingChat(false);
    }
  };

  // Clear Chat History
  const handleClearChat = async () => {
    if (!docData?.doc_id) return;
    try {
      await clearChatHistory(docData.doc_id);
      setDocData((prev) => ({ ...prev, chat_history: [] }));
    } catch (err) {
      console.error('Failed to clear chat:', err);
    }
  };

  // Reset Document / Upload New Paper
  const handleResetDoc = async () => {
    try {
      await resetWorkspaceSession();
    } catch (err) {
      console.warn('Session reset notice:', err);
    }
    setDocData(null);
    setUploadError(null);
    setAnalysisError(null);
    setActiveTab('overview');
  };

  // Save & Verify API Key
  const handleSaveApiKey = async (newKey) => {
    try {
      const data = await updateApiKey(newKey);
      if (data.is_configured) {
        setSystemConfig((prev) => ({ ...prev, is_api_configured: true }));
      }
      return data;
    } catch (err) {
      return { success: false, message: err.message || 'Failed to update API key.' };
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

      {/* Main Workspace Body */}
      <main className="main-content">
        {!docData ? (
          /* Welcome Hero & Upload */
          <UploadZone
            onFileUpload={handleFileUpload}
            isUploading={isUploading}
            uploadError={uploadError}
          />
        ) : (
          /* Document Intelligence Workspace */
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

            {/* Active Feature Tab View */}
            <div style={{ marginTop: '2rem' }}>
              {activeTab === 'overview' && (
                <OverviewTab
                  analysis={docData.analysis}
                  onTriggerAnalysis={handleTriggerAnalysis}
                  isAnalyzing={isAnalyzing}
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

      {/* Settings Modal */}
      <ApiKeyModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        isConfigured={systemConfig.is_api_configured}
        onSaveKey={handleSaveApiKey}
      />
    </div>
  );
}
