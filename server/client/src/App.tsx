import React from 'react';
import ChatUI from './components/ChatUI';

// For the sake of example, let's have mock data
const mockData = {
  roomUuid: "123456",
  csrfToken: "csrfToken123",
  files: [
    {
      original_name: "example.txt",
      uuid: "abcdef",
      updated_at: new Date()
    },
    //... more files
  ]
}

const App: React.FC = () => {
  return (
    <div className="bg-gray-200">
      <ChatUI roomUuid={mockData.roomUuid} csrfToken={mockData.csrfToken} files={mockData.files} />
    </div>
  );
}

export default App;
