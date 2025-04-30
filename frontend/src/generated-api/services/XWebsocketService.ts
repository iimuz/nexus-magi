/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
import type { ChatRequest } from '../models/ChatRequest';
import type { WebSocketResponse } from '../models/WebSocketResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class XWebsocketService {
    /**
     * WebSocketチャットエンドポイント
     * @param requestBody
     * @returns WebSocketResponse The request has succeeded.
     * @throws ApiError
     */
    public static chatWebsocketChat(
        requestBody: {
            request: ChatRequest;
        },
    ): CancelablePromise<WebSocketResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/chat/ws',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * WebSocket討論チャットエンドポイント
     * @param requestBody
     * @returns WebSocketResponse The request has succeeded.
     * @throws ApiError
     */
    public static debateWebsocketDebate(
        requestBody: {
            request: ChatRequest;
        },
    ): CancelablePromise<WebSocketResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/debate/ws',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
