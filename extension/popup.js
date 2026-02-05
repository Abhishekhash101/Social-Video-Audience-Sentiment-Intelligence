document.getElementById("analyzeBtn").addEventListener("click", async () => {
    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = "Scraping comments... (Please scroll down to load comments first!)";

    // 1. Get the current active tab
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // 2. Execute script to scrape comments from the DOM
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: scrapeComments,
    }, async (results) => {
        const comments = results[0].result;

        if (!comments || comments.length === 0) {
            resultDiv.innerHTML = "<p style='color:red'>No comments found. Scroll down the video page to load them and try again.</p>";
            return;
        }

        resultDiv.innerHTML = `Found ${comments.length} comments. Analyzing...`;

        let positiveCount = 0;
        let negativeCount = 0;

        // 3. Send each comment to your Flask API
        // We use Promise.all to send them in parallel for speed
        const promises = comments.slice(0, 10).map(async (commentText) => {
            try {
                const response = await fetch("https://social-video-audience-sentiment.onrender.com/predict", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ comment: commentText })
                });
                const data = await response.json();
                return data.sentiment;
            } catch (error) {
                console.error("API Error:", error);
                return null;
            }
        });

        const sentiments = await Promise.all(promises);

        // 4. Calculate Stats
        sentiments.forEach(s => {
            if (s === "Positive") positiveCount++;
            else if (s === "Negative") negativeCount++;
        });

        const total = positiveCount + negativeCount;
        const posPct = total === 0 ? 0 : Math.round((positiveCount / total) * 100);

        // 5. Display Final Result
        resultDiv.innerHTML = `
            <div style="margin-top:15px; padding:10px; background:#f0f0f0; border-radius:5px;">
                <h3 style="text-align:center; margin:0 0 10px 0;">Overall Vibe</h3>
                <div class="stat"><strong>Positive:</strong> <span>${positiveCount}</span></div>
                <div class="stat"><strong>Negative:</strong> <span>${negativeCount}</span></div>
                <hr>
                <div style="text-align:center; font-size:18px; color:${posPct > 50 ? 'green' : 'red'}">
                    <strong>${posPct}% Positive</strong>
                </div>
            </div>
        `;
    });
});

// This function runs INSIDE the YouTube page, not the popup
function scrapeComments() {
    // Selector for YouTube comments (polymer)
    const commentElements = document.querySelectorAll("ytd-comment-thread-renderer #content-text");
    const comments = [];
    
    // Grab the text from the top 10 visible comments
    commentElements.forEach((el, index) => {
        if (index < 10) { // Limit to 10 for speed
            comments.push(el.innerText);
        }
    });
    
    return comments;
}