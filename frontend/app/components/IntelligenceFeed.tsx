'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  IntelligenceCard,
  IntelligenceFeedData,
  IntelligenceFeedProps,
  IntelligenceCardType,
  UrgencyLevel,
} from '@/types/strategic-intelligence';

const IntelligenceFeed: React.FC<IntelligenceFeedProps> = ({
  initialData,
  enableRealtime = false,
  filters = [],
  onActionClick,
}) => {
  const [feedData, setFeedData] = useState<IntelligenceFeedData>(
    initialData || { cards: [], unread_count: 0, last_updated: new Date().toISOString() }
  );
  const [selectedFilters, setSelectedFilters] = useState<Set<IntelligenceCardType>>(
    new Set(filters)
  );
  const [showOnlyUnread, setShowOnlyUnread] = useState(false);
  const [selectedCard, setSelectedCard] = useState<IntelligenceCard | null>(null);

  const getUrgencyIcon = (urgency: UrgencyLevel): string => {
    switch (urgency) {
      case 'critical':
        return '🔴';
      case 'important':
        return '🟡';
      case 'info':
        return '🔵';
      default:
        return '⚪';
    }
  };

  const getUrgencyColor = (urgency: UrgencyLevel): string => {
    switch (urgency) {
      case 'critical':
        return 'border-red-500 bg-red-50';
      case 'important':
        return 'border-yellow-500 bg-yellow-50';
      case 'info':
        return 'border-blue-500 bg-blue-50';
      default:
        return 'border-gray-300 bg-white';
    }
  };

  const getCardTypeLabel = (type: IntelligenceCardType): string => {
    const labels: Record<IntelligenceCardType, string> = {
      disruption_alert: 'Disruption Alert',
      position_threat: 'Position Threat',
      loop_detection: 'Loop Detection',
      flywheel_milestone: 'Flywheel Milestone',
      pattern_match: 'Pattern Match',
      decision_due: 'Decision Due',
      opportunity: 'Opportunity',
      metric_threshold: 'Metric Threshold',
    };
    return labels[type];
  };

  const getCardIcon = (type: IntelligenceCardType): string => {
    const icons: Record<IntelligenceCardType, string> = {
      disruption_alert: '⚡',
      position_threat: '⚔️',
      loop_detection: '🔄',
      flywheel_milestone: '🎯',
      pattern_match: '📊',
      decision_due: '⏰',
      opportunity: '💰',
      metric_threshold: '📈',
    };
    return icons[type];
  };

  const toggleFilter = (type: IntelligenceCardType) => {
    setSelectedFilters((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(type)) {
        newSet.delete(type);
      } else {
        newSet.add(type);
      }
      return newSet;
    });
  };

  const markAsRead = useCallback((cardId: string) => {
    setFeedData((prev) => ({
      ...prev,
      cards: prev.cards.map((card) =>
        card.id === cardId ? { ...card, read: true } : card
      ),
      unread_count: Math.max(0, prev.unread_count - 1),
    }));
  }, []);

  const markAllAsRead = () => {
    setFeedData((prev) => ({
      ...prev,
      cards: prev.cards.map((card) => ({ ...card, read: true })),
      unread_count: 0,
    }));
  };

  const handleCardClick = (card: IntelligenceCard) => {
    if (!card.read) {
      markAsRead(card.id);
    }
    setSelectedCard(card);
  };

  const handleActionClick = (cardId: string, action: string) => {
    if (onActionClick) {
      onActionClick(cardId, action);
    }
  };

  // Real-time WebSocket connection (if enabled)
  useEffect(() => {
    if (!enableRealtime) return;

    // In production, replace with actual WebSocket connection
    // const ws = new WebSocket('ws://api/strategic-intelligence/live');
    // ws.onmessage = (event) => {
    //   const update = JSON.parse(event.data);
    //   handleLiveUpdate(update);
    // };
    // return () => ws.close();

    // Demo: Simulate updates every 30 seconds
    const interval = setInterval(() => {
      // Simulate new card arrival
      console.log('Simulating real-time update...');
    }, 30000);

    return () => clearInterval(interval);
  }, [enableRealtime]);

  const filteredCards = feedData.cards.filter((card) => {
    if (selectedFilters.size > 0 && !selectedFilters.has(card.type)) {
      return false;
    }
    if (showOnlyUnread && card.read) {
      return false;
    }
    return true;
  });

  const allCardTypes: IntelligenceCardType[] = [
    'disruption_alert',
    'position_threat',
    'loop_detection',
    'flywheel_milestone',
    'pattern_match',
    'decision_due',
    'opportunity',
    'metric_threshold',
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-gray-900">Intelligence Feed</h2>
            {feedData.unread_count > 0 && (
              <span className="bg-red-600 text-white text-sm font-bold px-3 py-1 rounded-full">
                {feedData.unread_count} new
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowOnlyUnread(!showOnlyUnread)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                showOnlyUnread
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Unread Only
            </button>

            {feedData.unread_count > 0 && (
              <button
                onClick={markAllAsRead}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-300 transition-colors"
              >
                Mark All Read
              </button>
            )}
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          {allCardTypes.map((type) => (
            <button
              key={type}
              onClick={() => toggleFilter(type)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                selectedFilters.has(type)
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {getCardIcon(type)} {getCardTypeLabel(type)}
            </button>
          ))}
        </div>
      </div>

      {/* Feed */}
      <div className="p-4 max-h-[600px] overflow-y-auto space-y-3">
        <AnimatePresence mode="popLayout">
          {filteredCards.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">No intelligence cards to display</p>
              <p className="text-sm mt-2">
                {showOnlyUnread
                  ? 'All caught up! No unread items.'
                  : 'Adjust filters to see more items.'}
              </p>
            </div>
          ) : (
            filteredCards.map((card) => (
              <motion.div
                key={card.id}
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -100 }}
                className={`border-l-4 rounded-lg p-4 cursor-pointer transition-all ${getUrgencyColor(
                  card.urgency
                )} ${!card.read ? 'shadow-md' : 'opacity-75'}`}
                onClick={() => handleCardClick(card)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{getUrgencyIcon(card.urgency)}</span>
                    <span className="text-lg">{getCardIcon(card.type)}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900">{card.title}</h3>
                      <span className="text-xs text-gray-500">{getCardTypeLabel(card.type)}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {!card.read && (
                      <span className="w-2 h-2 bg-blue-600 rounded-full" />
                    )}
                    <span className="text-xs text-gray-500">
                      {new Date(card.timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>

                <p className="text-sm text-gray-700 mb-3">{card.description}</p>

                {/* Metadata badges */}
                {Object.keys(card.metadata).length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {Object.entries(card.metadata).slice(0, 3).map(([key, value]) => (
                      <span
                        key={key}
                        className="text-xs bg-white bg-opacity-50 px-2 py-1 rounded"
                      >
                        <span className="font-medium">{key}:</span>{' '}
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </span>
                    ))}
                  </div>
                )}

                {/* Quick Actions */}
                {card.actions && card.actions.length > 0 && (
                  <div className="flex gap-2">
                    {card.actions.map((action, idx) => (
                      <button
                        key={idx}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleActionClick(card.id, action.action);
                        }}
                        className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                          action.primary
                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                            : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                )}
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 p-3 bg-gray-50 text-center text-xs text-gray-500">
        Last updated: {new Date(feedData.last_updated).toLocaleString()}
        {enableRealtime && <span className="ml-2">• 🟢 Live</span>}
      </div>

      {/* Card Detail Modal */}
      <AnimatePresence>
        {selectedCard && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setSelectedCard(null)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{getUrgencyIcon(selectedCard.urgency)}</span>
                  <span className="text-3xl">{getCardIcon(selectedCard.type)}</span>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">{selectedCard.title}</h3>
                    <span className="text-sm text-gray-500">{getCardTypeLabel(selectedCard.type)}</span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedCard(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <p className="text-gray-700 mb-6">{selectedCard.description}</p>

              {/* Full Metadata */}
              {Object.keys(selectedCard.metadata).length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Details</h4>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    {Object.entries(selectedCard.metadata).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-start">
                        <span className="font-medium text-gray-700 capitalize">
                          {key.replace(/_/g, ' ')}:
                        </span>
                        <span className="text-gray-900 text-right ml-4">
                          {typeof value === 'object'
                            ? JSON.stringify(value, null, 2)
                            : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              {selectedCard.actions && selectedCard.actions.length > 0 && (
                <div className="flex gap-3">
                  {selectedCard.actions.map((action, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        handleActionClick(selectedCard.id, action.action);
                        setSelectedCard(null);
                      }}
                      className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                        action.primary
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              )}

              <div className="mt-6 text-xs text-gray-500 text-center">
                {new Date(selectedCard.timestamp).toLocaleString()}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default IntelligenceFeed;
