"use client";

import React, { useState, useEffect } from "react";
import { MessageSquare, ArrowUpDown } from "lucide-react";
import { CommentCard, Comment } from "./CommentCard";
import { CommentForm } from "./CommentForm";
import { Button } from "./Button";
import { Alert } from "./Alert";
import { Spinner } from "./Spinner";

export interface CommentThreadProps {
  /** Report ID */
  reportId: string;
  /** Comments data */
  comments: Comment[];
  /** Current logged-in user */
  currentUser?: {
    id: string;
    name: string;
  };
  /** Reply handler */
  onReply?: (commentId: string, text: string) => Promise<void>;
  /** Edit handler */
  onEdit?: (commentId: string, text: string) => Promise<void>;
  /** Delete handler */
  onDelete?: (commentId: string) => Promise<void>;
  /** Loading state */
  isLoading?: boolean;
  /** Error message */
  error?: string;
}

type SortOrder = "newest" | "oldest";

/**
 * Build a nested comment tree from flat array
 */
const buildCommentTree = (comments: Comment[]): Comment[] => {
  const commentMap = new Map<string, Comment & { replies: Comment[] }>();
  const rootComments: Comment[] = [];

  // Create a map of all comments with empty replies array
  comments.forEach((comment) => {
    commentMap.set(comment.id, { ...comment, replies: [] });
  });

  // Build the tree structure
  comments.forEach((comment) => {
    const commentWithReplies = commentMap.get(comment.id)!;

    // If no parent, it's a root comment
    if (!comment.parent_id) {
      rootComments.push(commentWithReplies);
    } else {
      // Add to parent's replies
      const parent = commentMap.get(comment.parent_id);
      if (parent) {
        parent.replies.push(commentWithReplies);
      }
    }
  });

  return rootComments;
};

/**
 * Sort comments by date
 */
const sortComments = (comments: Comment[], order: SortOrder): Comment[] => {
  const sorted = [...comments].sort((a, b) => {
    const dateA = new Date(a.created_at).getTime();
    const dateB = new Date(b.created_at).getTime();
    return order === "newest" ? dateB - dateA : dateA - dateB;
  });

  // Recursively sort replies
  return sorted.map((comment) => ({
    ...comment,
    replies: comment.replies ? sortComments(comment.replies, order) : undefined,
  }));
};

export const CommentThread: React.FC<CommentThreadProps> = ({
  reportId,
  comments,
  currentUser,
  onReply,
  onEdit,
  onDelete,
  isLoading = false,
  error,
}) => {
  const [sortOrder, setSortOrder] = useState<SortOrder>("newest");
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [editingComment, setEditingComment] = useState<Comment | null>(null);

  // Build and sort comment tree
  const commentTree = sortComments(buildCommentTree(comments), sortOrder);

  const toggleSort = () => {
    setSortOrder((prev) => (prev === "newest" ? "oldest" : "newest"));
  };

  const handleReplyClick = (commentId: string) => {
    setReplyingTo(commentId);
    setEditingComment(null);
  };

  const handleEditClick = (comment: Comment) => {
    setEditingComment(comment);
    setReplyingTo(null);
  };

  const handleReplySubmit = async (text: string) => {
    if (!replyingTo || !onReply) return;

    await onReply(replyingTo, text);
    setReplyingTo(null);
  };

  const handleEditSubmit = async (text: string) => {
    if (!editingComment || !onEdit) return;

    await onEdit(editingComment.id, text);
    setEditingComment(null);
  };

  const handleDeleteClick = async (commentId: string) => {
    if (!onDelete) return;

    const confirmed = window.confirm(
      "Are you sure you want to delete this comment? This action cannot be undone."
    );
    if (confirmed) {
      await onDelete(commentId);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" label="Loading comments..." />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        variant="error"
        title="Error loading comments"
        description={error}
      />
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-gray-400" aria-hidden="true" />
          <h2 className="text-lg font-semibold text-gray-900">
            Comments
            {comments.length > 0 && (
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({comments.length})
              </span>
            )}
          </h2>
        </div>

        {comments.length > 1 && (
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<ArrowUpDown className="w-4 h-4" />}
            onClick={toggleSort}
            aria-label={`Sort by ${
              sortOrder === "newest" ? "oldest" : "newest"
            } first`}
          >
            {sortOrder === "newest" ? "Newest" : "Oldest"}
          </Button>
        )}
      </div>

      {/* Comment list */}
      {comments.length === 0 ? (
        <div className="text-center py-12">
          <MessageSquare
            className="w-12 h-12 text-gray-300 mx-auto mb-3"
            aria-hidden="true"
          />
          <p className="text-gray-500">
            No comments yet. Be the first to comment!
          </p>
        </div>
      ) : (
        <div className="space-y-1" role="list" aria-label="Comment thread">
          {commentTree.map((comment) => (
            <div key={comment.id}>
              <CommentCard
                comment={comment}
                currentUser={currentUser}
                onReply={handleReplyClick}
                onEdit={handleEditClick}
                onDelete={handleDeleteClick}
                depth={0}
              />

              {/* Reply form */}
              {replyingTo === comment.id && (
                <div className="ml-14 mt-2 mb-4">
                  <CommentForm
                    reportId={reportId}
                    parentCommentId={comment.id}
                    onSubmit={handleReplySubmit}
                    onCancel={() => setReplyingTo(null)}
                    placeholder={`Reply to ${comment.user.name}...`}
                  />
                </div>
              )}

              {/* Edit form */}
              {editingComment?.id === comment.id && (
                <div className="ml-14 mt-2 mb-4">
                  <CommentForm
                    reportId={reportId}
                    existingComment={editingComment}
                    onSubmit={handleEditSubmit}
                    onCancel={() => setEditingComment(null)}
                    placeholder="Edit your comment..."
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Type extension to support parent_id for API integration
declare module "./CommentCard" {
  interface Comment {
    parent_id?: string;
  }
}
