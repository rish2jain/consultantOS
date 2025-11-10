# Alerting System Integration Example

This document shows how the continuous monitoring system integrates with the multi-channel alerting service.

## Integration in IntelligenceMonitor

```python
# consultantos/monitoring/intelligence_monitor.py

from consultantos.services.alerting import get_alerting_service

class IntelligenceMonitor:
    """Continuous intelligence monitoring with multi-channel alerts"""

    async def check_for_changes(
        self,
        monitor: Monitor
    ) -> Optional[Alert]:
        """Run monitoring check and send alerts if changes detected"""
        
        # 1. Run analysis
        new_snapshot = await self._run_analysis(monitor)
        
        # 2. Compare with previous snapshot
        changes = await self._detect_changes(monitor, new_snapshot)
        
        # 3. Calculate confidence
        confidence = self._calculate_confidence(changes)
        
        # 4. Check if alert threshold met
        if confidence < monitor.config.alert_threshold:
            return None  # No alert needed
        
        # 5. Create alert
        alert = Alert(
            id=f"alert_{uuid.uuid4().hex[:12]}",
            monitor_id=monitor.id,
            title=self._generate_alert_title(changes),
            summary=self._generate_summary(changes),
            confidence=confidence,
            changes_detected=changes,
            created_at=datetime.utcnow()
        )
        
        # 6. Send multi-channel notifications
        await self._send_alert_notifications(monitor, alert)
        
        # 7. Store alert
        await self.db.save_alert(alert)
        
        return alert
    
    async def _send_alert_notifications(
        self,
        monitor: Monitor,
        alert: Alert
    ) -> None:
        """Send alert to all configured channels"""
        
        # Get alerting service
        alerting_service = get_alerting_service()
        
        # Build user preferences
        user_preferences = monitor.config.notification_preferences or {}
        
        # Convert changes to dict format for channels
        changes_dict = [
            {
                "change_type": change.change_type.value,
                "title": change.title,
                "description": change.description,
                "confidence": change.confidence,
                "detected_at": change.detected_at,
                "previous_value": change.previous_value,
                "current_value": change.current_value,
                "source_urls": change.source_urls
            }
            for change in alert.changes_detected
        ]
        
        # Send to all configured channels in parallel
        delivery_results = await alerting_service.send_alert(
            alert_id=alert.id,
            monitor_id=monitor.id,
            user_id=monitor.user_id,
            title=alert.title,
            summary=alert.summary,
            confidence=alert.confidence,
            changes=changes_dict,
            notification_channels=[
                channel.value 
                for channel in monitor.config.notification_channels
            ],
            user_preferences=user_preferences
        )
        
        # Log delivery results
        success_channels = [
            channel for channel, result in delivery_results.items()
            if result.status == "sent"
        ]
        failed_channels = [
            channel for channel, result in delivery_results.items()
            if result.status == "failed"
        ]
        
        self.logger.info(
            "alert_notifications_sent",
            alert_id=alert.id,
            monitor_id=monitor.id,
            success_channels=success_channels,
            failed_channels=failed_channels
        )
```

## Background Worker Integration

```python
# consultantos/jobs/monitoring_worker.py

from consultantos.services.alerting import get_alerting_service

class MonitoringWorker:
    """Background worker for scheduled monitoring checks"""
    
    async def process_monitor(self, monitor: Monitor) -> None:
        """Process a single monitor check"""
        
        try:
            # Run monitoring check
            alert = await self.intelligence_monitor.check_for_changes(monitor)
            
            if alert:
                self.logger.info(
                    "alert_generated",
                    monitor_id=monitor.id,
                    alert_id=alert.id,
                    confidence=alert.confidence,
                    change_count=len(alert.changes_detected)
                )
                # Notifications already sent by check_for_changes()
            else:
                self.logger.debug(
                    "no_alert_generated",
                    monitor_id=monitor.id,
                    reason="below_threshold"
                )
        
        except Exception as e:
            self.logger.error(
                "monitor_check_failed",
                monitor_id=monitor.id,
                error=str(e)
            )
            
            # Update error count
            monitor.error_count += 1
            monitor.last_error = str(e)
            
            if monitor.error_count >= 5:
                # Disable monitor after 5 consecutive failures
                monitor.status = MonitorStatus.ERROR
                
                # Send error notification to user
                await self._send_error_notification(monitor, str(e))
            
            await self.db.update_monitor(monitor.id, monitor.user_id, monitor.dict())
    
    async def _send_error_notification(
        self,
        monitor: Monitor,
        error_message: str
    ) -> None:
        """Send notification about monitoring errors"""
        
        alerting_service = get_alerting_service()
        user_preferences = monitor.config.notification_preferences or {}
        
        # Send error alert
        await alerting_service.send_alert(
            alert_id=f"error_{uuid.uuid4().hex[:12]}",
            monitor_id=monitor.id,
            user_id=monitor.user_id,
            title=f"⚠️ Monitoring Error: {monitor.company}",
            summary=f"Monitor has failed 5 times. Error: {error_message}",
            confidence=1.0,
            changes=[
                {
                    "change_type": "system_error",
                    "title": "Monitoring disabled due to repeated errors",
                    "description": error_message,
                    "confidence": 1.0
                }
            ],
            notification_channels=[
                channel.value 
                for channel in monitor.config.notification_channels
            ],
            user_preferences=user_preferences
        )
```

## API Endpoint Example

```python
# consultantos/api/monitoring_endpoints.py

@router.post("/{monitor_id}/run-check")
async def run_manual_check(
    monitor_id: str,
    user_id: str = Depends(get_current_user_id),
    monitor_service: IntelligenceMonitor = Depends(get_intelligence_monitor),
) -> dict:
    """
    Manually trigger monitoring check.
    
    Useful for testing or immediate updates.
    """
    try:
        # Get monitor
        monitor = await monitor_service.db.get_monitor(monitor_id, user_id)
        if not monitor:
            raise HTTPException(404, detail="Monitor not found")
        
        # Run check
        alert = await monitor_service.check_for_changes(monitor)
        
        if alert:
            return {
                "status": "alert_generated",
                "alert_id": alert.id,
                "confidence": alert.confidence,
                "change_count": len(alert.changes_detected),
                "notifications_sent": True
            }
        else:
            return {
                "status": "no_changes",
                "notifications_sent": False
            }
    
    except Exception as e:
        logger.error("manual_check_failed", monitor_id=monitor_id, error=str(e))
        raise HTTPException(500, detail=str(e))
```

## Frontend Dashboard Example

```typescript
// frontend/app/dashboard/alerts/page.tsx

'use client';

import { useEffect, useState } from 'react';

interface Notification {
  alert_id: string;
  monitor_id: string;
  title: string;
  summary: string;
  confidence: number;
  change_count: number;
  created_at: string;
  read: boolean;
  priority: 'high' | 'medium' | 'low';
}

export default function AlertsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch in-app notifications from Firestore
    const fetchNotifications = async () => {
      const userId = await getCurrentUserId();
      const notificationsRef = collection(
        db,
        `users/${userId}/notifications`
      );

      const q = query(
        notificationsRef,
        where('read', '==', false),
        orderBy('created_at', 'desc'),
        limit(20)
      );

      const snapshot = await getDocs(q);
      const data = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      })) as Notification[];

      setNotifications(data);
      setLoading(false);
    };

    fetchNotifications();
  }, []);

  const markAsRead = async (notificationId: string) => {
    const userId = await getCurrentUserId();
    const notificationRef = doc(
      db,
      `users/${userId}/notifications/${notificationId}`
    );

    await updateDoc(notificationRef, {
      read: true,
      read_at: new Date()
    });

    // Update local state
    setNotifications(prev => 
      prev.filter(n => n.id !== notificationId)
    );
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-orange-600 bg-orange-50';
      case 'low': return 'text-yellow-600 bg-yellow-50';
    }
  };

  if (loading) return <div>Loading alerts...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Alert Notifications</h1>

      {notifications.length === 0 ? (
        <div className="text-center text-gray-500 py-12">
          No unread alerts
        </div>
      ) : (
        <div className="space-y-4">
          {notifications.map(notification => (
            <div
              key={notification.id}
              className="border rounded-lg p-4 hover:bg-gray-50"
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-lg">
                  {notification.title}
                </h3>
                <span className={`
                  px-2 py-1 rounded text-xs font-medium
                  ${getPriorityColor(notification.priority)}
                `}>
                  {notification.priority.toUpperCase()}
                </span>
              </div>

              <p className="text-gray-700 mb-3">
                {notification.summary}
              </p>

              <div className="flex justify-between items-center text-sm">
                <div className="text-gray-500">
                  <span className="font-medium">
                    Confidence: {(notification.confidence * 100).toFixed(0)}%
                  </span>
                  <span className="mx-2">•</span>
                  <span>
                    {notification.change_count} changes detected
                  </span>
                </div>

                <button
                  onClick={() => markAsRead(notification.id)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  Mark as read
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

## Complete Flow Diagram

```
User Creates Monitor
  ↓
MonitoringWorker runs scheduled check
  ↓
IntelligenceMonitor.check_for_changes()
  ├─→ Run analysis (agents)
  ├─→ Detect changes (compare snapshots)
  ├─→ Calculate confidence
  └─→ If confidence > threshold:
        ├─→ Create Alert
        ├─→ AlertingService.send_alert()
        │     ├─→ EmailChannel (parallel)
        │     ├─→ SlackChannel (parallel)
        │     ├─→ WebhookChannel (parallel)
        │     └─→ InAppChannel (parallel)
        ├─→ Store Alert in Firestore
        └─→ Update Monitor stats

User receives notifications:
  ├─→ Email: HTML template in inbox
  ├─→ Slack: Block Kit message in channel
  ├─→ Webhook: JSON POST to custom endpoint
  └─→ In-App: Firestore notification for dashboard
```

## Error Handling Example

```python
# Handle partial delivery failures gracefully

delivery_results = await alerting_service.send_alert(...)

# Check which channels succeeded
success_channels = []
failed_channels = []

for channel, result in delivery_results.items():
    if result.status == "sent":
        success_channels.append(channel)
    elif result.status == "failed":
        failed_channels.append(channel)
        logger.warning(
            "channel_delivery_failed",
            channel=channel,
            error=result.error_message,
            retry_count=result.retry_count
        )
    elif result.status == "rate_limited":
        logger.info(
            "channel_rate_limited",
            channel=channel
        )

# Alert sent successfully if at least one channel succeeded
if success_channels:
    logger.info(
        "alert_sent_successfully",
        alert_id=alert.id,
        success_channels=success_channels,
        failed_channels=failed_channels
    )
else:
    logger.error(
        "alert_delivery_failed_all_channels",
        alert_id=alert.id,
        failed_channels=failed_channels
    )
```

## Testing Integration

```python
# tests/test_monitoring_integration.py

@pytest.mark.asyncio
async def test_monitoring_with_alerts(mock_orchestrator, mock_db, mock_alerting):
    """Test end-to-end monitoring with alert delivery"""
    
    # Setup
    monitor = Monitor(
        id="monitor_123",
        user_id="user_456",
        company="Tesla",
        industry="EVs",
        config=MonitoringConfig(
            notification_channels=["email", "slack"],
            notification_preferences={
                "email": "test@example.com",
                "slack_channel": "#alerts"
            }
        )
    )
    
    # Mock successful alert delivery
    mock_alerting.send_alert = AsyncMock(return_value={
        "email": AlertDeliveryResult(
            channel="email",
            status=DeliveryStatus.SENT,
            delivered_at=datetime.utcnow()
        ),
        "slack": AlertDeliveryResult(
            channel="slack",
            status=DeliveryStatus.SENT,
            delivered_at=datetime.utcnow()
        )
    })
    
    # Run monitoring check
    intelligence_monitor = IntelligenceMonitor(
        orchestrator=mock_orchestrator,
        db_service=mock_db
    )
    
    alert = await intelligence_monitor.check_for_changes(monitor)
    
    # Verify alert created
    assert alert is not None
    assert alert.confidence >= monitor.config.alert_threshold
    
    # Verify notifications sent
    mock_alerting.send_alert.assert_called_once()
    call_args = mock_alerting.send_alert.call_args
    assert call_args.kwargs["user_id"] == "user_456"
    assert call_args.kwargs["notification_channels"] == ["email", "slack"]
```

This integration demonstrates how the multi-channel alerting system seamlessly integrates with the existing ConsultantOS monitoring infrastructure.
