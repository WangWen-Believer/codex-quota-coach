package com.codexquotacoach.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.widget.RemoteViews

class QuotaWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(context: Context, manager: AppWidgetManager, appWidgetIds: IntArray) {
        QuotaRefreshWorker.enqueuePeriodic(context)
        render(context, manager, appWidgetIds)
        QuotaRefreshWorker.enqueueOnce(context)
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
        if (intent.action == ACTION_REFRESH) {
            QuotaRefreshWorker.enqueueOnce(context)
            updateAll(context)
        }
    }

    companion object {
        const val ACTION_REFRESH = "com.codexquotacoach.widget.ACTION_REFRESH"

        fun updateAll(context: Context) {
            val manager = AppWidgetManager.getInstance(context)
            val component = ComponentName(context, QuotaWidgetProvider::class.java)
            val ids = manager.getAppWidgetIds(component)
            render(context, manager, ids)
        }

        private fun render(context: Context, manager: AppWidgetManager, ids: IntArray) {
            if (ids.isEmpty()) return
            val snapshot = QuotaRepository.loadCachedSnapshot(context) ?: QuotaSnapshot.empty()
            val error = QuotaRepository.lastError(context)
            ids.forEach { id ->
                manager.updateAppWidget(id, buildViews(context, snapshot, error))
            }
        }

        private fun buildViews(context: Context, snapshot: QuotaSnapshot, error: String): RemoteViews {
            val views = RemoteViews(context.packageName, R.layout.widget_quota)
            val displaySnapshot = snapshot
            val headline = if (error.isNotBlank()) "数据待刷新" else displaySnapshot.headline
            val footer = footerText(displaySnapshot, error)

            views.setTextViewText(R.id.widget_primary_remaining, displaySnapshot.primary.remainingText)
            views.setTextViewText(R.id.widget_primary_status, displaySnapshot.primary.statusText)
            views.setProgressBar(
                R.id.widget_primary_progress,
                100,
                displaySnapshot.primary.remainingPercent ?: 0,
                false,
            )

            views.setTextViewText(R.id.widget_weekly_remaining, displaySnapshot.weekly.remainingText)
            views.setTextViewText(R.id.widget_weekly_status, displaySnapshot.weekly.statusText)
            views.setProgressBar(
                R.id.widget_weekly_progress,
                100,
                displaySnapshot.weekly.remainingPercent ?: 0,
                false,
            )

            views.setTextViewText(R.id.widget_headline, headline)
            views.setTextViewText(R.id.widget_footer, footer)
            views.setTextColor(R.id.widget_headline, statusColor(displaySnapshot, error))
            views.setTextColor(R.id.widget_primary_status, windowColor(displaySnapshot.primary.status, error))
            views.setTextColor(R.id.widget_weekly_status, windowColor(displaySnapshot.weekly.status, error))

            views.setOnClickPendingIntent(R.id.widget_refresh, refreshIntent(context))
            views.setOnClickPendingIntent(R.id.widget_root, openAppIntent(context))
            return views
        }

        private fun footerText(snapshot: QuotaSnapshot, error: String): String {
            if (error.isNotBlank()) {
                return "刷新失败 · ${error.take(32)}"
            }
            val updated = snapshot.updatedAtShort
            val source = snapshot.sourceDevice ?: "--"
            return "$updated · $source"
        }

        private fun refreshIntent(context: Context): PendingIntent {
            val intent = Intent(context, QuotaWidgetProvider::class.java).apply {
                action = ACTION_REFRESH
            }
            return PendingIntent.getBroadcast(
                context,
                1001,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )
        }

        private fun openAppIntent(context: Context): PendingIntent {
            val intent = Intent(context, MainActivity::class.java)
            return PendingIntent.getActivity(
                context,
                1002,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )
        }

        private fun statusColor(snapshot: QuotaSnapshot, error: String): Int {
            if (error.isNotBlank() || snapshot.stale) return RED
            val statuses = setOf(snapshot.primary.status, snapshot.weekly.status)
            return when {
                statuses.any { it == "low" || it == "empty" || it == "stale" } -> RED
                statuses.any { it == "slow" || it == "idle" || it == "fast" } -> YELLOW
                statuses.all { it == "healthy" } -> GREEN
                else -> MUTED
            }
        }

        private fun windowColor(status: String, error: String): Int {
            if (error.isNotBlank()) return RED
            return when (status) {
                "healthy" -> GREEN
                "slow", "idle", "fast" -> YELLOW
                "low", "empty", "stale" -> RED
                else -> MUTED
            }
        }

        private val GREEN = Color.parseColor("#43D17A")
        private val YELLOW = Color.parseColor("#E7B84B")
        private val RED = Color.parseColor("#EF6A6A")
        private val MUTED = Color.parseColor("#9AA0A6")
    }
}
