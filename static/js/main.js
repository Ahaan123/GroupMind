// static/js/main.js

// Function to check if an element is in the viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Function to handle scroll-triggered animations
function handleScrollAnimations() {
    const animatedElements = document.querySelectorAll('.scroll-animate');

    animatedElements.forEach((element) => {
        if (isInViewport(element)) {
            element.classList.add('animate');
        }
    });
}

// Add event listener for scroll
window.addEventListener('scroll', handleScrollAnimations);

// Trigger animations on page load
document.addEventListener('DOMContentLoaded', handleScrollAnimations);

// Handle subreddit analysis
document.addEventListener("DOMContentLoaded", function () {
    const analyzeButton = document.getElementById('analyzeButton');
    const subredditInput = document.getElementById('subredditInput');
    const messageElement = document.getElementById('subredditMessage');

    if (!analyzeButton) {
        console.error("Analyze button not found.");
        return;
    }

    analyzeButton.addEventListener('click', async () => {
        const subreddit = subredditInput.value.trim();
        if (!subreddit) {
            messageElement.textContent = 'Please enter a valid subreddit name.';
            return;
        }

        messageElement.textContent = "Analyzing subreddit...";
        console.log(`Sending request to /analyze with subreddit: ${subreddit}`);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ subreddit }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break; // ✅ Stop processing when response is fully received

                buffer += decoder.decode(value, { stream: true });

                // Process each JSON line separately
                const lines = buffer.split("\n").filter(line => line.trim() !== "");
                buffer = ""; // Clear buffer after processing

                for (const line of lines) {
                    try {
                        const data = JSON.parse(line);
                        console.log("Received:", data);

                        if (data.progress) {
                            messageElement.textContent = data.message;
                        }
                        if (data.response) {
                            messageElement.textContent = `Analysis complete! Start chatting with r/${subreddit} persona.`;
                            initializeChat(subreddit);
                        }
                    } catch (error) {
                        console.warn("Skipping incomplete JSON chunk:", line);
                    }
                }
            }
            console.log("✅ Streaming complete."); // Debugging: Ensure we exit the loop
        } catch (error) {
            console.error('Fetch Error:', error);
            messageElement.textContent = 'Failed to analyze subreddit. Please try again.';
        }
    });
});

// Initialize chat function
function initializeChat(subreddit) {
    const chatWindow = document.getElementById('chatWindow');
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');

    // Ensure chat window is cleared
    chatWindow.innerHTML = `<div class="text-gray-300">Chatbot: Hello! I'm the persona of r/${subreddit}. Ask me anything.</div>`;

    // Remove any previous event listeners before adding a new one
    sendButton.replaceWith(sendButton.cloneNode(true));
    const newSendButton = document.getElementById('sendButton');

    // Handle sending messages
    newSendButton.addEventListener('click', async () => {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        // Display user message
        chatWindow.innerHTML += `<div class="text-right text-blue-300">You: ${userMessage}</div>`;
        chatInput.value = '';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ subreddit, message: userMessage }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            if (data.error) {
                chatWindow.innerHTML += `<div class="text-gray-300">Chatbot: Error - ${data.error}</div>`;
            } else {
                chatWindow.innerHTML += `<div class="text-gray-300">Chatbot: ${data.response}</div>`;
            }
        } catch (error) {
            chatWindow.innerHTML += `<div class="text-gray-300">Chatbot: Failed to send message. Please try again.</div>`;
        }

        // Auto-scroll chat to bottom
        chatWindow.scrollTop = chatWindow.scrollHeight;
    });
}
