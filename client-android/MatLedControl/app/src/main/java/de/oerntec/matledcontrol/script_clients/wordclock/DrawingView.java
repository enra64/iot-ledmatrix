package de.oerntec.matledcontrol.script_clients.wordclock;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Point;
import android.graphics.Rect;
import android.support.annotation.ColorInt;
import android.support.v4.content.ContextCompat;
import android.util.AttributeSet;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Collections;

import de.oerntec.matledcontrol.R;

public class DrawingView extends View implements LocationClickHandler.CombinedOnClickListener {
    private final LocationClickHandler mClickHandler = new LocationClickHandler(this);
    private UpdateRequiredListener mUpdateListener;

    ArrayList<String[]> mLines = new ArrayList<>();
    ArrayList<ArrayList<Rect>> mWordBoundingRectangles;
    ArrayList<ArrayList<Integer>> mWordColors;

    private static final float TEST_TEXT_SIZE = 24f;

    private Paint canvasPaint, textPaint;
    private Canvas drawCanvas;
    private Bitmap canvasBitmap;

    @ColorInt
    private int mCurrentColor;

    public DrawingView(Context context, AttributeSet attrs) {
        super(context, attrs);

        // set up paints
        textPaint = new Paint(Paint.DITHER_FLAG | Paint.ANTI_ALIAS_FLAG);
        canvasPaint = new Paint(Paint.DITHER_FLAG);
    }


    @Override
    protected void onSizeChanged(int width, int height, int oldWidth, int oldHeight) {
        super.onSizeChanged(width, height, oldWidth, oldHeight);
        canvasBitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
        drawCanvas = new Canvas(canvasBitmap);

        // force reloading the configuration
        setLines(mLines);
    }

    private void loadShittyDebugWordclockConfig(){
        ArrayList<String[]> lines = new ArrayList<>();
        lines.add(new String[]{"HALF", "TWENTY"});
        lines.add(new String[]{"QUARTER", "FIVE"});
        lines.add(new String[]{"TEN", "MINUTES"});
        lines.add(new String[]{"TO", "PAST", "THREE"});
        lines.add(new String[]{"ONE", "TWO", "FOUR"});
        lines.add(new String[]{"TWELVE", "EIGHT"});
        lines.add(new String[]{"ELEVEN", "NINE"});
        lines.add(new String[]{"TEN", "SEVEN", "SIX"});
        lines.add(new String[]{"FIVE", "O'CLOCK"});
        lines.add(new String[]{"\u25CF", "\u25CF", "\u25CF", "\u25CF"});
        setLines(lines);
    }

    private void updateFontSize(ArrayList<String[]> lines, ArrayList<String> concatenatedLines, String longestLine) {
        // set the font size so the widest line will fit
        textPaint.setTextSize(TEST_TEXT_SIZE);
        textPaint.setTextSize(TEST_TEXT_SIZE * getWidth() / textPaint.measureText(longestLine));

        // store the new width for each line
        ArrayList<Integer> lineWidths = new ArrayList<>();
        ArrayList<Integer> lineHeights = new ArrayList<>();

        Rect measurementRect = new Rect();
        for (String line : concatenatedLines) {
            textPaint.getTextBounds(line, 0, line.length(), measurementRect);
            lineWidths.add(measurementRect.width());
            lineHeights.add(measurementRect.height());
        }

        int maxLineHeight = Collections.max(lineHeights);
        int maxLineWidth = Collections.max(lineWidths);
        int availablePadding = (getWidth() - maxLineWidth);
        int interWordMargin = availablePadding / 2;

        // store bounding rectangle for each word
        mWordBoundingRectangles = new ArrayList<>();
        int yOffset = maxLineHeight;
        for (int lineIndex = 0; lineIndex < lines.size(); lineIndex++) {
            ArrayList<Rect> lineBoundingRectangles = new ArrayList<>();
            int xOffset = (getWidth() - lineWidths.get(lineIndex)) / 2;
            for (String word : lines.get(lineIndex)) {
                Rect boundingRect = new Rect();
                textPaint.getTextBounds(word, 0, word.length(), boundingRect);
                boundingRect.offsetTo(-boundingRect.left, boundingRect.top - boundingRect.bottom);
                boundingRect.offset(xOffset, yOffset);
                lineBoundingRectangles.add(boundingRect);
                xOffset += boundingRect.width() + interWordMargin;
            }
            yOffset += maxLineHeight;
            mWordBoundingRectangles.add(lineBoundingRectangles);
        }
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        return mClickHandler.onTouchEvent(event);
    }

    void setLines(ArrayList<String[]> lines) {
        if(lines.size() > 0){
            this.mLines = lines;

            // concatenate all lines; create color int for all words
            mWordColors = new ArrayList<>();
            ArrayList<String> concatenatedLines = new ArrayList<>();
            for (String[] line : lines) {
                ArrayList<Integer> lineWordColors = new ArrayList<>();
                StringBuilder sb = new StringBuilder();
                for (String word : line) {
                    sb.append(word);
                    lineWordColors.add(Color.BLACK);
                }
                mWordColors.add(lineWordColors);
                concatenatedLines.add(sb.toString());
            }

            // find the widest line
            float max = Integer.MIN_VALUE;
            int maxWidthIndex = -1;
            for (int i = 0; i < concatenatedLines.size(); i++) {
                float width = textPaint.measureText(concatenatedLines.get(i));
                if (width > max) {
                    max = width;
                    maxWidthIndex = i;
                }
            }

            updateFontSize(mLines, concatenatedLines, concatenatedLines.get(maxWidthIndex));
            redraw();
        }
    }

    void setChangeListener(UpdateRequiredListener updateRequiredListener) {
        mUpdateListener = updateRequiredListener;
    }

    /**
     * Update the color that will be applied to newly clicked words
     *
     * @param color integer color representation
     */
    void setColor(@ColorInt int color) {
        mCurrentColor = color;
    }

    private void redraw() {
        // blank canvas
        drawCanvas.drawColor(ContextCompat.getColor(getContext(), R.color.wordclock_background_color));

        for (int lineIndex = 0; lineIndex < mLines.size(); lineIndex++) {
            String[] line = mLines.get(lineIndex);

            for (int wordIndex = 0; wordIndex < line.length; wordIndex++) {
                // apply word color
                Rect boundingRectangle = mWordBoundingRectangles.get(lineIndex).get(wordIndex);
                textPaint.setColor(mWordColors.get(lineIndex).get(wordIndex));
                drawCanvas.drawText(line[wordIndex], boundingRectangle.left, boundingRectangle.bottom, textPaint);
            }
        }

        // reeeedraw
        invalidate();
        mUpdateListener.onWordChanged();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        canvas.drawBitmap(canvasBitmap, 0, 0, canvasPaint);
    }

    JSONObject getAsJsonObject() {
        JSONArray colorArray = new JSONArray();
        for(ArrayList<Integer> lineList : mWordColors)
            colorArray.put(new JSONArray(lineList));
        JSONObject responseWrapper = new JSONObject();
        try {
            responseWrapper.put("word_color_config", colorArray);
        } catch (JSONException e) {
            Log.wtf("wordcdrw", "how the fuck can you get an exception while parsing the wordclock colors to JSON");
        }
        return responseWrapper;
    }

    private Point getWord(int x, int y) {
        for (int lineIndex = 0; lineIndex < mLines.size(); lineIndex++) {
            for (int wordIndex = 0; wordIndex < mLines.get(lineIndex).length; wordIndex++) {
                Rect boundingRect = mWordBoundingRectangles.get(lineIndex).get(wordIndex);
                // found the one?
                if (boundingRect.contains(x, y))
                    return new Point(lineIndex, wordIndex);
                    // skip this line if the rect is above the y coordinate
                else if (boundingRect.bottom < y)
                    break;
            }
        }
        return null;
    }

    @Override
    public void onClick(int x, int y) {
        Point wordCoordinates = getWord(x, y);
        if (wordCoordinates != null) {
            mWordColors.get(wordCoordinates.x).set(wordCoordinates.y, mCurrentColor);
            redraw();
        }
    }

    @Override
    public void onLongClick(int x, int y) {
        Point wordCoordinates = getWord(x, y);
        if (wordCoordinates != null)
            mUpdateListener.onColorCopied(mWordColors.get(wordCoordinates.x).get(wordCoordinates.y));
    }

    interface UpdateRequiredListener {
        void onWordChanged();

        void onColorCopied(@ColorInt int color);
    }
}

