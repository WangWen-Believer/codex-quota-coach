package com.codexquotacoach.widget

import android.content.Context
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.Worker
import androidx.work.WorkerParameters
import java.util.concurrent.TimeUnit

class QuotaRefreshWorker(
    context: Context,
    params: WorkerParameters,
) : Worker(context, params) {
    override fun doWork(): Result {
        return try {
            QuotaRepository.fetchAndSave(applicationContext)
            QuotaWidgetProvider.updateAll(applicationContext)
            Result.success()
        } catch (error: Exception) {
            QuotaRepository.saveError(applicationContext, error.message ?: "刷新失败")
            QuotaWidgetProvider.updateAll(applicationContext)
            Result.success()
        }
    }

    companion object {
        private const val PERIODIC_WORK = "codex_quota_periodic_refresh"
        private const val MANUAL_WORK = "codex_quota_manual_refresh"

        fun enqueuePeriodic(context: Context) {
            val request = PeriodicWorkRequestBuilder<QuotaRefreshWorker>(1, TimeUnit.HOURS)
                .build()
            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                PERIODIC_WORK,
                ExistingPeriodicWorkPolicy.UPDATE,
                request,
            )
        }

        fun enqueueOnce(context: Context) {
            val request = OneTimeWorkRequestBuilder<QuotaRefreshWorker>().build()
            WorkManager.getInstance(context).enqueueUniqueWork(
                MANUAL_WORK,
                ExistingWorkPolicy.REPLACE,
                request,
            )
        }
    }
}
