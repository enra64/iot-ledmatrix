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
import android.view.MotionEvent;
import android.view.View;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Random;

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

    void setLines(JsonObject lines) {
        mLineCount = lines.get("lines").getAsInt();

        JsonArray config = lines.get("config").getAsJsonArray();
        mWords = new HashMap<>(config.size());

        for (int i = 0; i < config.size(); i++) {
            Word newWord = new Word(i, config.get(i).getAsJsonObject());
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

    void randomizeColors() {
        Random rnd = new Random();
        List<Float> availableHues = new ArrayList<>(mWords.size());

        // generate n = mWords.size() evenly spaced hue values
        float stepSize = 360 / mWords.size();
        float offset = rnd.nextFloat() * stepSize;
        for (int i = 0; i < mWords.size(); i++)
            availableHues.add(stepSize * i + offset);

        // shuffle to avoid putting similar colors next to each other
        Collections.shuffle(availableHues);

        // random start offset to avoid always starting at blue
        int i = rnd.nextInt(mWords.size());
        for (Word word : mWords.values()) {
            // choose next hue value
            float hue = availableHues.get(i++ % mWords.size());

            // randomize value a little to further reduce similarity of output
            word.color = Color.HSVToColor(new float[]{hue, 1, 0.5f + rnd.nextFloat() * 0.5f});
        }

        redraw();
    }

    void setColors(JsonObject data) {
        JsonArray colorConfig = data.get("color_config").getAsJsonArray();

        for (int i = 0; i < colorConfig.size(); i++) {
            JsonObject colorInfo = colorConfig.get(i).getAsJsonObject();
            int wordId = colorInfo.get("id").getAsInt();
            int wordColor = colorInfo.get("clr").getAsInt();
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

    JsonObject getAsJsonObject() {
        JsonArray colorArray = new JsonArray();
        JsonObject responseWrapper = new JsonObject();

        for (Word word : mWords.values())
            colorArray.add(word.withColorAsJson());
        responseWrapper.add("word_color_config", colorArray);
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

        Word(int id, JsonObject data) {
            this.id = id;
            displayString = data.get("word").getAsString();
            ledRectangle = getRectFromJsonArray(data.get("rect").getAsJsonObject());

            if (data.has("pos")) {
                xPos = data.get("pos").getAsJsonArray().get(0).getAsInt();
                lineIndex = data.get("pos").getAsJsonArray().get(1).getAsInt();
            } else {
                xPos = ledRectangle.left;
                lineIndex = ledRectangle.top;
            }



            category = WordCategory.valueOf(data.get("category").getAsString());
            Object info = data.get("info");
            this.info = String.valueOf(info);
        }

        Point getCoordinates() {
            return new Point(xPos, lineIndex);
        }

        private Rect getRectFromJsonArray(JsonObject rectData) {
            // default value 0 for x
            int x = 0;
            if (rectData.has("x"))
                x = rectData.get("x").getAsInt();

            // default value 1 for height
            int height = 0;
            if (rectData.has("height"))
                height = rectData.get("height").getAsInt();

            return new Rect(
                    x, rectData.get("y").getAsInt(),
                    x + rectData.get("width").getAsInt(),
                    rectData.get("y").getAsInt() + height
            );
        }

        private JsonObject withColorAsJson() {
            JsonObject representation = new JsonObject();
            representation.addProperty("id", id);
            representation.addProperty("clr", color);
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

