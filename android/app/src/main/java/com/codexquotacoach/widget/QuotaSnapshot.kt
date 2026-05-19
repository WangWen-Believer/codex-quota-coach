package com.codexquotacoach.widget

import org.json.JSONObject
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter

data class QuotaWindow(
    val label: String,
    val remainingPercent: Int?,
    val remainingText: String,
    val status: String,
    val statusText: String,
)

data class QuotaSnapshot(
    val headline: String,
    val updatedAt: String?,
    val sourceDevice: String?,
    val primary: QuotaWindow,
    val weekly: QuotaWindow,
    val stale: Boolean,
) {
    val updatedAtShort: String
        get() = shortTime(updatedAt)

    companion object {
        fun fromJson(json: String): QuotaSnapshot {
            val root = JSONObject(json)
            return QuotaSnapshot(
                headline = root.optString("headline", "暂无额度数据"),
                updatedAt = root.optStringOrNull("updatedAt"),
                sourceDevice = root.optStringOrNull("sourceDevice"),
                primary = root.optJSONObject("primary").toWindow("5h"),
                weekly = root.optJSONObject("weekly").toWindow("Weekly"),
                stale = root.optBoolean("stale", false),
            )
        }

        fun empty(): QuotaSnapshot {
            return QuotaSnapshot(
                headline = "配置 Hub 后开始刷新",
                updatedAt = null,
                sourceDevice = null,
                primary = QuotaWindow("5h", null, "--", "unknown", "--"),
                weekly = QuotaWindow("Weekly", null, "--", "unknown", "--"),
                stale = true,
            )
        }
    }
}

private fun JSONObject?.toWindow(defaultLabel: String): QuotaWindow {
    if (this == null) {
        return QuotaWindow(defaultLabel, null, "--", "unknown", "--")
    }
    val percent = if (has("remainingPercent") && !isNull("remainingPercent")) {
        optDouble("remainingPercent").toInt().coerceIn(0, 100)
    } else {
        null
    }
    return QuotaWindow(
        label = optString("label", defaultLabel),
        remainingPercent = percent,
        remainingText = optString("remainingText", percent?.let { "$it%" } ?: "--"),
        status = optString("status", "unknown"),
        statusText = optString("statusText", "--"),
    )
}

private fun JSONObject.optStringOrNull(name: String): String? {
    if (!has(name) || isNull(name)) return null
    return optString(name).takeIf { it.isNotBlank() }
}

private fun shortTime(value: String?): String {
    if (value.isNullOrBlank()) return "--"
    return try {
        OffsetDateTime.parse(value).format(DateTimeFormatter.ofPattern("HH:mm"))
    } catch (_: Exception) {
        value
    }
}
