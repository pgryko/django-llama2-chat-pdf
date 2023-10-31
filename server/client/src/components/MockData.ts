// MockData.ts
const mockFiles = [
  {
    original_name: "file1.txt",
    uuid: "12345-abcde",
    updated_at: new Date("2023-11-01T10:00:00Z")
  },
  {
    original_name: "image1.jpg",
    uuid: "67890-fghij",
    updated_at: new Date("2023-11-01T11:00:00Z")
  }
];

const mockRoomUuid = "sample-room-uuid";
const mockCsrfToken = "sample-csrf-token";

export { mockFiles, mockRoomUuid, mockCsrfToken };
