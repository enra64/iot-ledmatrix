package de.oerntec.matledcontrol.script_clients.wordclock;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Point;
import android.graphics.Rect;
import android.support.annotation.ColorInt;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;

import org.json.JSONObject;

import java.util.ArrayList;

public class DrawingView extends View implements LocationClickHandler.CombinedOnClickListener {
    private final LocationClickHandler mClickHandler;
    private UpdateRequiredListener mUpdateListener;

    //draw: wordclockwords
    private int mViewWidth;

    ArrayList<String[]> mLines = new ArrayList<>();
    ArrayList<ArrayList<Rect>> mWordBoundingRectangles;
    ArrayList<ArrayList<Integer>> mWordColors;

    ArrayList<Float> lineWidths;
    private static final float TEST_TEXT_SIZE = 24f;

    //canvas n shit
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

        mClickHandler = new LocationClickHandler(this);
    }


    @Override
    protected void onSizeChanged(int width, int height, int oldWidth, int oldHeight) {
        super.onSizeChanged(width, height, oldWidth, oldHeight);
        this.mViewWidth = width;
        canvasBitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
        drawCanvas = new Canvas(canvasBitmap);

        ArrayList<String[]> lines = new ArrayList<>();
        String[] line1 = {"HALF","TWENTY"};
        String[] line2 = {"QUARTER","FIVE"};
        String[] line3 = {"TEN","MINUTES"};
        String[] line4 = {"TO","PAST", "THREE"};
        String[] line5 = {"ONE","TWO", "FOUR"};
        String[] line6 = {"TWELVE","EIGHT"};
        String[] line7 = {"ELEVEN","NINE"};
        String[] line8 = {"TEN","SEVEN", "SIX"};
        String[] line9 = {"FIVE","O'CLOCK"};
        String[] line10 = {".",".",".","."};
        lines.add(line1);lines.add(line2);lines.add(line3);lines.add(line4);
        lines.add(line5);lines.add(line6);lines.add(line7);lines.add(line8);
        lines.add(line9);lines.add(line10);
        //setLines(mLines);
        setLines(lines);
    }

    private void updateFontSize(ArrayList<String[]> lines, ArrayList<String> concatenatedLines, String longestLine) {
        // set the font size so the widest line will fit
        textPaint.setTextSize(TEST_TEXT_SIZE);
        textPaint.setTextSize(TEST_TEXT_SIZE * mViewWidth / textPaint.measureText(longestLine));

        // store the new width for each line
        lineWidths = new ArrayList<>();
        for(String line : concatenatedLines)
            lineWidths.add(textPaint.measureText(line));

        // store bounding rectangle for each word
        mWordBoundingRectangles = new ArrayList<>();
        int yOffset = 0;
        for (String[] line : lines) {
            ArrayList<Rect> lineBoundingRectangles = new ArrayList<>();
            int xOffset = 0;
            for(String word : line) {
                Rect boundingRect = new Rect();
                textPaint.getTextBounds(word, 0, word.length(), boundingRect);
                boundingRect.offset(xOffset, yOffset);
                lineBoundingRectangles.add(boundingRect);
                xOffset += boundingRect.width();
            }
            yOffset += lineBoundingRectangles.get(0).height();
            mWordBoundingRectangles.add(lineBoundingRectangles);
        }
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        return mClickHandler.onTouchEvent(event);
    }

    void setLines(ArrayList<String[]> lines) {
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

    void setChangeListener(UpdateRequiredListener updateRequiredListener) {
        mUpdateListener = updateRequiredListener;
    }

    /**
     * Update the color that will be applied to newly clicked words
     *
     * @param color integer color representation
     */
    public void setColor(@ColorInt int color) {
        mCurrentColor = color;
    }

    private void redraw() {
        // blank screen
        drawCanvas.drawColor(Color.WHITE);

        float yOffset = 0;
        for (int lineIndex = 0; lineIndex < mLines.size(); lineIndex++) {
            float xOffset = (mViewWidth - lineWidths.get(lineIndex)) / 2;
            String[] line = mLines.get(lineIndex);

            for (int wordIndex = 0; wordIndex < line.length; wordIndex++) {
                // apply word color
                textPaint.setColor(mWordColors.get(lineIndex).get(wordIndex));

                // draw text
                drawCanvas.drawText(line[wordIndex], xOffset, yOffset, textPaint);

                // move next word behind this one
                xOffset += mWordBoundingRectangles.get(lineIndex).get(wordIndex).width();
            }

            yOffset += mWordBoundingRectangles.get(lineIndex).get(0).height();
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
        return null;
    }

    private Point getWord(int x, int y){
        for(int lineIndex = 0; lineIndex < mLines.size(); lineIndex++) {
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
        if (wordCoordinates != null){
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

