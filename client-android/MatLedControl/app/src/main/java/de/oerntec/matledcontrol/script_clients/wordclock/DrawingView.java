package de.oerntec.matledcontrol.script_clients.wordclock;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Rect;
import android.support.annotation.ColorInt;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Arrays;

public class DrawingView extends View implements LocationClickHandler.CombinedOnClickListener {
    private final LocationClickHandler mClickHandler;
    ArrayList<String[]> lines = new ArrayList<>();

    private int NUMBER_OF_WORDS = 0;
    private int NUMBER_OF_LINES = 0;

    private UpdateRequiredListener mUpdateListener;

    //draw: wordclockwords
    private int textSize = 10, width;
    Rect wordRects[] = new Rect[NUMBER_OF_WORDS];
    int wordColors[] = new int[NUMBER_OF_WORDS];
    int firstWordHeight[] = new int[NUMBER_OF_LINES];
    int lineWidth[] = new int[NUMBER_OF_LINES];
    boolean textSizeFinal;

    //canvas n shit
    private Paint canvasPaint, textPaint, rectPaint;
    private Canvas drawCanvas;
    private Bitmap canvasBitmap;

    @ColorInt
    private int mCurrentColor;

    public DrawingView(Context context, AttributeSet attrs) {
        super(context, attrs);
        //get drawing area setup for interaction
        textPaint = new Paint();
        rectPaint = new Paint();
        //set initial color
        int paintColor = 0xFFFF0000;
        Arrays.fill(wordColors, paintColor);
        rectPaint.setColor(paintColor);
        rectPaint.setStyle(Paint.Style.STROKE);
        rectPaint.setStrokeWidth(3);
        canvasPaint = new Paint(Paint.DITHER_FLAG);

        mClickHandler = new LocationClickHandler(this);
    }



    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        //view given size
        width = w;
        super.onSizeChanged(w, h, oldw, oldh);
        canvasBitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
        drawCanvas = new Canvas(canvasBitmap);
        //Log.d(TAG, "w: "+w+", h: "+h);
        //create wordclockinterface
        int prevWidth = 18;
        while (lineWidth[3] < w) {
            prevWidth = textSize;
            textSize++;
            redraw();
        }
        textSize = prevWidth;
        redraw();
        textSizeFinal = true;
        redraw();
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        return mClickHandler.onTouchEvent(event);
    }

    void setLines(ArrayList<String[]> lines){
        this.lines = lines;
        NUMBER_OF_LINES = lines.size();

        int wordCount = 0;
        for(String[] line : lines)
            wordCount += line.length;
        NUMBER_OF_WORDS = wordCount;
    }

    void setChangeListener(UpdateRequiredListener updateRequiredListener){
        mUpdateListener = updateRequiredListener;
    }

    /**
     * Update the color that will be applied to newly clicked words
     * @param color integer color representation
     */
    public void setColor(@ColorInt int color) {
        mCurrentColor = color;
    }

    public void redraw() {
        textPaint.setTextSize(textSize);
        //blank screen
        drawCanvas.drawColor(Color.WHITE);

        int yCounter = 0, wordCount = 0;
        //y-axis throughput
        for (String[] stringArray : lines) {
            Rect rectText;
            float xOffset, yOffset;
            int yOffInt;
            if (!textSizeFinal)
                lineWidth[yCounter] = 0;
            //x-axis throughput
            for (int i = 0; i < stringArray.length; i++) {
                yOffset = 0;
                //center text
                xOffset = (width - lineWidth[yCounter]) / 2;
                rectText = new Rect();
                rectPaint.setColor(wordColors[wordCount]);
                textPaint.setColor(wordColors[wordCount]);
                textPaint.getTextBounds(stringArray[i], 0, stringArray[i].length(), rectText);
                //punkte: rechtecke vergrößern
                if (wordCount > NUMBER_OF_WORDS - 5)
                    rectText.inset(-30, -30);
                else
                    rectText.inset(-5, -5);
                wordRects[wordCount] = rectText;
                //erstes Wort? in firstword array eintragen
                if (i == 0)
                    firstWordHeight[yCounter] = rectText.height();
                //for automatic max size and centering
                if (!textSizeFinal)
                    lineWidth[yCounter] += rectText.width();
                //xOffset=alle bisherigen wörter der reihe
                for (int c = 1; c <= i; c++)
                    xOffset += wordRects[wordCount - c].width();
                //addiere die höhen der ersten boxen um den yOffset zu kriegen
                for (int iterator = 0; iterator <= yCounter; iterator++)
                    yOffset += firstWordHeight[iterator] + 1;
                //draw text
                if (wordCount > NUMBER_OF_WORDS - 5)//punkte
                    drawCanvas.drawText(stringArray[i], xOffset + 20, yOffset - 30, textPaint);
                else
                    drawCanvas.drawText(stringArray[i], xOffset, yOffset, textPaint);
                //retrieve, move, and overwrite the rectangle to the correct position
                yOffInt = (int) ((yOffset - rectText.height()) + 3);
                rectText.offsetTo((int) xOffset, yOffInt);
                wordRects[wordCount] = rectText;
                wordCount++;
            }
            yCounter++;
        }
        //reeeedraw
        invalidate();
        mUpdateListener.onWordChanged();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        canvas.drawBitmap(canvasBitmap, 0, 0, canvasPaint);
    }

    JSONObject getAsJsonObject(){
        return null;
    }

    @Override
    public void onClick(int x, int y) {
        for (int counter = 0; counter < NUMBER_OF_WORDS; counter++) {
            if (wordRects[counter].contains(x, y)) {
                //Log.d(TAG, "short: rect: "+counter);
                wordColors[counter] = mCurrentColor;
                redraw();
                //break loop
                return;
            }
        }
    }

    @Override
    public void onLongClick(int x, int y) {
        for (int counter = 0; counter < NUMBER_OF_WORDS; counter++) {
            if (wordRects[counter].contains(x, y)) {
                mUpdateListener.onColorCopied(wordColors[counter]);
                return;
            }
        }
    }

    interface UpdateRequiredListener {
        void onWordChanged();
        void onColorCopied(@ColorInt int color);
    }
}

