import React from 'react';
import { SideBar } from './SideBar';
import { ChatArea } from './ChatArea';

import { mockFiles, mockRoomUuid, mockCsrfToken } from './MockData';

interface ChatUIProps {
  roomUuid: string;
  csrfToken: string;
  files: Array<{
    original_name: string;
    uuid: string;
    updated_at: Date;
  }>;
}

const ChatUI: React.FC<ChatUIProps> = ({ roomUuid, csrfToken, files }) => {

    const handleSendMessage = (message: string) => {
    console.log("Message sent:", message);
  };

  const handleFileUpload = (file: File) => {
    console.log("File uploaded:", file.name);
  };

  const someMessagesArray = [
    "Hello!",
    "How are you?"
  ];
  return (
    <div className="container mx-auto p-4 flex flex-col lg:flex-row h-screen">
      <SideBar roomUuid={roomUuid} files={files} />
      <ChatArea
  roomUuid="some-uuid"
  onSendMessage={handleSendMessage}
  onUploadFile={handleFileUpload}
  messages={someMessagesArray}
/>
    </div>
  );
}

export default ChatUI;
