package de.oerntec.matledcontrol.script_clients.wordclock;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Random;

import android.annotation.SuppressLint;
import android.content.Context;
import android.os.SystemClock;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Rect;

import org.json.JSONObject;

public class DrawingView extends View {
    private final String TAG = "drawingView";
    ArrayList<String[]> lines;
    //..
    private final int NUMBER_OF_WORDS = 25;
    private final int NUMBER_OF_LINES = 10;

    //detect long press
    private long startTime = 0;

    //are we changing values
    public boolean changingColors = true;

    private UpdateRequiredListener mUpdateListener;

    //draw: wordclockwords
    private int textSize = 2, width;
    Rect wordRects[] = new Rect[NUMBER_OF_WORDS];
    boolean drawRect[] = new boolean[NUMBER_OF_WORDS];
    int wordColors[] = new int[NUMBER_OF_WORDS];
    int wordWidth[] = new int[NUMBER_OF_WORDS];
    int firstWordHeight[] = new int[NUMBER_OF_LINES];
    int lineWidth[] = new int[NUMBER_OF_LINES];
    boolean textSizeFinal;

    //canvas n shit
    private Paint canvasPaint, textPaint, rectPaint;
    private int paintColor = 0xFFFF0000;
    private Canvas drawCanvas;
    private Bitmap canvasBitmap;

    public DrawingView(Context context, AttributeSet attrs) {
        super(context, attrs);
        //init words
        //SGD = new ScaleGestureDetector(this,new ScaleListener());
        lines = new ArrayList<String[]>();
        String[] line1 = {"HALF", "TWENTY"};
        String[] line2 = {"QUARTER", "FIVE"};
        String[] line3 = {"TEN", "MINUTES"};
        String[] line4 = {"TO", "PAST", "THREE"};
        String[] line5 = {"ONE", "TWO", "FOUR"};
        String[] line6 = {"TWELVE", "EIGHT"};
        String[] line7 = {"ELEVEN", "NINE"};
        String[] line8 = {"TEN", "SEVEN", "SIX"};
        String[] line9 = {"FIVE", "O'CLOCK"};
        String[] line10 = {".", ".", ".", "."};
        lines.add(line1);
        lines.add(line2);
        lines.add(line3);
        lines.add(line4);
        lines.add(line5);
        lines.add(line6);
        lines.add(line7);
        lines.add(line8);
        lines.add(line9);
        lines.add(line10);

        //get drawing area setup for interaction
        textPaint = new Paint();
        rectPaint = new Paint();
        //set initial color
        Arrays.fill(wordColors, paintColor);
        rectPaint.setColor(paintColor);
        rectPaint.setStyle(Paint.Style.STROKE);
        rectPaint.setStrokeWidth(3);
        canvasPaint = new Paint(Paint.DITHER_FLAG);
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

    void setChangeListener(UpdateRequiredListener updateRequiredListener){
        mUpdateListener = updateRequiredListener;
    }

    public void invertZero() {
        Boolean allOff = false;
        for (int i = 0; i < NUMBER_OF_WORDS; i++)
            if (drawRect[i])
                allOff = true;
        if (allOff)
            for (int i = 0; i < NUMBER_OF_WORDS; i++)
                drawRect[i] = false;
        else
            for (int i = 0; i < NUMBER_OF_WORDS; i++)
                drawRect[i] = true;
        redraw();
    }

    public void randomise() {
        Random rnd = new Random();
        for (int i = 0; i < NUMBER_OF_WORDS; i++) {
            if (drawRect[i])
                wordColors[i] = Color.argb(255, rnd.nextInt(256), rnd.nextInt(256), rnd.nextInt(256));
        }
        redraw();
    }

    public void setColors(int[] tempColors) {
        wordColors = tempColors;
    }

    @SuppressLint("ClickableViewAccessibility")
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        // Log.i("touchcoor", "X: "+touchX+" Y: "+touchY);
        // decide how to handle click
        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                startTime = SystemClock.elapsedRealtime() + 600;
                changingColors = true;
                //Log.i("touchcoor", "word: down");
                break;
            case MotionEvent.ACTION_CANCEL:
            case MotionEvent.ACTION_UP:
                changingColors = false;
                //Log.i("touchcoor", "word: up/cancel");
                if (SystemClock.elapsedRealtime() < startTime)
                    onClick(event.getX(), event.getY());
                else
                    onLongClick(event.getX(), event.getY());
                break;
            default:
                return false;
        }
        return true;
    }

    /**
     * Update the color for all selected words
     * @param color integer color representation
     */
    public void setColor(int color) {
        //Log.d(TAG, "setColor");
        for (int i = 0; i < NUMBER_OF_WORDS; i++)
            //if rect is marked, set the color to new value
            if (drawRect[i])
                wordColors[i] = color;
        redraw();
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
                if (drawRect[wordCount])
                    drawCanvas.drawRect(rectText, rectPaint);
                wordRects[wordCount] = rectText;
                wordCount++;
            }
            yCounter++;
        }
        //reeeedraw
        invalidate();
        //Log.i(TAG, ""+(System.currentTimeMillis()-benchmarkTest));
    }

    @Override
    protected void onDraw(Canvas canvas) {
        canvas.drawBitmap(canvasBitmap, 0, 0, canvasPaint);
    }

    public float getTextHeight() {
        int yOffset = 0;
        for (int iterator = 0; iterator < 10; iterator++) {
            yOffset += firstWordHeight[iterator] + 1;
        }
        return (float) yOffset;
    }

    public void onClick(float xPos, float yPos) {
        for (int counter = 0; counter < NUMBER_OF_WORDS; counter++) {
            if (wordRects[counter].contains((int) xPos, (int) yPos)) {
                //Log.d(TAG, "short: rect: "+counter);
                drawRect[counter] = !drawRect[counter];
                redraw();
                //break loop
                return;
            }
        }
    }

    public void onLongClick(float xPos, float yPos) {
        for (int counter = 0; counter < NUMBER_OF_WORDS; counter++) {
            if (wordRects[counter].contains((int) xPos, (int) yPos)) {
                //Log.d(TAG, "long: rect: "+counter);
                setColor(wordColors[counter]);
                redraw();
                //break loop
                return;
            }
        }
    }

    JSONObject getAsJsonObject(){
        return null;
    }

    public int[] getWordColors() {
        return wordColors;
    }

    public void increaseText() {
        textSize += 2;
        redraw();
    }

    public void setTextSize(int textS) {
        textSize = textS;
    }

    public int getTextSize() {
        return textSize;
    }

    public void decreaseText() {
        textSize -= 2;
        redraw();
    }

    interface UpdateRequiredListener {
        void onWordChanged();
    }
}

