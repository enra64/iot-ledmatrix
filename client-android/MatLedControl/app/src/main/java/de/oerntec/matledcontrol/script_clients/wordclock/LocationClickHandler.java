package de.oerntec.matledcontrol.script_clients.wordclock;

import android.graphics.Point;
import android.os.Handler;
import android.os.SystemClock;
import android.view.MotionEvent;

/**
 * This class reacts to onTouchEvent calls, measuring how long they take and calling on(Long)Click
 * respectively for the listener given in the constructor.
 */
class LocationClickHandler {
    private CombinedOnClickListener combinedOnClickListener;
    private Handler longClickHandler = new Handler();
    private boolean longClickExecuted = false;
    private MotionEvent.PointerCoords lastPointCoordinates = new MotionEvent.PointerCoords();


    LocationClickHandler(CombinedOnClickListener combinedOnClickListener) {
        this.combinedOnClickListener = combinedOnClickListener;
    }

    boolean onTouchEvent(MotionEvent event) {
        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                longClickHandler.postDelayed(longClickCheck, 500);
                event.getPointerCoords(0, lastPointCoordinates);
                break;
            case MotionEvent.ACTION_MOVE:
                //event.getPointerCoords(0, lastPointCoordinates);
                //break;
            case MotionEvent.ACTION_CANCEL:
            case MotionEvent.ACTION_UP:
                // only do a short-click if we did not fire the onLongClick event
                if (!longClickExecuted)
                    combinedOnClickListener.onClick((int) event.getX(), (int) event.getY());

                // reset long click state
                longClickHandler.removeCallbacks(longClickCheck);
                longClickExecuted = false;
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

    private Runnable longClickCheck = new Runnable() {
        @Override
        public void run() {
            combinedOnClickListener.onLongClick((int) lastPointCoordinates.x, (int) lastPointCoordinates.y);
            longClickExecuted = true;
        }
    };
}
