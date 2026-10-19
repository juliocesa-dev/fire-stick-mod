package com.gathin.tvhome;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.drawable.GradientDrawable;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.widget.TextView;

/**
 * Software screen dimmer: a translucent black layer drawn over everything (any app, not just this launcher)
 * via an accessibility overlay window, plus a transient on-screen HUD while the level is being adjusted.
 * Doesn't touch the TV's real backlight - there's no API for that from an HDMI source - this only darkens the
 * picture the Fire TV outputs, the same trick screen-dimmer apps use.
 */
class DimOverlay {

    private static final String PREFS = "tvhome";
    private static final String KEY_LEVEL = "dim_level";
    static final int STEPS = 10;
    private static final float MAX_ALPHA = 0.85f;   // never fully opaque: always some picture left to see
    private static final long HUD_TIMEOUT_MS = 2500;

    private final Context ctx;
    private final WindowManager wm;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Runnable hideHudRunnable = this::hideHud;

    private View dimView;
    private TextView hudView;
    private int level;   // 0..STEPS, 0 = off

    DimOverlay(Context ctx) {
        this.ctx = ctx;
        this.wm = (WindowManager) ctx.getSystemService(Context.WINDOW_SERVICE);
        this.level = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getInt(KEY_LEVEL, 0);
        applyDim();
    }

    /** Hold-to-open: shows the HUD so the level is visible before the first adjustment. */
    void open() {
        showHud();
        resetHudTimeout();
    }

    void adjust(int delta) {
        level = Math.max(0, Math.min(STEPS, level + delta));
        ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putInt(KEY_LEVEL, level).apply();
        applyDim();
        showHud();
        resetHudTimeout();
    }

    boolean isHudShowing() {
        return hudView != null;
    }

    void close() {
        handler.removeCallbacks(hideHudRunnable);
        hideHud();
    }

    private void resetHudTimeout() {
        handler.removeCallbacks(hideHudRunnable);
        handler.postDelayed(hideHudRunnable, HUD_TIMEOUT_MS);
    }

    private void applyDim() {
        float alpha = (level / (float) STEPS) * MAX_ALPHA;
        if (level == 0) {
            if (dimView != null) {
                try {
                    wm.removeView(dimView);
                } catch (Exception ignored) {
                }
                dimView = null;
            }
            return;
        }
        if (dimView == null) {
            dimView = new View(ctx);
            dimView.setBackgroundColor(Color.BLACK);
            WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                    WindowManager.LayoutParams.MATCH_PARENT, WindowManager.LayoutParams.MATCH_PARENT,
                    WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
                    WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                            | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                    PixelFormat.TRANSLUCENT);
            lp.gravity = Gravity.TOP | Gravity.START;
            try {
                wm.addView(dimView, lp);
            } catch (Exception e) {
                dimView = null;
                return;
            }
        }
        dimView.setAlpha(alpha);
    }

    private void showHud() {
        float dp = ctx.getResources().getDisplayMetrics().density;
        if (hudView == null) {
            hudView = new TextView(ctx);
            hudView.setTextColor(Color.WHITE);
            hudView.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 16);
            hudView.setPaddingRelative((int) (22 * dp), (int) (14 * dp), (int) (22 * dp), (int) (14 * dp));
            try {
                hudView.setTypeface(ctx.getResources().getFont(R.font.open_sans));
            } catch (Exception ignored) {
            }
            GradientDrawable bg = new GradientDrawable();
            bg.setColor(Color.argb(230, 28, 28, 30));
            bg.setCornerRadius(16 * dp);
            hudView.setBackground(bg);
            WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                    WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT,
                    WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
                    WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                            | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                    PixelFormat.TRANSLUCENT);
            lp.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
            lp.y = (int) (64 * dp);
            try {
                wm.addView(hudView, lp);
            } catch (Exception e) {
                hudView = null;
                return;
            }
        }
        StringBuilder bars = new StringBuilder();
        for (int i = 0; i < STEPS; i++) bars.append(i < level ? '█' : '░');
        hudView.setText("🔅  " + bars);
    }

    private void hideHud() {
        if (hudView == null) return;
        try {
            wm.removeView(hudView);
        } catch (Exception ignored) {
        }
        hudView = null;
    }
}
