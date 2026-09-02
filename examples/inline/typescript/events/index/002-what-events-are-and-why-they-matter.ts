import {Content} from '@google/genai';

/**
 * Conceptual Structure of an Event (TypeScript)
 */
export interface Event extends LlmResponse {
  /** Unique ID for this specific event. */
  id: string;
  /** ID for the whole interaction run. */
  invocationId: string;
  /** 'user' or agent name. */
  author?: string;
  /** Important for side-effects & control. */
  actions: EventActions;
  /** Creation time. */
  timestamp: number;
  /** Is it streaming output? */
  partial?: boolean;
  /** Is the turn finished? */
  turnComplete?: boolean;
  /** Hierarchy path. */
  branch?: string;
  /** List of IDs for long-running tools. */
  longRunningToolIds?: string[];
  /** The content of the response. */
  content?: Content;
  // ... other LlmResponse fields like errorCode, errorMessage
}