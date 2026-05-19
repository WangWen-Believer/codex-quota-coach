package com.codexquotacoach.widget

import android.app.Activity
import android.os.Bundle
import android.text.InputType
import android.view.Gravity
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

class MainActivity : Activity() {
    private lateinit var hubUrlInput: EditText
    private lateinit var tokenInput: EditText
    private lateinit var statusView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        QuotaRefreshWorker.enqueuePeriodic(this)
        setContentView(buildContent())
    }

    private fun buildContent(): ViewGroup {
        val root = ScrollView(this).apply {
            setBackgroundColor(COLORS.background)
        }
        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(20), dp(24), dp(20), dp(24))
        }
        root.addView(content)

        content.addView(text("Codex Quota Coach", 24f, COLORS.text, bold = true))
        content.addView(text("配置 Quota Hub 后，桌面 Widget 会每小时刷新 Codex 5h / Weekly 额度。", 14f, COLORS.muted).withTop(8))

        content.addView(label("Hub URL").withTop(28))
        hubUrlInput = editText("https://quota.example.com", QuotaRepository.getHubUrl(this))
        content.addView(hubUrlInput.withTop(8))

        content.addView(label("Bearer Token optional").withTop(18))
        tokenInput = editText("", QuotaRepository.getToken(this)).apply {
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
        }
        content.addView(tokenInput.withTop(8))

        val buttonRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        content.addView(buttonRow.withTop(22))
        buttonRow.addView(button("保存") { saveConfig("已保存配置") }.withRowWeight())
        buttonRow.addView(button("测试连接") { testConnection() }.withRowWeight(left = 10))
        buttonRow.addView(button("刷新") { refreshWidget() }.withRowWeight(left = 10))

        statusView = text("桌面添加 Codex Quota 小组件后即可查看额度。", 13f, COLORS.muted)
        content.addView(statusView.withTop(22))

        val cached = QuotaRepository.loadCachedSnapshot(this)
        if (cached != null) {
            statusView.text = "上次数据：${cached.headline} · ${cached.updatedAtShort} · ${cached.sourceDevice ?: "--"}"
        }

        return root
    }

    private fun saveConfig(message: String) {
        QuotaRepository.saveConfig(this, hubUrlInput.text.toString(), tokenInput.text.toString())
        QuotaRefreshWorker.enqueuePeriodic(this)
        QuotaWidgetProvider.updateAll(this)
        statusView.setTextColor(COLORS.green)
        statusView.text = message
    }

    private fun testConnection() {
        saveConfig("正在测试连接...")
        Thread {
            try {
                val snapshot = QuotaRepository.fetchAndSave(this)
                QuotaWidgetProvider.updateAll(this)
                runOnUiThread {
                    statusView.setTextColor(COLORS.green)
                    statusView.text = "连接成功：${snapshot.headline} · ${snapshot.updatedAtShort}"
                }
            } catch (error: Exception) {
                QuotaRepository.saveError(this, error.message ?: "连接失败")
                QuotaWidgetProvider.updateAll(this)
                runOnUiThread {
                    statusView.setTextColor(COLORS.red)
                    statusView.text = "连接失败：${error.message ?: "未知错误"}"
                }
            }
        }.start()
    }

    private fun refreshWidget() {
        saveConfig("已触发刷新")
        QuotaRefreshWorker.enqueueOnce(this)
    }

    private fun text(value: String, size: Float, color: Int, bold: Boolean = false): TextView {
        return TextView(this).apply {
            text = value
            textSize = size
            setTextColor(color)
            if (bold) typeface = android.graphics.Typeface.DEFAULT_BOLD
            setLineSpacing(0f, 1.15f)
        }
    }

    private fun label(value: String): TextView {
        return text(value, 13f, COLORS.text, bold = true)
    }

    private fun editText(hintValue: String, value: String): EditText {
        return EditText(this).apply {
            hint = hintValue
            setText(value)
            setSingleLine(true)
            textSize = 15f
            setTextColor(COLORS.text)
            setHintTextColor(COLORS.muted)
            setBackgroundResource(R.drawable.edit_background)
        }
    }

    private fun button(value: String, onClick: () -> Unit): Button {
        return Button(this).apply {
            text = value
            textSize = 13f
            setTextColor(COLORS.text)
            setBackgroundResource(R.drawable.button_background)
            setOnClickListener { onClick() }
            minHeight = dp(44)
            minWidth = 0
            includeFontPadding = false
        }
    }

    private fun <T : android.view.View> T.withTop(top: Int): T {
        val params = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT,
        )
        params.topMargin = dp(top)
        layoutParams = params
        return this
    }

    private fun <T : android.view.View> T.withRowWeight(left: Int = 0): T {
        val params = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        params.leftMargin = dp(left)
        layoutParams = params
        return this
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()

    private object COLORS {
        val background = android.graphics.Color.parseColor("#111315")
        val text = android.graphics.Color.parseColor("#E8EAED")
        val muted = android.graphics.Color.parseColor("#9AA0A6")
        val green = android.graphics.Color.parseColor("#43D17A")
        val red = android.graphics.Color.parseColor("#EF6A6A")
    }
}
