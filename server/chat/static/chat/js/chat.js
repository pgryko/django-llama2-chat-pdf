// This whole thing is a hack and should be re-written in typescript and react
const room_uuid = roomUuidFromDjango;  // This comes from the Django template context
const getMessagesURI = getMessagesURIFromDjango;
const setMessagesURI = setMessagesURIFromDjango;
const getStreamResponseURI = getStreamResponseURIFromDjango;
const csrfToken = csrfTokenFromDjango;

const chatBox = document.getElementById('chat-box');

// Function to display message sequence
function displayMessages(data) {
    chatBox.innerHTML = '';  // Clear the current chat box

    data.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('flex', 'items-start', 'mb-4');

        const messageContent = document.createElement('div');
        const messageHeader = document.createElement('div');
        messageHeader.innerText = msg.message_type;  // Display the message type as the header
        messageHeader.classList.add('text-xs', 'font-bold', 'mb-1');  // Style the header
        messageContent.appendChild(messageHeader);  // Add the header to the messageContent

        const messageText = document.createElement('div');
        messageText.innerText = msg.content;

        if (msg.message_type === 'CONTEXT') {
            messageText.classList.add('text-xs'); // Adjust the class as per your desired text size
        }

        messageContent.appendChild(messageText);  // Add the message text below the header

        if (msg.message_type === 'USER') {
            messageContent.classList.add('rounded-lg', 'bg-blue-100', 'inline-block', 'p-4');
        } else if (msg.message_type === 'SYSTEM') {
            messageContent.classList.add('rounded-lg', 'bg-red-100', 'inline-block', 'p-4');
        } else if (msg.message_type === 'CONTEXT') {
            messageContent.classList.add('rounded-lg', 'bg-orange-300', 'inline-block', 'p-4');
        } else if (msg.message_type === 'LLM') {
            messageContent.classList.add('rounded-lg', 'bg-gray-300', 'inline-block', 'p-4');
        }

        // You can add more conditions if you have other message types

        messageDiv.appendChild(messageContent);
        chatBox.appendChild(messageDiv);
    });
}


document.addEventListener('DOMContentLoaded', async function () {

    // Load initial messages
    const message_set_response = await fetch(getMessagesURI, {
        method: "GET",
        headers: {
            "Content-Type": 'application/json',
            "X-CSRFToken": csrfToken,
        },
    });

    if (message_set_response.ok) {
        const responseData = await message_set_response.json(); // Await the Promise returned by .json()
        displayMessages(responseData);
    }


    // Send a GET request to the get_messages endpoint to obtain messages
    const sendButton = document.getElementById('send-button');

    // Listen for the send button click, so we can query the server for messages
    sendButton.addEventListener('click', async function () {
        // Get the message from input
        const message = document.getElementById('chat-message').value;

        const RoleEnum = {
            USER: 'USER',
            SYSTEM: 'SYSTEM',
            CONTEXT: 'CONTEXT',
            LLM: 'LLM',
        };

        const message_content = {
            role: RoleEnum.USER,
            content: message
        };


        // Send a POST request to set messages
        const message_set_response = await fetch(setMessagesURI, {
            method: "POST",
            headers: {
                "Content-Type": 'application/json',
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(message_content),
        });

        if (message_set_response.ok) {
            const responseData = await message_set_response.json(); // Await the Promise returned by .json()
            displayMessages(responseData);
            // Clear the input
            document.getElementById('chat-message').value = '';
            // Clear previous LLM response
            document.getElementById('llm-response').innerHTML = '';
        } else {
            console.error("Failed to send message:", response.statusText);
            return;
        }

        // Send a GET request to the stream_chat endpoint to obtain stream
        const response = await fetch(getStreamResponseURI, {
            method: "GET",
            headers: {
                "X-CSRFToken": csrfToken,
            },
        });

        if (response.body) {
            // Get the readable stream from the response body
            const reader = response.body.getReader();

            // Create a new TextDecoder to parse UTF-8 encoded chunks
            const decoder = new TextDecoder("utf-8");

            // Define a function that reads the stream
            const processStream = async () => {
                const llmResponse = document.getElementById('llm-response');

                // Remove any child nodes
                if (llmResponse.firstChild) {
                    llmResponse.firstChild.remove()
                }

                const messageDiv = document.createElement('div');
                messageDiv.classList.add('rounded-lg', 'bg-gray-300', 'inline-block', 'p-4');

                const messageContent = document.createElement('p');

                messageDiv.appendChild(messageContent);
                chatBox.appendChild(messageDiv);

                while (true) {
                    // Read a chunk from the stream
                    const {value, done} = await reader.read();

                    if (done) {
                        break;
                    }

                    // Convert the chunk into a string
                    const chunk = decoder.decode(value, {stream: true});

                    try {
                        // Replace newlines with <br> tags for better formatting
                        messageDiv.innerHTML += chunk.replace(/\n/g, '<br>');

                    } catch (e) {
                        console.error("Failed to parse message:", e);
                    }
                }
            };

            // Start processing the stream
            processStream().catch(err => {
                console.error("Error reading the stream:", err);
            });
        } else {
            console.error("Failed to send message:", response.statusText);
        }

    });
});