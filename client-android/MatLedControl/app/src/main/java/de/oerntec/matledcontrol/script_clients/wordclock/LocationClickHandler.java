package de.oerntec.matledcontrol.script_clients.wordclock;

import android.os.SystemClock;
import android.view.MotionEvent;

/**
 * This class reacts to onTouchEvent calls, measuring how long they take and calling on(Long)Click
 * respectively for the listener given in the constructor.
 */
class LocationClickHandler {
    private CombinedOnClickListener combinedOnClickListener;
    private long lastTouchStartTime = 0;

    LocationClickHandler(CombinedOnClickListener combinedOnClickListener) {
        this.combinedOnClickListener = combinedOnClickListener;
    }

    boolean onTouchEvent(MotionEvent event) {
        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                lastTouchStartTime = SystemClock.elapsedRealtime() + 600;
                break;
            case MotionEvent.ACTION_CANCEL:
            case MotionEvent.ACTION_UP:
                if (SystemClock.elapsedRealtime() < lastTouchStartTime)
                    combinedOnClickListener.onClick((int) event.getX(), (int) event.getY());
                else
                    combinedOnClickListener.onLongClick((int) event.getX(), (int) event.getY());
                break;
            default:
                return false;
        }
        return true;
    }

    interface CombinedOnClickListener {
        void onClick(int x, int y);

        void onLongClick(int x, int y);
    }
}
