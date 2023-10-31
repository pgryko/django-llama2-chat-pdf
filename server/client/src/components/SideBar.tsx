import React from 'react';

interface SideBarProps {
  roomUuid: string;
  files: Array<{
    original_name: string;
    uuid: string;
    updated_at: Date;
  }>;
}

export const SideBar: React.FC<SideBarProps> = ({ roomUuid, files }) => {
  return (
    <div className="w-full lg:w-1/4 bg-white p-4 shadow-lg overflow-y-auto mb-4 lg:mb-0" style={{ maxHeight: "calc(100vh - 2rem)" }}>
      <a href={`/chatroom_list`}>
        <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded focus:outline-none mb-4">Go Back</button>
      </a>
      <h1 className="text-lg font-semibold mb-4">Uploaded Files</h1>
      {files.map(file => (
        <div key={file.uuid} className="p-4 bg-gray-100 rounded-lg shadow hover:bg-gray-200">
          {/* Dummy link for the sake of this example */}
          <a href={`/file_view/${roomUuid}/${file.uuid}`} className="flex justify-between items-center w-full p-2 rounded-lg">
            <div className="flex items-center">
              <div className="ml-4 text-gray-700">
                <p className="text-s font-medium">
                  <span className="text-gray-500">File Name:</span>
                  {file.original_name}
                </p>
                <p className="text-s font-small">
                  <span className="text-gray-500">File ID:</span>
                  {file.uuid}
                </p>
                <p className="text-xs text-gray-400">{file.updated_at.toLocaleDateString()}</p>
              </div>
            </div>
            {/* Dummy form for the sake of this example */}
            <form method="post" action={`/file_delete/${roomUuid}/${file.uuid}`}>
              <button type="submit" className="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded focus:outline-none">X</button>
            </form>
          </a>
        </div>
      ))}
    </div>
  );
}
