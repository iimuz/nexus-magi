/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ChatMessage = {
  /**
   * メッセージの役割（ユーザーまたはアシスタント）
   */
  role: ChatMessage.role;
  /**
   * メッセージの内容
   */
  content: string;
};
export namespace ChatMessage {
  /**
   * メッセージの役割（ユーザーまたはアシスタント）
   */
  export enum role {
    USER = 'user',
    ASSISTANT = 'assistant',
  }
}
