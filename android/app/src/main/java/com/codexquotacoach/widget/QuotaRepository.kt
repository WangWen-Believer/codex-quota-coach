package com.codexquotacoach.widget

import android.content.Context
import java.net.HttpURLConnection
import java.net.URL
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter

object QuotaRepository {
    private const val PREFS = "codex_quota_prefs"
    private const val KEY_HUB_URL = "hub_url"
    private const val KEY_TOKEN = "token"
    private const val KEY_LAST_SNAPSHOT = "last_snapshot"
    private const val KEY_LAST_ERROR = "last_error"
    private const val KEY_LAST_ERROR_AT = "last_error_at"

    fun getHubUrl(context: Context): String {
        return prefs(context).getString(KEY_HUB_URL, "") ?: ""
    }

    fun getToken(context: Context): String {
        return prefs(context).getString(KEY_TOKEN, "") ?: ""
    }

    fun saveConfig(context: Context, hubUrl: String, token: String) {
        prefs(context).edit()
            .putString(KEY_HUB_URL, normalizeHubUrl(hubUrl))
            .putString(KEY_TOKEN, token.trim())
            .apply()
    }

    fun loadCachedSnapshot(context: Context): QuotaSnapshot? {
        val raw = prefs(context).getString(KEY_LAST_SNAPSHOT, null) ?: return null
        return try {
            QuotaSnapshot.fromJson(raw)
        } catch (_: Exception) {
            null
        }
    }

    fun lastError(context: Context): String {
        return prefs(context).getString(KEY_LAST_ERROR, "") ?: ""
    }

    fun lastErrorAt(context: Context): String {
        return prefs(context).getString(KEY_LAST_ERROR_AT, "") ?: ""
    }

    fun fetchAndSave(context: Context): QuotaSnapshot {
        val hubUrl = getHubUrl(context)
        if (hubUrl.isBlank()) {
            throw IllegalStateException("Hub URL 未配置")
        }

        val raw = fetchQuotaJson(hubUrl, getToken(context))
        val snapshot = QuotaSnapshot.fromJson(raw)
        prefs(context).edit()
            .putString(KEY_LAST_SNAPSHOT, raw)
            .remove(KEY_LAST_ERROR)
            .remove(KEY_LAST_ERROR_AT)
            .apply()
        return snapshot
    }

    fun saveError(context: Context, message: String) {
        prefs(context).edit()
            .putString(KEY_LAST_ERROR, message.take(120))
            .putString(KEY_LAST_ERROR_AT, OffsetDateTime.now().format(DateTimeFormatter.ISO_OFFSET_DATE_TIME))
            .apply()
    }

    private fun fetchQuotaJson(hubUrl: String, token: String): String {
        val endpoint = if (hubUrl.endsWith("/quota")) hubUrl else "${hubUrl.trimEnd('/')}/quota"
        val connection = (URL(endpoint).openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            connectTimeout = 10_000
            readTimeout = 10_000
            setRequestProperty("Accept", "application/json")
            if (token.isNotBlank()) {
                setRequestProperty("Authorization", "Bearer $token")
            }
        }

        return try {
            val code = connection.responseCode
            val stream = if (code in 200..299) connection.inputStream else connection.errorStream
            val body = stream?.bufferedReader(Charsets.UTF_8)?.use { it.readText() }.orEmpty()
            if (code !in 200..299) {
                throw IllegalStateException("Hub HTTP $code: ${body.take(80)}")
            }
            body
        } finally {
            connection.disconnect()
        }
    }

    private fun normalizeHubUrl(value: String): String {
        val trimmed = value.trim().trimEnd('/')
        if (trimmed.isBlank()) return ""
        if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
            return trimmed
        }
        return "http://$trimmed"
    }

    private fun prefs(context: Context) = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
}
