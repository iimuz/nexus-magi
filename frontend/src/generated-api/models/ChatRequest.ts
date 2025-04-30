/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
import type { ChatMessage } from './ChatMessage';
export type ChatRequest = {
    /**
     * メッセージの履歴
     */
    messages: Array<ChatMessage>;
    /**
     * ストリーミングモードを使用するかどうか
     */
    stream?: boolean;
    /**
     * 討論モードを使用するかどうか
     */
    debate?: boolean;
    /**
     * 討論ラウンド数
     */
    debate_rounds?: number;
};
