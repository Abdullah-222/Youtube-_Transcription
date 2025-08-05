class APIClient {
  constructor() {
    this.baseURL = "http://localhost:8000"; // Your deployed backend
  }

  async askQuestion(videoUrl, question) {
    try {
      // Validate inputs
      if (!videoUrl || !question) {
        throw new Error('Video URL and question are required');
      }

      // Clean the video URL (remove any extra parameters that might cause issues)
      const cleanUrl = this.cleanVideoUrl(videoUrl);
      
      console.log('Sending request to backend:', {
        video_url: cleanUrl,
        question: question
      });

      const response = await fetch(`${this.baseURL}/extension/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_url: cleanUrl,
          question: question
        })
      });

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        
        // Try to get more detailed error information
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage += ` - ${errorData.detail}`;
          }
        } catch (e) {
          // If we can't parse the error response, use the status text
          errorMessage += ` - ${response.statusText}`;
        }
        
        if (response.status === 404) {
          throw new Error('API server not found. Make sure your backend server is running at ' + this.baseURL);
        } else if (response.status === 422) {
          throw new Error(`Invalid request: ${errorMessage}. Please check the video URL format.`);
        }
        
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Backend response:', result);
      return result;
    } catch (error) {
      console.error('API Error:', error);
      if (error.message.includes('Failed to fetch')) {
        throw new Error('Cannot connect to API server. Please make sure your backend is running at ' + this.baseURL);
      }
      throw error;
    }
  }

  cleanVideoUrl(url) {
    // Remove any extra parameters that might cause validation issues
    // Keep only the essential video ID part
    try {
      const urlObj = new URL(url);
      
      // Handle different YouTube URL formats
      if (urlObj.hostname.includes('youtube.com')) {
        const videoId = urlObj.searchParams.get('v');
        if (videoId) {
          return `https://www.youtube.com/watch?v=${videoId}`;
        }
      } else if (urlObj.hostname.includes('youtu.be')) {
        const videoId = urlObj.pathname.substring(1); // Remove leading slash
        if (videoId) {
          return `https://www.youtube.com/watch?v=${videoId}`;
        }
      }
      
      // If we can't parse it properly, return the original URL
      return url;
    } catch (e) {
      // If URL parsing fails, return the original URL
      return url;
    }
  }

  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}