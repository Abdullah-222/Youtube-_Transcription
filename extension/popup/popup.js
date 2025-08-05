class YouTubeAIAssistant {
  constructor() {
    this.apiClient = new APIClient();
    this.currentVideo = null;
    this.messages = [];
    this.isLoading = false;
    
    this.initializeEventListeners();
    this.loadCurrentVideo();
  }

  initializeEventListeners() {
    document.getElementById('analyze-btn').addEventListener('click', () => {
      this.analyzeCurrentVideo();
    });

    document.getElementById('send-btn').addEventListener('click', () => {
      this.sendQuestion();
    });

    document.getElementById('clear-btn').addEventListener('click', () => {
      this.clearChat();
    });

    document.getElementById('question-input').addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendQuestion();
      }
    });

    // Auto-resize textarea
    document.getElementById('question-input').addEventListener('input', (e) => {
      e.target.style.height = 'auto';
      e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px';
    });
  }

  async loadCurrentVideo() {
    try {
      // Get current video from background script
      chrome.runtime.sendMessage({action: 'getCurrentVideo'}, (response) => {
        if (response && response.videoId) {
          this.currentVideo = response;
          console.log('Loaded video info:', response);
          this.updateVideoInfo(response);
          this.loadChatHistory();
        } else {
          console.warn('No current video found.');
          this.showError('No YouTube video detected. Please navigate to a YouTube video page.');
        }
      });
    } catch (error) {
      console.error('Error loading video:', error);
      this.showError('Failed to load video information.');
    }
  }

  updateVideoInfo(videoInfo) {
    const videoInfoDiv = document.getElementById('video-info');
    const videoTitle = document.getElementById('video-title');
    const videoUrl = document.getElementById('video-url');

    if (videoInfo.videoTitle) {
      videoTitle.textContent = videoInfo.videoTitle;
    } else {
      videoTitle.textContent = 'Video Title Not Available';
    }
    
    videoUrl.textContent = videoInfo.videoUrl || 'URL Not Available';
    videoInfoDiv.classList.remove('hidden');
  }

  setLoading(loading) {
    this.isLoading = loading;
    const sendBtn = document.getElementById('send-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const input = document.getElementById('question-input');
    
    if (loading) {
      sendBtn.disabled = true;
      analyzeBtn.disabled = true;
      input.disabled = true;
      sendBtn.textContent = 'Sending...';
      analyzeBtn.textContent = 'Analyzing...';
    } else {
      sendBtn.disabled = false;
      analyzeBtn.disabled = false;
      input.disabled = false;
      sendBtn.textContent = 'Send';
      analyzeBtn.textContent = 'Analyze Current Video';
    }
  }

  async analyzeCurrentVideo() {
    if (!this.currentVideo) {
      this.showError('No video detected. Please navigate to a YouTube video.');
      return;
    }

    if (!this.currentVideo.videoUrl) {
      this.showError('Invalid video URL. Please refresh the page and try again.');
      return;
    }

    console.log('Analyzing video:', this.currentVideo);
    this.setLoading(true);
    this.addMessage('assistant', 'Analyzing video content...');
    
    try {
      const response = await this.apiClient.askQuestion(
        this.currentVideo.videoUrl,
        'What is this video about? Please provide a comprehensive summary.'
      );
      
      this.updateLastMessage(response.answer);
      this.saveChatHistory();
    } catch (error) {
      console.error('Analysis error:', error);
      this.updateLastMessage(`Sorry, I encountered an error analyzing the video: ${error.message}`);
    } finally {
      this.setLoading(false);
    }
  }

  async sendQuestion() {
    const input = document.getElementById('question-input');
    const question = input.value.trim();
    
    if (!question || this.isLoading) return;
    
    if (!this.currentVideo) {
      this.showError('No video detected. Please navigate to a YouTube video.');
      return;
    }

    if (!this.currentVideo.videoUrl) {
      this.showError('Invalid video URL. Please refresh the page and try again.');
      return;
    }

    console.log('Sending question:', question, 'for video:', this.currentVideo);
    this.setLoading(true);
    this.addMessage('user', question);
    input.value = '';
    input.style.height = '40px'; // Reset height

    try {
      const response = await this.apiClient.askQuestion(
        this.currentVideo.videoUrl,
        question
      );
      
      this.addMessage('assistant', response.answer);
      this.saveChatHistory();
    } catch (error) {
      console.error('Question error:', error);
      this.addMessage('assistant', `Sorry, I encountered an error processing your question: ${error.message}`);
    } finally {
      this.setLoading(false);
    }
  }

  addMessage(type, content) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    // Handle line breaks and formatting
    const formattedContent = content.replace(/\n/g, '<br>');
    messageDiv.innerHTML = formattedContent;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    this.messages.push({type, content, timestamp: Date.now()});
  }

  updateLastMessage(content) {
    const messages = document.querySelectorAll('.message');
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      const formattedContent = content.replace(/\n/g, '<br>');
      lastMessage.innerHTML = formattedContent;
    }
  }

  clearChat() {
    document.getElementById('messages').innerHTML = '';
    this.messages = [];
    this.saveChatHistory();
  }

  saveChatHistory() {
    if (this.currentVideo?.videoId) {
      chrome.storage.local.set({
        chatHistory: this.messages,
        videoId: this.currentVideo.videoId
      });
    }
  }

  loadChatHistory() {
    if (this.currentVideo?.videoId) {
      chrome.storage.local.get(['chatHistory', 'videoId'], (result) => {
        if (result.videoId === this.currentVideo.videoId && result.chatHistory) {
          this.messages = result.chatHistory;
          this.messages.forEach(msg => {
            this.addMessage(msg.type, msg.content);
          });
        }
      });
    }
  }

  showError(message) {
    this.addMessage('assistant', `⚠️ Error: ${message}`);
  }

  async testConnection() {
    try {
      const health = await this.apiClient.healthCheck();
      console.log('Backend health:', health);
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }
}

// Initialize the assistant when popup opens
document.addEventListener('DOMContentLoaded', () => {
  new YouTubeAIAssistant();
});