// Extract video information from YouTube page
class YouTubeVideoExtractor {
  constructor() {
    this.videoId = this.extractVideoId();
    this.videoTitle = this.extractVideoTitle();
    this.videoUrl = this.buildVideoUrl();
    this.channelName = this.extractChannelName();
  }

  extractVideoId() {
    // Handle different YouTube URL formats
    const url = window.location.href;
    let videoId = null;
    
    // Standard watch URLs
    const watchMatch = url.match(/[?&]v=([^&]+)/);
    if (watchMatch) {
      videoId = watchMatch[1];
    }
    
    // Short URLs (youtu.be)
    const shortMatch = url.match(/youtu\.be\/([^?]+)/);
    if (shortMatch) {
      videoId = shortMatch[1];
    }
    
    // Embedded URLs
    const embedMatch = url.match(/embed\/([^?]+)/);
    if (embedMatch) {
      videoId = embedMatch[1];
    }
    
    console.log(`Extracted video ID: ${videoId}`);
    return videoId;
  }

  buildVideoUrl() {
    // Always return a clean, standard YouTube watch URL
    if (this.videoId) {
      return `https://www.youtube.com/watch?v=${this.videoId}`;
    }
    return window.location.href; // Fallback to current URL
  }

  extractVideoTitle() {
    // Try multiple selectors for video title
    const selectors = [
      'h1.ytd-video-primary-info-renderer',
      'h1.ytd-watch-metadata',
      'h1.title',
      'h1[class*="title"]',
      'ytd-video-primary-info-renderer h1',
      'ytd-watch-metadata h1'
    ];
    
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        const title = element.textContent.trim();
        if (title && title.length > 0) {
          return title;
        }
      }
    }
    
    // Fallback: try to get from meta tags
    const metaTitle = document.querySelector('meta[property="og:title"]');
    if (metaTitle && metaTitle.content) {
      return metaTitle.content;
    }
    
    return 'Unknown Title';
  }

  extractChannelName() {
    // Try multiple selectors for channel name
    const selectors = [
      'ytd-channel-name yt-formatted-string.ytd-video-owner-renderer',
      'ytd-video-owner-renderer yt-formatted-string',
      'a[href*="/channel/"]',
      'a[href*="/c/"]',
      'a[href*="/user/"]',
      'span[class*="channel"]'
    ];
    
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        const channelName = element.textContent.trim();
        if (channelName && channelName.length > 0) {
          return channelName;
        }
      }
    }
    
    return 'Unknown Channel';
  }

  getVideoInfo() {
    return {
      videoId: this.videoId,
      videoTitle: this.videoTitle,
      videoUrl: this.videoUrl,
      channelName: this.channelName,
      timestamp: Date.now()
    };
  }

  isValidVideo() {
    return this.videoId && this.videoId.length > 0;
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getVideoInfo') {
    const extractor = new YouTubeVideoExtractor();
    const videoInfo = extractor.getVideoInfo();
    console.log('Sending video info to popup:', videoInfo);
    sendResponse(videoInfo);
  }
});

// Notify background script when video changes
let currentVideoId = null;
let checkInterval = null;

function checkVideoChange() {
  const extractor = new YouTubeVideoExtractor();
  
  if (extractor.isValidVideo() && extractor.videoId !== currentVideoId) {
    currentVideoId = extractor.videoId;
    console.log('Video changed:', extractor.getVideoInfo());
    
    chrome.runtime.sendMessage({
      action: 'videoChanged',
      videoInfo: extractor.getVideoInfo()
    });
  }
}

// Start monitoring for video changes
function startVideoMonitoring() {
  if (checkInterval) {
    clearInterval(checkInterval);
  }
  
  checkInterval = setInterval(checkVideoChange, 2000);
  
  // Also check immediately
  checkVideoChange();
}

// Stop monitoring
function stopVideoMonitoring() {
  if (checkInterval) {
    clearInterval(checkInterval);
    checkInterval = null;
  }
}

// Start monitoring when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startVideoMonitoring);
} else {
  startVideoMonitoring();
}

// Handle YouTube's SPA navigation
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    console.log('URL changed, restarting video monitoring');
    startVideoMonitoring();
  }
}).observe(document, {subtree: true, childList: true});

// Clean up when page unloads
window.addEventListener('beforeunload', stopVideoMonitoring);