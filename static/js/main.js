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

    if (!analyzeButton) {
        console.error("Analyze button not found.");
        return;
    }

    analyzeButton.addEventListener('click', async () => {
        console.log("Analyze button clicked!");

        const subredditInput = document.getElementById('subredditInput').value.trim();
        const messageElement = document.getElementById('subredditMessage');

        if (!subredditInput) {
            messageElement.textContent = 'Please enter a valid subreddit name.';
            return;
        }

        console.log(`Sending request to /analyze with subreddit: ${subredditInput}`);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ subreddit: subredditInput }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let result = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                result += decoder.decode(value, { stream: true });

                try {
                    const data = JSON.parse(result);
                    console.log('Received:', data);

                    if (data.progress) {
                        messageElement.textContent = data.message;
                    }

                    if (data.response) {
                        messageElement.textContent = `Analysis complete! Start chatting with the r/${subredditInput} persona.`;
                        initializeChat(data.response);
                    }
                } catch (error) {
                    console.error('JSON Parsing Error:', error);
                }
            }
        } catch (error) {
            console.error('Fetch Error:', error);
            messageElement.textContent = 'Failed to analyze subreddit. Please try again.';
        }
    });
});



// Initialize chat
function initializeChat(chatbotResponse) {
    const chatWindow = document.getElementById('chatWindow');
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');

    // Display initial chatbot response
    chatWindow.innerHTML = `<div class="text-gray-300">Chatbot: ${chatbotResponse}</div>`;

    // Handle sending messages
    sendButton.addEventListener('click', async () => {
        const userMessage = chatInput.value.trim();
        if (userMessage) {
            // Display user message
            chatWindow.innerHTML += `<div class="text-right text-blue-300">You: ${userMessage}</div>`;
            chatInput.value = '';

            // Send message to backend and get chatbot response
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: userMessage }),
                });
                const data = await response.json();
                if (data.error) {
                    chatWindow.innerHTML += `<div class="text-gray-300">Chatbot: Error - ${data.error}</div>`;
                } else {
                    chatWindow.innerHTML += `<div class="text-gray-300">Chatbot: ${data.response}</div>`;
                }
            } catch (error) {
                chatWindow.innerHTML += `<div class="text-gray-300">Chatbot: Failed to send message. Please try again.</div>`;
            }

            chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll to bottom
        }
    });
}

// Simulate chatbot response (replace with actual API call)
async function simulateChatbotResponse(userMessage) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(`You said: "${userMessage}". How can I assist you further?`);
        }, 1000); // Simulate a 1-second delay
    });
}
