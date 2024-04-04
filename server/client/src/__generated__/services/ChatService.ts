/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DocumentFileSchema } from '../models/DocumentFileSchema';
import type { Message } from '../models/Message';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class ChatService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Upload File
     * @param roomUuid
     * @param formData
     * @returns DocumentFileSchema OK
     * @throws ApiError
     */
    public chatApisChatUploadFile(
        roomUuid: string,
        formData: {
            file: Blob;
        },
    ): CancelablePromise<Array<DocumentFileSchema>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/chat/upload/{room_uuid}',
            path: {
                'room_uuid': roomUuid,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
        });
    }
    /**
     * Get Files
     * @param roomUuid
     * @returns DocumentFileSchema OK
     * @throws ApiError
     */
    public chatApisChatGetFiles(
        roomUuid: string,
    ): CancelablePromise<Array<DocumentFileSchema>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/chat/files/{room_uuid}',
            path: {
                'room_uuid': roomUuid,
            },
        });
    }
    /**
     * Delete Files
     * @param roomUuid
     * @param fileUuid
     * @returns DocumentFileSchema OK
     * @throws ApiError
     */
    public chatApisChatDeleteFiles(
        roomUuid: string,
        fileUuid: string,
    ): CancelablePromise<Array<DocumentFileSchema>> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/chat/file/{room_uuid}/{file_uuid}',
            path: {
                'room_uuid': roomUuid,
                'file_uuid': fileUuid,
            },
        });
    }
    /**
     * Get Stream Chat
     * @param roomUuid
     * @returns any OK
     * @throws ApiError
     */
    public chatApisChatGetStreamChat(
        roomUuid: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/chat/stream_chat/{room_uuid}',
            path: {
                'room_uuid': roomUuid,
            },
        });
    }
    /**
     * Set Messages
     * @param roomUuid
     * @param requestBody
     * @returns any OK
     * @throws ApiError
     */
    public chatApisChatSetMessages(
        roomUuid: string,
        requestBody: Array<Message>,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/chat/messages/{room_uuid}',
            path: {
                'room_uuid': roomUuid,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Get Messages
     * @param roomUuid
     * @returns any OK
     * @throws ApiError
     */
    public chatApisChatGetMessages(
        roomUuid: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/chat/messages/{room_uuid}',
            path: {
                'room_uuid': roomUuid,
            },
        });
    }
    /**
     * Set User Message
     * @param roomUuid
     * @param requestBody
     * @returns any OK
     * @throws ApiError
     */
    public chatApisChatSetUserMessage(
        roomUuid: string,
        requestBody: Message,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/chat/message/{room_uuid}',
            path: {
                'room_uuid': roomUuid,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
