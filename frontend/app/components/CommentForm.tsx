"use client";

import React, { useState, useEffect } from "react";
import { Send, X } from "lucide-react";
import { Button } from "./Button";
import { Alert } from "./Alert";

export interface CommentFormProps {
  /** Report ID */
  reportId: string;
  /** Parent comment ID for replies */
  parentCommentId?: string;
  /** Existing comment for edit mode */
  existingComment?: {
    id: string;
    text: string;
  };
  /** Submit handler */
  onSubmit: (text: string) => Promise<void>;
  /** Cancel handler */
  onCancel?: () => void;
  /** Placeholder text */
  placeholder?: string;
}

const MAX_CHARS = 1000;

export const CommentForm: React.FC<CommentFormProps> = ({
  reportId,
  parentCommentId,
  existingComment,
  onSubmit,
  onCancel,
  placeholder = "Write a comment...",
}) => {
  const [text, setText] = useState(existingComment?.text || "");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditMode = Boolean(existingComment);
  const isReplyMode = Boolean(parentCommentId);
  const remainingChars = MAX_CHARS - text.length;
  const isOverLimit = remainingChars < 0;
  const isEmpty = text.trim().length === 0;

  useEffect(() => {
    if (existingComment) {
      setText(existingComment.text);
    }
  }, [existingComment]);

  const submitComment = async () => {
    if (isEmpty || isOverLimit) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(text.trim());
      setText(""); // Clear on success
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit comment");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submitComment();
  };

  const handleCancel = () => {
    setText(existingComment?.text || "");
    setError(null);
    onCancel?.();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Ctrl/Cmd + Enter
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      submitComment();
    }

    // Cancel on Escape
    if (e.key === "Escape" && onCancel) {
      e.preventDefault();
      handleCancel();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      {error && (
        <Alert
          variant="error"
          description={error}
          dismissible
          onClose={() => setError(null)}
        />
      )}

      <div className="relative">
        <label htmlFor={`comment-${reportId}`} className="sr-only">
          {isEditMode
            ? "Edit comment"
            : isReplyMode
            ? "Reply to comment"
            : "Add comment"}
        </label>

        <textarea
          id={`comment-${reportId}`}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isSubmitting}
          // maxLength restricts new input; isOverLimit handles pre-existing content that may exceed limit
          maxLength={MAX_CHARS}
          rows={3}
          className={`
            w-full px-4 py-3 rounded-lg border transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-offset-1
            disabled:opacity-50 disabled:cursor-not-allowed
            resize-none
            ${
              isOverLimit
                ? "border-red-300 focus:border-red-500 focus:ring-red-500"
                : "border-gray-300 focus:border-primary-500 focus:ring-primary-500"
            }
          `}
          aria-describedby={`comment-counter-${reportId} comment-hint-${reportId}`}
          aria-invalid={isOverLimit}
        />

        {/* Character counter */}
        <div
          id={`comment-counter-${reportId}`}
          className={`
            absolute bottom-2 right-2 text-xs font-medium
            ${
              isOverLimit
                ? "text-red-600"
                : remainingChars < 100
                ? "text-yellow-600"
                : "text-gray-400"
            }
          `}
          aria-live="polite"
          aria-atomic="true"
        >
          {remainingChars < 100 && (
            <span>
              {remainingChars} character{remainingChars !== 1 ? "s" : ""}{" "}
              remaining
            </span>
          )}
        </div>
      </div>

      {/* Helper text */}
      <p id={`comment-hint-${reportId}`} className="text-xs text-gray-500">
        Press{" "}
        <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs">
          Ctrl
        </kbd>{" "}
        +{" "}
        <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs">
          Enter
        </kbd>{" "}
        to submit
        {onCancel && (
          <>
            {", "}
            <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs">
              Esc
            </kbd>{" "}
            to cancel
          </>
        )}
      </p>

      {/* Action buttons */}
      <div className="flex items-center gap-2 justify-end">
        {onCancel && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleCancel}
            disabled={isSubmitting}
            leftIcon={<X className="w-4 h-4" />}
          >
            Cancel
          </Button>
        )}

        <Button
          type="submit"
          variant="primary"
          size="sm"
          isLoading={isSubmitting}
          disabled={isEmpty || isOverLimit || isSubmitting}
          leftIcon={!isSubmitting && <Send className="w-4 h-4" />}
        >
          {isEditMode ? "Save" : isReplyMode ? "Reply" : "Comment"}
        </Button>
      </div>

      {/* Future enhancement placeholder */}
      {/* TODO: Add @ mention suggestions */}
    </form>
  );
};
export default CommentForm;
