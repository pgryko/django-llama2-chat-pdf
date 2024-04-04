/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class ChromaService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Chroma Heartbeat
     * From chromadb get the current time in nanoseconds since epoch.
     * Used to check if the chroma service is alive.
     * @returns any OK
     * @throws ApiError
     */
    public chatApisChromaChromaHeartbeat(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/chat/chroma/heartbeat',
        });
    }
    /**
     * List Collections
     * Return a list of all collections.
     * @returns any OK
     * @throws ApiError
     */
    public chatApisChromaListCollections(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/chat/chroma/list',
        });
    }
    /**
     * Chroma Get
     * @param collection
     * @returns any OK
     * @throws ApiError
     */
    public chatApisChromaChromaGet(
        collection: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/chat/chroma/{collection}',
            path: {
                'collection': collection,
            },
        });
    }
    /**
     * Chroma Delete
     * Deletes the contents of the collection
     * @param collection
     * @returns any OK
     * @throws ApiError
     */
    public chatApisChromaChromaDelete(
        collection: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/chat/chroma/{collection}',
            path: {
                'collection': collection,
            },
        });
    }
}
