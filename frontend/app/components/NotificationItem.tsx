"use client";

import React from "react";
import { Bell, MessageCircle, Share2, GitBranch, Trash2 } from "lucide-react";
import { getRelativeTime } from "../utils/dateFormat";

export interface Notification {
  id: string;
  type: "comment" | "share" | "version" | "analysis" | "system";
  title: string;
  description: string;
  read: boolean;
  created_at: string;
  link?: string;
}

export interface NotificationItemProps {
  notification: Notification;
  onRead?: (id: string) => void;
  onClick?: (notification: Notification) => void;
  onDelete?: (id: string) => void;
}

const typeConfig = {
  comment: {
    icon: MessageCircle,
    color: "text-blue-600",
    bgColor: "bg-blue-50",
  },
  share: {
    icon: Share2,
    color: "text-green-600",
    bgColor: "bg-green-50",
  },
  version: {
    icon: GitBranch,
    color: "text-purple-600",
    bgColor: "bg-purple-50",
  },
  analysis: {
    icon: Bell,
    color: "text-orange-600",
    bgColor: "bg-orange-50",
  },
  system: {
    icon: Bell,
    color: "text-gray-600",
    bgColor: "bg-gray-50",
  },
};

export const NotificationItem: React.FC<NotificationItemProps> = ({
  notification,
  onRead,
  onClick,
  onDelete,
}) => {
  const [showDelete, setShowDelete] = React.useState(false);
  const config = typeConfig[notification.type];
  const IconComponent = config.icon;

  const handleClick = () => {
    if (!notification.read && onRead) {
      onRead(notification.id);
    }
    if (onClick) {
      onClick(notification);
    }
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(notification.id);
    }
  };

  return (
    <div
      className={`
        relative flex gap-3 p-4 border-b border-gray-100 transition-colors
        cursor-pointer hover:bg-gray-50 group
        ${!notification.read ? "bg-blue-50/30" : "bg-white"}
      `}
      onClick={handleClick}
      onMouseEnter={() => setShowDelete(true)}
      onMouseLeave={() => setShowDelete(false)}
      role="button"
      tabIndex={0}
      aria-label={`${notification.read ? "Read" : "Unread"} notification: ${
        notification.title
      }`}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handleClick();
        }
      }}
    >
      {/* Icon */}
      <div
        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${config.bgColor}`}
      >
        <IconComponent
          className={`w-5 h-5 ${config.color}`}
          aria-hidden="true"
        />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <p
              className={`text-sm font-medium text-gray-900 ${
                !notification.read ? "font-semibold" : ""
              }`}
            >
              {notification.title}
            </p>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {notification.description}
            </p>
          </div>

          {/* Unread indicator */}
          {!notification.read && (
            <span
              className="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full"
              aria-label="Unread"
            />
          )}
        </div>

        {/* Timestamp */}
        <p className="text-xs text-gray-500 mt-2">
          <time dateTime={notification.created_at}>
            {getRelativeTime(notification.created_at)}
          </time>
        </p>
      </div>

      {/* Delete button */}
      {showDelete && onDelete && (
        <button
          type="button"
          onClick={handleDelete}
          className="
            absolute top-4 right-4 flex-shrink-0 p-1.5
            text-gray-400 hover:text-red-600 hover:bg-red-50
            rounded-md transition-colors
            focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2
          "
          aria-label="Delete notification"
        >
          <Trash2 className="w-4 h-4" aria-hidden="true" />
        </button>
      )}
    </div>
  );
};
export default NotificationItem;
