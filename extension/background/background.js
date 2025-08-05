// Handle all message communications
let currentVideo = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getCurrentVideo') {
    // First try to use cached video info
    if (currentVideo && currentVideo.videoId) {
      sendResponse(currentVideo);
      return false;
    }

    // Query the active tab for video information
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      if (tabs[0] && tabs[0].url && tabs[0].url.includes('youtube.com')) {
        chrome.tabs.sendMessage(tabs[0].id, {action: 'getVideoInfo'}, (response) => {
          if (chrome.runtime.lastError) {
            console.error('Error getting video info:', chrome.runtime.lastError);
            sendResponse(null);
            return;
          }
          
          if (response && response.videoId) {
            currentVideo = response;
            chrome.storage.local.set({ currentVideo: response });
            sendResponse(response);
          } else {
            sendResponse(null);
          }
        });
      } else {
        sendResponse(null);
      }
    });
    return true; // Keep message channel open for async response
  }
  
  else if (request.action === 'videoChanged') {
    // Update current video info
    if (request.videoInfo && request.videoInfo.videoId) {
      currentVideo = request.videoInfo;
      chrome.storage.local.set({ currentVideo: request.videoInfo });
      console.log('Video updated in background:', request.videoInfo);
    }
  }
});

// Initialize from storage on startup
chrome.storage.local.get(['currentVideo'], (result) => {
  if (result.currentVideo) {
    currentVideo = result.currentVideo;
    console.log('Loaded video from storage:', currentVideo);
  }
});

// Handle tab updates to refresh video info
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.includes('youtube.com/watch')) {
    // Clear current video to force refresh
    currentVideo = null;
    chrome.storage.local.remove(['currentVideo']);
  }
});

// Handle tab activation to refresh video info
chrome.tabs.onActivated.addListener((activeInfo) => {
  chrome.tabs.get(activeInfo.tabId, (tab) => {
    if (tab.url && tab.url.includes('youtube.com/watch')) {
      // Clear current video to force refresh
      currentVideo = null;
      chrome.storage.local.remove(['currentVideo']);
    }
  });
});