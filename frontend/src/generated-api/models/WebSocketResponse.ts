/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type WebSocketResponse = {
    /**
     * レスポンスを生成するシステム（MAGI）
     */
    system: WebSocketResponse.system;
    /**
     * レスポンスの内容
     */
    response: string;
    /**
     * 現在のフェーズ
     */
    phase?: string;
};
export namespace WebSocketResponse {
    /**
     * レスポンスを生成するシステム（MAGI）
     */
    export enum system {
        MELCHIOR = 'melchior',
        BALTHASAR = 'balthasar',
        CASPER = 'casper',
        CONSENSUS = 'consensus',
    }
}

