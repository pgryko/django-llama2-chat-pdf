import React, { useState } from 'react';

interface ChatAreaProps {
    roomUuid: string;
    onSendMessage: (message: string) => void;
    onUploadFile: (file: File) => void;
    messages: { text: string; timestamp: string; sender: string }[];
}

export const ChatArea: React.FC<ChatAreaProps> = ({ roomUuid, onSendMessage, onUploadFile, messages = [] }) => {
    const [message, setMessage] = useState('');

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            onUploadFile(e.target.files[0]);
        }
    };

    const handleSendMessage = () => {
        onSendMessage(message);
        setMessage(''); // clear the input after sending
    };

    return (
        <div className="w-full lg:w-3/4 bg-white p-4 shadow-lg flex flex-col">
            <h1 className="text-2xl font-semibold mb-4">Chat Room: {roomUuid}</h1>
            <div className="flex-1 overflow-y-auto">
                <div id="chat-box">
                    {messages && messages.map((msg, idx) => (
                        <div key={idx} className="p-2 border-b">
                            <span className="text-gray-500">[{msg.timestamp}] {msg.sender}:</span> {msg.text}
                        </div>
                    ))}
                </div>
                <div id="llm-response">
                    {/* Placeholder: This is where the response stream will be injected */}
                </div>
            </div>
            <div className="border-t p-4">
                <div className="flex flex-col lg:flex-row items-center">
                    <form id="upload-form" encType="multipart/form-data">
                        <label className="flex items-center px-4 py-2 bg-gray-200 text-blue-500 rounded-lg tracking-wide uppercase cursor-pointer hover:bg-blue-500 hover:text-white">
                            <svg className="w-4 h-4 mr-2" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                                <path d="M10 6a1 1 0 01.293.07l6 4a1 1 0 01-1.086 1.682l-4.207-.964l-.293.633a1 1 0 01-1.28.385l-6-3a1 1 0 111.086-1.682l4.207.964l.293-.633a1 1 0 01.707-.464z"></path>
                                <path d="M5 10a1 1 0 010-2h10a1 1 0 010 2H5z"></path>
                            </svg>
                            <span className="mt-2 text-base leading-normal">Select a file</span>
                            <input type="file" name="file" className="hidden" onChange={handleFileUpload} />
                        </label>
                    </form>
                    <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        className="w-full lg:flex-1 mt-2 lg:mt-0 ml-0 lg:ml-4 p-2 rounded border"
                        placeholder="Type your message"
                    />
                    <button onClick={handleSendMessage} className="mt-2 lg:mt-0 w-full lg:w-auto ml-0 lg:ml-4 px-6 py-2 text-white bg-blue-500 rounded hover:bg-blue-600">
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
};
