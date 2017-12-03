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

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;

import de.oerntec.matledcontrol.R;

public class DrawingView extends View implements LocationClickHandler.CombinedOnClickListener {
    private final LocationClickHandler mClickHandler = new LocationClickHandler(this);
    private UpdateRequiredListener mUpdateListener;

    private HashMap<Point, Word> mWords = new HashMap<>();
    private int mLineCount;

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
    }

    private void updateFontSize(ArrayList<String> concatenatedLines, String longestLine) {
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

        // store bounding rectangle for each displayString
        int yOffset = maxLineHeight;
        for (int lineIndex = 0; lineIndex < mLineCount; lineIndex++) {
            int xOffset = (getWidth() - lineWidths.get(lineIndex)) / 2;

            for (Word word : getWordsForLine(mWords, lineIndex)) {
                textPaint.getTextBounds(word.displayString, 0, word.displayString.length(), word.boundingRectangle);
                word.boundingRectangle.offsetTo(-word.boundingRectangle.left, word.boundingRectangle.top - word.boundingRectangle.bottom);
                word.boundingRectangle.offset(xOffset, yOffset);
                xOffset += word.boundingRectangle.width() + interWordMargin;
            }
            yOffset += maxLineHeight;
        }
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        return mClickHandler.onTouchEvent(event);
    }

    private List<Word> getWordsForLine(HashMap<Point, Word> wordMap, int lineIndex) {
        ArrayList<Word> result = new ArrayList<>(5);
        for (Word w : wordMap.values())
            if (w.lineIndex == lineIndex)
                result.add(w);

        Collections.sort(result, new Comparator<Word>() {
            @Override
            public int compare(Word w1, Word w2) {
                //noinspection SuspiciousNameCombination
                return Integer.compare(w1.xPos, w2.xPos);
            }
        });

        return result;
    }

    void setLines(JSONObject lines) throws JSONException {
        mLineCount = lines.getInt("lines");

        JSONArray config = lines.getJSONArray("config");
        mWords = new HashMap<>(config.length());

        for (int i = 0; i < config.length(); i++) {
            Word newWord = new Word(i, config.getJSONObject(i));
            mWords.put(newWord.getCoordinates(), newWord);
        }

        // concatenate all lines; create color int for all words
        ArrayList<String> concatenatedLines = new ArrayList<>();
        for (int i = 0; i < mLineCount; i++) {
            StringBuilder sb = new StringBuilder();
            for (Word word : getWordsForLine(mWords, i))
                sb.append(word.displayString);
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

        updateFontSize(concatenatedLines, concatenatedLines.get(maxWidthIndex));
        redraw();
    }

    void setColors(JSONObject data) throws JSONException {
        JSONArray colorConfig = data.getJSONArray("color_config");

        for (int i = 0; i < colorConfig.length(); i++) {
            JSONObject colorInfo = colorConfig.getJSONObject(i);
            int wordId = colorInfo.getInt("id");
            int wordColor = colorInfo.getInt("clr");
            for (Word word : mWords.values())
                if (word.id == wordId)
                    word.color = wordColor;
        }

        redraw();
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

        for (Word word : mWords.values()) {
            textPaint.setColor(word.color);
            drawCanvas.drawText(word.displayString, word.boundingRectangle.left, word.boundingRectangle.bottom, textPaint);
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
        JSONObject responseWrapper = new JSONObject();

        try {
            for (Word word : mWords.values())
                colorArray.put(word.withColorAsJson());
            responseWrapper.put("word_color_config", colorArray);
        } catch (JSONException e) {
            Log.e("wordcdrw", "how the fuck can you get an exception while parsing the wordclock colors to JSON");
        }
        return responseWrapper;
    }

    private Word getWordByTouchCoordinates(int x, int y) {
        for (Word word : mWords.values())
            if (word.boundingRectangle.contains(x, y))
                return word;
        return null;
    }

    @Override
    public void onClick(int x, int y) {
        Word word = getWordByTouchCoordinates(x, y);
        if (word != null) {
            word.color = mCurrentColor;
            redraw();
        }
    }

    @Override
    public void onLongClick(int x, int y) {
        Word word = getWordByTouchCoordinates(x, y);
        if (word != null)
            mUpdateListener.onColorCopied(word.color);
    }

    interface UpdateRequiredListener {
        void onWordChanged();

        void onColorCopied(@ColorInt int color);
    }

    @SuppressWarnings("unused")
    private class Word {
        private String displayString;
        private int xPos, lineIndex;
        private Rect ledRectangle;
        private WordCategory category;
        private String info;
        private int id;
        @ColorInt
        private int color = Color.BLACK;
        private Rect boundingRectangle = new Rect();

        Word(int id, JSONObject data) throws JSONException {
            this.id = id;
            displayString = data.getString("word");
            ledRectangle = getRectFromJsonArray(data.getJSONObject("rect"));

            if (data.has("pos")) {
                xPos = data.getJSONArray("pos").getInt(0);
                lineIndex = data.getJSONArray("pos").getInt(1);
            } else {
                xPos = ledRectangle.left;
                lineIndex = ledRectangle.top;
            }



            category = WordCategory.valueOf(data.getString("category"));
            Object info = data.get("info");
            if (info instanceof String) this.info = (String) info;
            else this.info = Integer.toString((Integer) info);
        }

        Point getCoordinates() {
            return new Point(xPos, lineIndex);
        }

        private Rect getRectFromJsonArray(JSONObject rectData) throws JSONException {
            // default value 0 for x
            int x = 0;
            if (rectData.has("x"))
                x = rectData.getInt("x");

            // default value 1 for height
            int height = 0;
            if (rectData.has("height"))
                height = rectData.getInt("height");

            return new Rect(
                    x, rectData.getInt("y"),
                    x + rectData.getInt("width"),
                    rectData.getInt("y") + height
            );
        }

        private JSONObject withColorAsJson() throws JSONException {
            JSONObject representation = new JSONObject();
            representation.put("id", id);
            representation.put("clr", color);
            return representation;
        }
    }

    /**
     * WordClock words can be one of the following types
     */
    @SuppressWarnings("unused")
    private enum WordCategory {
        HOUR,
        OTHER,
        MINUTE_BIG,
        MINUTE_SMALL_POINT,
        MINUTE_SMALL_BAR
    }
}

