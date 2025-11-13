"use client";

import React from "react";
import { MessageSquare, Edit2, Trash2 } from "lucide-react";
import { Button } from "./Button";

export interface Comment {
  id: string;
  user: {
    id: string;
    name: string;
    email?: string;
  };
  text: string;
  created_at: string;
  updated_at?: string;
  replies?: Comment[];
}

export interface CommentCardProps {
  /** Comment data */
  comment: Comment;
  /** Current logged-in user */
  currentUser?: {
    id: string;
    name: string;
  };
  /** Reply handler */
  onReply?: (commentId: string) => void;
  /** Edit handler */
  onEdit?: (comment: Comment) => void;
  /** Delete handler */
  onDelete?: (commentId: string) => void;
  /** Nesting depth (max 3) */
  depth?: number;
}

const getRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? "s" : ""} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
  });
};

const getInitials = (name: string): string => {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "";
  return parts
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
};

export const CommentCard: React.FC<CommentCardProps> = ({
  comment,
  currentUser,
  onReply,
  onEdit,
  onDelete,
  depth = 0,
}) => {
  const isOwn = currentUser?.id === comment.user.id;
  const canReply = depth < 3 && onReply;
  const isEdited =
    comment.updated_at && comment.updated_at !== comment.created_at;

  // Indentation based on depth
  const marginLeft = depth > 0 ? `${depth * 2}rem` : "0";

  return (
    <article
      className="group relative"
      style={{ marginLeft }}
      aria-label={`Comment by ${comment.user.name}`}
    >
      <div className="flex gap-3 p-4 rounded-lg hover:bg-gray-50 transition-colors">
        {/* Avatar */}
        <div
          className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-semibold text-sm"
          aria-hidden="true"
        >
          {getInitials(comment.user.name)}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-baseline gap-2 flex-wrap">
            <span className="font-semibold text-gray-900">
              {comment.user.name}
            </span>
            <time
              dateTime={comment.created_at}
              className="text-sm text-gray-500"
              aria-label={`Posted ${getRelativeTime(comment.created_at)}`}
            >
              {getRelativeTime(comment.created_at)}
            </time>
            {isEdited && (
              <span
                className="text-xs text-gray-400 italic"
                aria-label="This comment has been edited"
              >
                (edited)
              </span>
            )}
          </div>

          {/* Comment text */}
          <div className="mt-1 text-gray-700 whitespace-pre-wrap break-words">
            {comment.text}
          </div>

          {/* Actions */}
          <div className="mt-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            {canReply && (
              <Button
                variant="ghost"
                size="sm"
                leftIcon={<MessageSquare className="w-4 h-4" />}
                onClick={() => onReply(comment.id)}
                aria-label={`Reply to ${comment.user.name}'s comment`}
              >
                Reply
              </Button>
            )}

            {isOwn && onEdit && (
              <Button
                variant="ghost"
                size="sm"
                leftIcon={<Edit2 className="w-4 h-4" />}
                onClick={() => onEdit(comment)}
                aria-label="Edit your comment"
              >
                Edit
              </Button>
            )}

            {isOwn && onDelete && (
              <Button
                variant="ghost"
                size="sm"
                leftIcon={<Trash2 className="w-4 h-4" />}
                onClick={() => onDelete(comment.id)}
                aria-label="Delete your comment"
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                Delete
              </Button>
            )}
          </div>

          {/* Nested replies */}
          {comment.replies && comment.replies.length > 0 && (
            <div className="mt-3 space-y-2" role="list" aria-label="Replies">
              {comment.replies.map((reply) => (
                <CommentCard
                  key={reply.id}
                  comment={reply}
                  currentUser={currentUser}
                  onReply={onReply}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  depth={depth + 1}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </article>
  );
};

export default CommentCard;
